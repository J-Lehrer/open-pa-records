"""
PA County Records Audit — Haiku Batch Runner
=============================================
Sends batched county research prompts to Claude Haiku via the Anthropic API.
Requires: pip install anthropic

Usage:
    python run_batch.py                    # Run all unresearched batches
    python run_batch.py --batch 2          # Run specific batch (2-7)
    python run_batch.py --verify           # Verify needs_review entries
    python run_batch.py --dry-run          # Print prompts without calling API

Set ANTHROPIC_API_KEY env var before running.
"""

import anthropic
import json
import csv
import os
import sys
import argparse
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL = "claude-haiku-4-5-20251001"
DATA_DIR = Path(__file__).parent / "data"
PROMPTS_DIR = Path(__file__).parent / "prompts"
SEED_FILE = Path(__file__).parent / "seed_counties.csv"
OUTPUT_FILE = DATA_DIR / "counties.csv"
RAW_DIR = DATA_DIR / "raw_responses"

# All 67 PA counties grouped into batches
BATCHES = {
    1: ["Adams", "Bucks", "Chester", "Delaware", "Montgomery", "Philadelphia"],  # pre-seeded
    2: ["Allegheny", "Armstrong", "Beaver", "Bedford", "Berks", "Blair", "Bradford", "Butler", "Cambria", "Cameron"],
    3: ["Carbon", "Centre", "Clarion", "Clearfield", "Clinton", "Columbia", "Crawford", "Cumberland", "Dauphin", "Elk"],
    4: ["Erie", "Fayette", "Forest", "Franklin", "Fulton", "Greene", "Huntingdon", "Indiana", "Jefferson", "Juniata"],
    5: ["Lackawanna", "Lancaster", "Lawrence", "Lebanon", "Lehigh", "Luzerne", "Lycoming", "McKean", "Mercer", "Mifflin"],
    6: ["Monroe", "Montour", "Northampton", "Northumberland", "Perry", "Pike", "Potter", "Schuylkill", "Snyder", "Somerset"],
    7: ["Sullivan", "Susquehanna", "Tioga", "Union", "Venango", "Warren", "Washington", "Wayne", "Westmoreland", "Wyoming", "York"],
}

SYSTEM_PROMPT = """You are a research assistant auditing Pennsylvania county Recorder of Deeds offices for public access to property deed records online. You will be given a batch of PA county names. For each county, you must find and classify their online deed records access.

You MUST use web search for every county. Do not guess or assume.

For each county, search for:
1. "[County name] County PA Recorder of Deeds"
2. If that doesn't clarify online access, also try: "[County name] County PA property records search"

Classify each county using ONLY these access tiers:
- "free" — Users can search, view, AND download/print document images online at no cost, no subscription, no account required (or free account only)
- "paywalled" — Any payment required to access full records. This includes: subscriptions, prepaid accounts, per-use fees, pay-to-download, pay-for-copies, or limited free views with paid full access. If only some data is free but full access requires payment, classify as paywalled.
- "none" — No online access to deed records. In-person only.

For vendor identification, look for these known vendors:
- LANDEX / Optical Storage Solutions (landex.com domains)
- GovOS / Kofile
- Tyler Technologies (countygovernmentrecords.com)
- Fidlar Technologies
- Cott Systems / GovOS
- USLandRecords
- County-built/custom systems

Respond ONLY with a valid JSON array. No commentary, no markdown fences, no preamble."""

USER_PROMPT_TEMPLATE = """Research the following Pennsylvania counties and classify their Recorder of Deeds online access. Use web search for each one.

Counties: {counties}

For each county, return a JSON object with these exact fields:
{{
  "county": "County Name",
  "fips": "42XXX",
  "recorder_url": "official recorder of deeds URL or county page URL",
  "online_system": "name of the online records system",
  "vendor": "third-party vendor name or 'county-built' or 'none'",
  "access_tier": "free|paywalled|none",
  "free_search": true/false,
  "free_view": true/false,
  "free_download": true/false,
  "subscription_required": true/false,
  "fee_structure": "description of fees or 'none'",
  "records_start_year": earliest year available online (integer or null),
  "in_person_free": true,
  "notes": "any relevant context",
  "source_url": "URL where you confirmed access info",
  "last_verified": "{today}",
  "status": "verified"
}}

Return ONLY a JSON array of objects. No other text."""

VERIFY_SYSTEM_PROMPT = """You are verifying Pennsylvania county Recorder of Deeds access data. You will be given existing data for a county. Use web search to confirm or correct each field.

If the data is correct, return it unchanged with "status": "verified".
If any field is wrong, correct it and add a "corrections" field listing what changed.

Respond ONLY with a valid JSON object. No commentary."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_seed_data() -> dict:
    """Load seed CSV into a dict keyed by county name."""
    data = {}
    if SEED_FILE.exists():
        with open(SEED_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row["county"]] = row
    return data


def get_seeded_counties(seed: dict, status_filter: str = None) -> set:
    """Get set of county names from seed data, optionally filtered by status."""
    if status_filter:
        return {name for name, row in seed.items() if row.get("status") == status_filter}
    return set(seed.keys())


def get_unresearched_for_batch(batch_num: int, seed: dict) -> list:
    """Get counties in a batch that haven't been fully researched."""
    verified = get_seeded_counties(seed, "verified")
    return [c for c in BATCHES[batch_num] if c not in verified]


def parse_response(text: str) -> list:
    """Parse JSON array from Haiku response, handling common issues."""
    text = text.strip()
    # Strip markdown fences if Haiku adds them despite instructions
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()
    return json.loads(text)


def save_raw_response(batch_num: int, response_text: str):
    """Save raw API response for debugging."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"batch_{batch_num}_{date.today().isoformat()}.json"
    with open(path, "w") as f:
        f.write(response_text)
    print(f"  Raw response saved: {path}")


def call_haiku(system: str, user: str, dry_run: bool = False) -> str:
    """Call Claude Haiku API."""
    if dry_run:
        print("\n--- DRY RUN: Would send this prompt ---")
        print(f"System: {system[:200]}...")
        print(f"User: {user[:500]}...")
        print("--- END DRY RUN ---\n")
        return "[]"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user}],
    )

    # Extract text from response content blocks
    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)
    return "\n".join(text_parts)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def run_batch(batch_num: int, seed: dict, dry_run: bool = False):
    """Research a single batch of counties."""
    counties = get_unresearched_for_batch(batch_num, seed)
    if not counties:
        print(f"Batch {batch_num}: All counties already verified. Skipping.")
        return []

    print(f"Batch {batch_num}: Researching {len(counties)} counties: {', '.join(counties)}")

    user_prompt = USER_PROMPT_TEMPLATE.format(
        counties=", ".join(counties),
        today=date.today().isoformat(),
    )

    response_text = call_haiku(SYSTEM_PROMPT, user_prompt, dry_run)
    save_raw_response(batch_num, response_text)

    if dry_run:
        return []

    try:
        results = parse_response(response_text)
        print(f"  Parsed {len(results)} county records.")
        return results
    except json.JSONDecodeError as e:
        print(f"  ERROR parsing batch {batch_num}: {e}")
        print(f"  Raw response saved for debugging.")
        return []


def run_verify(seed: dict, dry_run: bool = False):
    """Verify counties with needs_review status."""
    to_verify = {name: row for name, row in seed.items() if row.get("status") == "needs_review"}
    if not to_verify:
        print("No counties need verification.")
        return []

    print(f"Verifying {len(to_verify)} counties: {', '.join(to_verify.keys())}")

    results = []
    for name, row in to_verify.items():
        user_prompt = f"""Verify the following PA county Recorder of Deeds data using web search. Visit the recorder_url and source_url to confirm accuracy.

Current data:
{json.dumps(row, indent=2)}

Return the verified/corrected JSON object. If you made corrections, add a "corrections" field as an array of strings describing what changed."""

        response_text = call_haiku(VERIFY_SYSTEM_PROMPT, user_prompt, dry_run)
        save_raw_response(f"verify_{name}", response_text)

        if not dry_run:
            try:
                result = json.loads(response_text.strip().strip("`").strip())
                results.append(result)
                corrections = result.get("corrections", [])
                if corrections:
                    print(f"  {name}: CORRECTED — {corrections}")
                else:
                    print(f"  {name}: Confirmed ✓")
            except json.JSONDecodeError as e:
                print(f"  {name}: ERROR parsing — {e}")

    return results


def merge_results(seed: dict, new_results: list) -> list:
    """Merge new results into seed data."""
    for result in new_results:
        county_name = result.get("county", "")
        if county_name:
            seed[county_name] = result

    # Return as sorted list
    return [seed[k] for k in sorted(seed.keys())]


def write_csv(records: list, output_path: Path):
    """Write records to CSV."""
    if not records:
        print("No records to write.")
        return

    fieldnames = [
        "county", "fips", "recorder_url", "online_system", "vendor",
        "access_tier", "free_search", "free_view", "free_download",
        "subscription_required", "fee_structure", "records_start_year",
        "in_person_free", "notes", "source_url", "last_verified", "status"
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} records to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="PA County Records Audit — Haiku Batch Runner")
    parser.add_argument("--batch", type=int, help="Run a specific batch (2-7). Batch 1 is pre-seeded.")
    parser.add_argument("--verify", action="store_true", help="Verify needs_review entries.")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling API.")
    parser.add_argument("--all", action="store_true", help="Run all unresearched batches (2-7).")
    args = parser.parse_args()

    # Check API key
    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)

    seed = load_seed_data()
    print(f"Loaded {len(seed)} seeded counties.\n")

    all_new_results = []

    if args.verify:
        results = run_verify(seed, args.dry_run)
        all_new_results.extend(results)

    elif args.batch:
        if args.batch == 1:
            print("Batch 1 is pre-seeded. Use --verify to check existing data.")
            sys.exit(0)
        results = run_batch(args.batch, seed, args.dry_run)
        all_new_results.extend(results)

    elif args.all:
        for batch_num in range(2, 8):
            results = run_batch(batch_num, seed, args.dry_run)
            all_new_results.extend(results)
            print()

    else:
        parser.print_help()
        sys.exit(0)

    # Merge and save
    if all_new_results and not args.dry_run:
        merged = merge_results(seed, all_new_results)
        write_csv(merged, OUTPUT_FILE)
        print(f"\nDone! {len(all_new_results)} new/updated records.")
    elif args.dry_run:
        print("\nDry run complete. No API calls made.")


if __name__ == "__main__":
    main()
