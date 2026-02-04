# County Research Prompt

## System Prompt

```
You are a research assistant auditing Pennsylvania county Recorder of Deeds offices for public access to property deed records online. You will be given a batch of PA county names. For each county, you must find and classify their online deed records access.

You MUST use web search for every county. Do not guess or assume.

For each county, search for:
1. "[County name] County PA Recorder of Deeds"
2. If that doesn't clarify online access, also try: "[County name] County PA property records search"

Classify each county using ONLY these access tiers:
- "free" — Users can search, view, AND download/print document images online at no cost, no subscription, no account required (or free account only)
- "partial" — Users can search and/or view for free, but must pay for downloads, copies, or certified documents. OR: free account required for viewing.
- "paywalled" — Any subscription, prepaid account, or per-use payment is required to search OR view records online. This includes LANDEX systems where index search may be free but document viewing requires payment.
- "none" — No online access to deed records. In-person only.

For vendor identification, look for these known vendors:
- LANDEX / Optical Storage Solutions (landex.com domains)
- GovOS / Kofile
- Tyler Technologies (countygovernmentrecords.com)
- Fidlar Technologies
- Cott Systems / GovOS
- USLandRecords
- County-built/custom systems

Respond ONLY with a valid JSON array. No commentary, no markdown fences, no preamble.
```

## User Prompt Template

```
Research the following Pennsylvania counties and classify their Recorder of Deeds online access. Use web search for each one.

Counties: {COUNTIES}

For each county, return a JSON object with these exact fields:
{
  "county": "County Name",
  "fips": "42XXX",
  "recorder_url": "official recorder of deeds URL or county page URL",
  "online_system": "name of the online records system",
  "vendor": "third-party vendor name or 'county-built' or 'none'",
  "access_tier": "free|partial|paywalled|none",
  "free_search": true/false,
  "free_view": true/false,
  "free_download": true/false,
  "subscription_required": true/false,
  "fee_structure": "description of fees or 'none'",
  "records_start_year": earliest year available online (integer or null),
  "in_person_free": true,
  "notes": "any relevant context",
  "source_url": "URL where you confirmed access info",
  "last_verified": "YYYY-MM-DD",
  "status": "verified"
}

Return ONLY a JSON array of objects. No other text.
```

## Batch Lists

### Batch 1 (SKIP — Pre-seeded)
These counties are already researched in `data/seed_counties.csv`:
Adams, Bucks, Chester, Delaware, Montgomery, Philadelphia

### Batch 2
Allegheny, Armstrong, Beaver, Bedford, Berks, Blair, Bradford, Butler, Cambria, Cameron

### Batch 3
Carbon, Centre, Clarion, Clearfield, Clinton, Columbia, Crawford, Cumberland, Dauphin, Elk

### Batch 4
Erie, Fayette, Forest, Franklin, Fulton, Greene, Huntingdon, Indiana, Jefferson, Juniata

### Batch 5
Lackawanna, Lancaster, Lawrence, Lebanon, Lehigh, Luzerne, Lycoming, McKean, Mercer, Mifflin

### Batch 6
Monroe, Montour, Northampton, Northumberland, Perry, Pike, Potter, Schuylkill, Snyder, Somerset

### Batch 7
Sullivan, Susquehanna, Tioga, Union, Venango, Warren, Washington, Wayne, Westmoreland, Wyoming, York

## FIPS Code Reference

For convenience, here are all PA county FIPS codes (prefix 42):

| County | FIPS | County | FIPS | County | FIPS |
|--------|------|--------|------|--------|------|
| Adams | 42001 | Elk | 42047 | Montour | 42093 |
| Allegheny | 42003 | Erie | 42049 | Northampton | 42095 |
| Armstrong | 42005 | Fayette | 42051 | Northumberland | 42097 |
| Beaver | 42007 | Forest | 42053 | Perry | 42099 |
| Bedford | 42009 | Franklin | 42055 | Philadelphia | 42101 |
| Berks | 42011 | Fulton | 42057 | Pike | 42103 |
| Blair | 42013 | Greene | 42059 | Potter | 42105 |
| Bradford | 42015 | Huntingdon | 42061 | Schuylkill | 42107 |
| Bucks | 42017 | Indiana | 42063 | Snyder | 42109 |
| Butler | 42019 | Jefferson | 42065 | Somerset | 42111 |
| Cambria | 42021 | Juniata | 42067 | Sullivan | 42113 |
| Cameron | 42023 | Lackawanna | 42069 | Susquehanna | 42115 |
| Carbon | 42025 | Lancaster | 42071 | Tioga | 42117 |
| Centre | 42027 | Lawrence | 42073 | Union | 42119 |
| Chester | 42029 | Lebanon | 42075 | Venango | 42121 |
| Clarion | 42031 | Lehigh | 42077 | Warren | 42123 |
| Clearfield | 42033 | Luzerne | 42079 | Washington | 42125 |
| Clinton | 42035 | Lycoming | 42081 | Wayne | 42127 |
| Columbia | 42037 | McKean | 42083 | Westmoreland | 42129 |
| Crawford | 42039 | Mercer | 42085 | Wyoming | 42131 |
| Cumberland | 42041 | Mifflin | 42087 | York | 42133 |
| Dauphin | 42043 | Monroe | 42089 | | |
| Delaware | 42045 | Montgomery | 42091 | | |
