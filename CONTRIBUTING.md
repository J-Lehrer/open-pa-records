# Contributing

Thanks for your interest in the PA County Records Access Audit!

## How to Help

### 1. Verify County Data
Pick a county from `data/counties.csv` (especially those with `status: needs_review`) and manually confirm the information by visiting the county's Recorder of Deeds website. Submit a PR with corrections.

### 2. Research Missing Counties
Check `data/counties.csv` for counties with `status: unresearched`. Visit the county website, classify their access, and submit a PR.

### 3. Report Issues
If you find incorrect data, open an issue with:
- County name
- What's wrong
- Correct information with source URL

### 4. Extend the Dataset
Ideas for additional data points:
- Exact fee schedules with screenshots
- Whether the county has a GIS/mapping integration
- API availability for bulk data access
- Historical record coverage gaps

## Data Standards

### Access Tier Definitions
Be precise with tier classification:

| Tier | Criteria |
|------|----------|
| `free` | Search + view + download, no payment of any kind |
| `partial` | Some free access but fees for full functionality |
| `paywalled` | Payment required to search OR view records |
| `none` | No online access whatsoever |

### Key Judgment Calls
- **Free account required** → `partial` (still a barrier, even if no money)
- **Free search but paid viewing** → `paywalled` (can't see the actual documents)
- **Watermarked viewing free, downloads paid** → `partial` (you can see the content)
- **LANDEX free index + paid images** → `paywalled` (index without images is not meaningful access)

### Source Requirements
Every `verified` entry must have a `source_url` pointing to where you confirmed the access information. Prefer official county or vendor URLs.

## Running Validation

```bash
python scripts/validate.py
```

This checks for schema compliance, missing fields, invalid enums, and logical consistency. All PRs should pass validation.

## Code of Conduct

Be respectful. This project exists to improve public access to public records. We welcome contributions from journalists, housing advocates, researchers, developers, and concerned citizens.
