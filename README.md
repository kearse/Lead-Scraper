# Business Intelligence Lead Scraper (Initial Framework)

## Overview
This project lays the groundwork for a multi-source business intelligence & lead discovery system. It:
- Discovers businesses (placeholder data sources for now)
- Builds enriched business profiles
- Extracts contacts & identifies potential decision makers
- Exports results to a structured folder hierarchy (JSON, CSV, text summaries)
- Uses an asynchronous orchestration pipeline

## Status
Current release is a structural & architectural scaffold with **mock data**. Future PRs will integrate real APIs & scraping logic.

## Features (Current)
- Async discovery pipeline
- Modular architecture (discovery, scrapers, profiles, extractors, export)
- Contact extraction & decision maker scoring (stub)
- Confidence scoring heuristic
- Hierarchical export (master summary + per-business folders)
- Pluggable design for future data sources

## Planned (Future PRs)
- Google Places, Yelp Fusion, LinkedIn, News APIs
- Proxy rotation & CAPTCHA strategy
- Database persistence (SQLAlchemy + PostgreSQL)
- Rate limiting & robots.txt compliance enforcement
- Email pattern inference & verification

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt

python src/main.py --industry "restaurants" --location "New York, NY" --limit 5
```

Inspect output in `exports/`.

## Export Structure (Example)

```
exports/
└── restaurants_New_York,_NY_20240101_120000/
    ├── master_summary.json
    ├── master_summary.csv
    ├── statistics.json
    └── Sample_Google_Maps_Biz/
        ├── profile.json
        ├── summary.txt
        ├── google_business/
        │   └── google_business_profile.json
        ├── social_media/
        │   ├── linkedin_profile.json
        │   └── facebook_profile.json
        └── contacts/
            ├── all_contacts.json
            ├── all_contacts.csv
            ├── decision_makers.json
            └── decision_makers.csv
```

## Configuration
Copy `.env.example` to `.env` and add API keys as integrations are added.

## Architecture

| Layer | Responsibility |
|-------|----------------|
| discovery | Aggregate candidate businesses |
| scrapers | Source-specific data retrieval (stubs now) |
| profiles | Orchestrate enrichment & consolidation |
| extractors | Contact/person parsing & scoring |
| export | Structured output generation |
| utils | Logging, (future) rate limiting, helpers |

## Ethical & Legal Use
This framework must be used in compliance with:
- Site Terms of Service
- robots.txt directives
- Applicable privacy & data laws (GDPR, CCPA)
- Fair use & rate limiting guidelines

Do NOT scrape authenticated or restricted content without permission.

## Contributing
Planned workflow: small, focused PRs replacing stubs with real integrations. Please coordinate on:
- Data model changes
- Adding dependencies
- External service integrations

## License
MIT (proposed) — add LICENSE file if acceptable.
