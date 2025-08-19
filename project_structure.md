business-intelligence-scraper/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── constants.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── discovery/
│   │   ├── __init__.py
│   │   ├── search_engine.py
│   │   ├── business_finder.py
│   │   └── filters.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── google_business.py
│   │   ├── social_media/
│   │   │   ├── __init__.py
│   │   │   ├── linkedin.py
│   │   │   ├── facebook.py
│   │   │   ├── instagram.py
│   │   │   └── twitter.py
│   │   ├── directories/
│   │   │   ├── __init__.py
│   │   │   ├── yelp.py
│   │   │   ├── yellow_pages.py
│   │   │   ├── better_business_bureau.py
│   │   │   └── industry_specific.py
│   │   └── news/
│   │       ├── __init__.py
│   │       └── news_scraper.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── contact_extractor.py
│   │   ├── email_finder.py
│   │   ├── phone_extractor.py
│   │   └── employee_finder.py
│   ├── profiles/
│   │   ├── __init__.py
│   │   ├── business_profile.py
│   │   ├── profile_builder.py
│   │   └── profile_enricher.py
│   ├── export/
│   │   ├── __init__.py
│   │   ├── export_manager.py
│   │   ├── folder_structure.py
│   │   └── formatters.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── connection.py
│   │   └── migrations/
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       ├── rate_limiter.py
│       ├── proxy_manager.py
│       └── logger.py
├── tests/
│   └── ...
└── exports/
    └── [generated business folders]