# 🏛️ PA County Records Access Audit

**How accessible are property deed records across Pennsylvania's 67 counties?**

Pennsylvania law (Right-to-Know Law, Act 3 of 2008) mandates that property deed records be freely inspectable — yet many counties place them behind third-party vendor paywalls. This project audits every PA county's Recorder of Deeds for online accessibility, vendor usage, and fee structures.

## Why This Matters

- **25% of Philadelphia home purchases (2017–2022)** were made by corporations ([Reinvestment Fund/Rutgers, 2025](https://www.reinvestment.com/insights/corporate-investors-in-single-family-homes-in-philadelphia/))
- **85% of corporate acquisitions** targeted low/moderate-income neighborhoods ([Federal Reserve Bank of Philadelphia, 2025](https://www.philadelphiafed.org/community-development/housing-and-neighborhoods/ownership-profile-of-single-family-residence-properties-in-philadelphia-large-corporate-investors))
- Anonymous LLC ownership obscures who is buying residential properties
- Paywall systems may violate PA's own fee statutes (Section 1307(e) requires OOR pre-approval)

**Without transparent deed records, communities cannot track institutional acquisition of their housing.**

## Data

The primary dataset is [`data/counties.csv`](data/counties.csv) with the following schema:

| Field | Type | Description |
|-------|------|-------------|
| `county` | string | County name |
| `fips` | string | 5-digit FIPS code (42XXX) |
| `recorder_url` | string | Official Recorder of Deeds URL |
| `online_system` | string | Name of online records system |
| `vendor` | string | Third-party vendor if applicable |
| `access_tier` | enum | `free`, `partial`, `paywalled`, `none` |
| `free_search` | boolean | Can you search the index for free online? |
| `free_view` | boolean | Can you view document images for free online? |
| `free_download` | boolean | Can you download/print documents for free? |
| `subscription_required` | boolean | Is a paid subscription needed for any access? |
| `fee_structure` | string | Description of fees if applicable |
| `records_start_year` | integer | Earliest year of online records |
| `in_person_free` | boolean | Free inspection available in-person? |
| `notes` | string | Additional context |
| `source_url` | string | URL where access info was confirmed |
| `last_verified` | date | Date this entry was last verified |
| `status` | enum | `verified`, `needs_review`, `unresearched` |

### Access Tier Definitions

- **`free`** — Full online search, view, and download at no cost (e.g., Delaware County's GovOS)
- **`partial`** — Free search and/or view, but fees for downloads/copies (e.g., Montgomery County)
- **`paywalled`** — Subscription or payment required to search or view (e.g., Bucks County LANDEX)
- **`none`** — No online access; in-person only

## Key Findings (In Progress)

| Access Tier | Count | Percentage |
|-------------|-------|------------|
| Free | TBD | TBD |
| Partial | TBD | TBD |
| Paywalled | TBD | TBD |
| None | TBD | TBD |

### Known Vendor Distribution

- **LANDEX** (Optical Storage Solutions, Doylestown PA): 12+ counties
- **GovOS / Kofile**: Delaware County (free model)
- **Tyler Technologies**: Chester County
- **PhilaDox** (city-operated): Philadelphia
- **County-built systems**: Montgomery County, others

## Methodology

Research is conducted using structured prompts executed by Claude Haiku for token efficiency. See [`prompts/`](prompts/) for the instruction templates. Each county is independently researched and classified, then human-verified.

### Workflow

1. **Batch research** — Run Haiku prompts against batches of ~10 counties
2. **Parse output** — Extract structured data from Haiku responses
3. **Validate** — Run `scripts/validate.py` to check for schema compliance
4. **Human review** — Spot-check classifications, especially edge cases
5. **Compile** — Merge into master `counties.csv`

## Legal Context

- **PA Right-to-Know Law (Act 3 of 2008)** — Records must be available for free inspection
- **Section 1307(g)** — No fee may be charged for searching or retrieval
- **Section 1307(e)** — "Enhanced electronic access" fees allowed only if pre-approved by OOR and not exclusionary
- **42 P.S. § 21051** — Copy fees capped at $0.50/page (uncertified), $1.50/page (certified)

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md). PRs welcome, especially for:
- Verifying/correcting county data
- Adding missing counties
- Improving the research prompts
- Visualization

## Roadmap

- [ ] Phase 1: Audit all 67 counties (this repo)
- [ ] Phase 2: Corporate vs. individual ownership analysis (downstream project)
- [ ] Phase 3: Interactive map / dashboard
- [ ] Phase 4: RTK request templates for challenging non-compliant counties

## License

MIT

## Acknowledgments

Research informed by the PA Office of Open Records, Reinvestment Fund, Federal Reserve Bank of Philadelphia, Reporters Committee for Freedom of the Press, and WHYY reporting on Delaware County's records modernization.
