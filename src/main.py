"""Lead Scraper main entry point."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from discovery.search_engine import SearchEngine
from profiles.profile_builder import ProfileBuilder
from extractors.contact_extractor import ContactExtractor
from export.export_manager import ExportManager
from utils.logger import setup_logger, logger

async def main():
    """Main pipeline orchestrator."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Lead Scraper - Business Intelligence & Contact Discovery")
    parser.add_argument("--industry", required=True, help="Target industry (e.g., 'restaurants', 'retail')")
    parser.add_argument("--location", required=True, help="Target location (e.g., 'New York, NY')")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of businesses to discover")
    parser.add_argument("--output", help="Output directory (defaults to exports/)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(level=args.log_level)
    
    logger.info("=" * 60)
    logger.info("Lead Scraper - Business Intelligence Pipeline")
    logger.info("=" * 60)
    logger.info(f"Industry: {args.industry}")
    logger.info(f"Location: {args.location}")
    logger.info(f"Limit: {args.limit}")
    logger.info(f"Log Level: {args.log_level}")
    
    try:
        # Initialize components
        search_engine = SearchEngine()
        profile_builder = ProfileBuilder()
        contact_extractor = ContactExtractor()
        export_manager = ExportManager(args.output) if args.output else ExportManager()
        
        # Step 1: Business Discovery
        logger.info("\n📊 Step 1: Business Discovery")
        leads = await search_engine.search_businesses(
            industry=args.industry,
            location=args.location,
            limit=args.limit
        )
        
        if not leads:
            logger.warning("No businesses found. Exiting.")
            return
        
        logger.info(f"✓ Discovered {len(leads)} business leads")
        
        # Step 2: Profile Building & Enrichment
        logger.info("\n🔍 Step 2: Profile Building & Enrichment")
        profiles = await profile_builder.build_profiles(leads)
        
        if not profiles:
            logger.warning("No profiles could be built. Exiting.")
            return
        
        logger.info(f"✓ Built {len(profiles)} enriched business profiles")
        
        # Step 3: Contact Extraction
        logger.info("\n👥 Step 3: Contact Extraction")
        contact_results = await contact_extractor.extract_contacts(profiles)
        
        logger.info(f"✓ Extracted contacts from {len(contact_results)} businesses")
        
        # Step 4: Export Results
        logger.info("\n📁 Step 4: Export Results")
        export_path = export_manager.export_campaign(
            profiles=profiles,
            contact_results=contact_results,
            industry=args.industry,
            location=args.location
        )
        
        logger.info(f"✓ Results exported to: {export_path}")
        
        # Summary statistics
        total_contacts = sum(len(cr.all_contacts) for cr in contact_results)
        total_decision_makers = sum(len(cr.decision_makers) for cr in contact_results)
        
        logger.info("\n" + "=" * 60)
        logger.info("CAMPAIGN SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Businesses Discovered: {len(leads)}")
        logger.info(f"Profiles Built: {len(profiles)}")
        logger.info(f"Total Contacts: {total_contacts}")
        logger.info(f"Decision Makers: {total_decision_makers}")
        logger.info(f"Export Location: {export_path}")
        
        # Show sample results
        if profiles:
            logger.info("\n📋 Sample Results:")
            for i, profile in enumerate(profiles[:3], 1):
                contact_result = next(
                    (cr for cr in contact_results if cr.business_id == profile.lead.business_id), 
                    None
                )
                logger.info(f"{i}. {profile.lead.name}")
                logger.info(f"   Industry: {profile.lead.industry}")
                logger.info(f"   Location: {profile.lead.location}")
                logger.info(f"   Confidence: {profile.lead.confidence_score:.2f}")
                logger.info(f"   Enrichment: {profile.enrichment_score:.2f}")
                if contact_result:
                    logger.info(f"   Contacts: {len(contact_result.all_contacts)} ({len(contact_result.decision_makers)} decision makers)")
                logger.info("")
        
        logger.info("🎉 Pipeline completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {str(e)}")
        if args.log_level == "DEBUG":
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)

def cli_main():
    """CLI entry point that handles async execution."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()

# TODO: Future enhancements for main pipeline:
# - Configuration file support (.yaml/.toml)
# - Resume capability for interrupted campaigns
# - Parallel campaign processing
# - Real-time progress reporting with progress bars
# - Campaign scheduling and automation
# - Integration with task queues (Celery/RQ)
# - Web interface for campaign management
# - API endpoints for programmatic access
# - Database persistence for campaign history
# - Email notifications for campaign completion