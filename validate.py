"""
PA County Records Audit — Data Validator
=========================================
Validates counties.csv for schema compliance, completeness, and consistency.

Usage:
    python validate.py                     # Validate data/counties.csv
    python validate.py path/to/file.csv    # Validate specific file
"""

import csv
import sys
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"
TOTAL_PA_COUNTIES = 67

VALID_TIERS = {"free", "partial", "paywalled", "none"}
VALID_STATUSES = {"verified", "needs_review", "unresearched"}
VALID_BOOLEANS = {"true", "false", "True", "False", ""}

REQUIRED_FIELDS = [
    "county", "fips", "access_tier", "status"
]

ALL_FIELDS = [
    "county", "fips", "recorder_url", "online_system", "vendor",
    "access_tier", "free_search", "free_view", "free_download",
    "subscription_required", "fee_structure", "records_start_year",
    "in_person_free", "notes", "source_url", "last_verified", "status"
]

# All 67 PA county names
ALL_COUNTIES = {
    "Adams", "Allegheny", "Armstrong", "Beaver", "Bedford", "Berks", "Blair",
    "Bradford", "Bucks", "Butler", "Cambria", "Cameron", "Carbon", "Centre",
    "Chester", "Clarion", "Clearfield", "Clinton", "Columbia", "Crawford",
    "Cumberland", "Dauphin", "Delaware", "Elk", "Erie", "Fayette", "Forest",
    "Franklin", "Fulton", "Greene", "Huntingdon", "Indiana", "Jefferson",
    "Juniata", "Lackawanna", "Lancaster", "Lawrence", "Lebanon", "Lehigh",
    "Luzerne", "Lycoming", "McKean", "Mercer", "Mifflin", "Monroe", "Montgomery",
    "Montour", "Northampton", "Northumberland", "Perry", "Philadelphia", "Pike",
    "Potter", "Schuylkill", "Snyder", "Somerset", "Sullivan", "Susquehanna",
    "Tioga", "Union", "Venango", "Warren", "Washington", "Wayne", "Westmoreland",
    "Wyoming", "York"
}


def validate(filepath: Path) -> tuple[list, list]:
    """Validate CSV file. Returns (errors, warnings)."""
    errors = []
    warnings = []

    if not filepath.exists():
        errors.append(f"File not found: {filepath}")
        return errors, warnings

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Check header
    missing_fields = set(ALL_FIELDS) - set(reader.fieldnames or [])
    if missing_fields:
        errors.append(f"Missing columns: {missing_fields}")

    # Track counties found
    counties_found = set()
    tier_counts = Counter()
    status_counts = Counter()

    for i, row in enumerate(rows, start=2):  # CSV line numbers (1-indexed + header)
        county = row.get("county", "").strip()

        # Required fields
        for field in REQUIRED_FIELDS:
            if not row.get(field, "").strip():
                errors.append(f"Row {i} ({county}): Missing required field '{field}'")

        # County name validation
        if county and county not in ALL_COUNTIES:
            warnings.append(f"Row {i}: Unknown county name '{county}'")

        if county in counties_found:
            errors.append(f"Row {i}: Duplicate county '{county}'")
        counties_found.add(county)

        # FIPS validation
        fips = row.get("fips", "").strip()
        if fips and (not fips.startswith("42") or len(fips) != 5):
            errors.append(f"Row {i} ({county}): Invalid FIPS '{fips}' (should be 42XXX)")

        # Enum validation
        tier = row.get("access_tier", "").strip()
        if tier and tier not in VALID_TIERS:
            errors.append(f"Row {i} ({county}): Invalid access_tier '{tier}'")
        tier_counts[tier] += 1

        status = row.get("status", "").strip()
        if status and status not in VALID_STATUSES:
            errors.append(f"Row {i} ({county}): Invalid status '{status}'")
        status_counts[status] += 1

        # Boolean validation
        for bool_field in ["free_search", "free_view", "free_download", "subscription_required", "in_person_free"]:
            val = row.get(bool_field, "").strip().lower()
            if val and val not in {"true", "false"}:
                warnings.append(f"Row {i} ({county}): '{bool_field}' = '{val}' (expected true/false)")

        # Consistency checks
        if tier == "free" and row.get("subscription_required", "").strip().lower() == "true":
            warnings.append(f"Row {i} ({county}): access_tier='free' but subscription_required=true")

        if tier == "paywalled" and row.get("free_view", "").strip().lower() == "true":
            warnings.append(f"Row {i} ({county}): access_tier='paywalled' but free_view=true")

        # Verified entries should have source_url
        if status == "verified" and not row.get("source_url", "").strip():
            warnings.append(f"Row {i} ({county}): status='verified' but no source_url")

    # Completeness
    missing_counties = ALL_COUNTIES - counties_found
    if missing_counties:
        warnings.append(f"Missing {len(missing_counties)} counties: {sorted(missing_counties)}")

    return errors, warnings, rows, tier_counts, status_counts


def main():
    filepath = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_DIR / "counties.csv"

    # Fall back to seed file
    if not filepath.exists():
        filepath = DATA_DIR / "seed_counties.csv"

    print(f"Validating: {filepath}\n")

    errors, warnings, rows, tier_counts, status_counts = validate(filepath)

    # Summary
    print(f"{'='*50}")
    print(f"  PA County Records Audit — Validation Report")
    print(f"{'='*50}")
    print(f"  Total rows:        {len(rows)}")
    print(f"  Target:            {TOTAL_PA_COUNTIES} counties")
    print(f"  Coverage:          {len(rows)}/{TOTAL_PA_COUNTIES} ({len(rows)/TOTAL_PA_COUNTIES*100:.0f}%)")
    print()
    print(f"  Access Tiers:")
    for tier in ["free", "partial", "paywalled", "none", ""]:
        count = tier_counts.get(tier, 0)
        label = tier if tier else "(blank)"
        if count:
            print(f"    {label:15s} {count:3d}  {'█' * count}")
    print()
    print(f"  Status:")
    for status in ["verified", "needs_review", "unresearched", ""]:
        count = status_counts.get(status, 0)
        label = status if status else "(blank)"
        if count:
            print(f"    {label:15s} {count:3d}  {'█' * count}")

    # Errors
    print()
    if errors:
        print(f"  ❌ {len(errors)} ERRORS:")
        for e in errors:
            print(f"     • {e}")
    else:
        print(f"  ✅ No errors!")

    if warnings:
        print(f"\n  ⚠️  {len(warnings)} WARNINGS:")
        for w in warnings:
            print(f"     • {w}")
    else:
        print(f"  ✅ No warnings!")

    print()
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
