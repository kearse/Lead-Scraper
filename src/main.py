"""Main orchestrator for Business Intelligence Lead Scraper."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.discovery.search_engine import BusinessSearchEngine
from src.profiles.profile_builder import ProfileBuilder, BusinessProfile
from src.extractors.contact_extractor import ContactExtractor
from src.export.export_manager import ExportManager
from src.utils.logger import logger


class LeadScraperOrchestrator:
    """Main orchestrator for the lead scraping pipeline."""
    
    def __init__(self):
        self.search_engine = BusinessSearchEngine()
        self.profile_builder = ProfileBuilder()
        self.contact_extractor = ContactExtractor()
        self.export_manager = ExportManager()
    
    async def run_campaign(
        self, 
        industry: str, 
        location: str, 
        limit: int = 10
    ) -> Path:
        """Run a complete lead scraping campaign."""
        
        logger.info(f"Starting lead scraping campaign")
        logger.info(f"Industry: {industry}")
        logger.info(f"Location: {location}")
        logger.info(f"Limit: {limit}")
        
        try:
            # Step 1: Discover businesses
            logger.info("Step 1: Discovering businesses...")
            search_results = await self.search_engine.search_all_sources(
                industry=industry,
                location=location,
                limit=limit
            )
            
            if not search_results:
                logger.warning("No businesses found in search")
                return None
            
            logger.info(f"Found {len(search_results)} businesses")
            
            # Step 2: Build enriched profiles
            logger.info("Step 2: Building enriched business profiles...")
            profiles = []
            
            for search_result in search_results:
                try:
                    profile = await self.profile_builder.build_profile(search_result)
                    profiles.append(profile)
                except Exception as e:
                    logger.error(f"Error building profile for {search_result.name}: {e}")
                    continue
            
            logger.info(f"Built {len(profiles)} enriched profiles")
            
            # Step 3: Enhanced contact extraction and scoring
            logger.info("Step 3: Extracting and enhancing contacts...")
            for profile in profiles:
                try:
                    # Extract additional contacts
                    additional_contacts = self.contact_extractor.extract_contacts_from_profile(profile)
                    
                    # Combine with existing contacts
                    all_contacts = profile.contacts + additional_contacts
                    
                    # Deduplicate
                    unique_contacts = self.contact_extractor.deduplicate_contacts(all_contacts)
                    
                    # Enhance names
                    enhanced_contacts = self.contact_extractor.enrich_contact_names(unique_contacts)
                    
                    # Score decision makers
                    final_contacts = self.contact_extractor.score_decision_makers(enhanced_contacts)
                    
                    profile.contacts = final_contacts
                    
                except Exception as e:
                    logger.error(f"Error extracting contacts for {profile.name}: {e}")
                    continue
            
            total_contacts = sum(len(p.contacts) for p in profiles)
            total_decision_makers = sum(len(p.get_decision_makers()) for p in profiles)
            logger.info(f"Extracted {total_contacts} total contacts, {total_decision_makers} decision makers")
            
            # Step 4: Export results
            logger.info("Step 4: Exporting results...")
            export_path = self.export_manager.create_campaign_export(
                profiles=profiles,
                industry=industry,
                location=location
            )
            
            logger.info(f"Campaign completed successfully!")
            logger.info(f"Results exported to: {export_path}")
            
            # Print summary
            self._print_campaign_summary(profiles, export_path)
            
            return export_path
            
        except Exception as e:
            logger.error(f"Campaign failed: {e}")
            raise
    
    def _print_campaign_summary(self, profiles: List[BusinessProfile], export_path: Path) -> None:
        """Print a summary of the campaign results."""
        print("\n" + "="*60)
        print("CAMPAIGN SUMMARY")
        print("="*60)
        print(f"Total businesses found: {len(profiles)}")
        print(f"Total contacts extracted: {sum(len(p.contacts) for p in profiles)}")
        print(f"Total decision makers identified: {sum(len(p.get_decision_makers()) for p in profiles)}")
        print(f"Export location: {export_path}")
        print("\nTop businesses by confidence score:")
        
        # Sort by confidence score
        sorted_profiles = sorted(profiles, key=lambda p: p.confidence_score, reverse=True)
        
        for i, profile in enumerate(sorted_profiles[:5], 1):
            print(f"  {i}. {profile.name}")
            print(f"     Confidence: {profile.confidence_score:.2f}")
            print(f"     Contacts: {len(profile.contacts)} ({len(profile.get_decision_makers())} decision makers)")
            print(f"     Sources: {', '.join(profile.sources)}")
            print()
        
        print(f"View complete results in: {export_path}")
        print("="*60)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Business Intelligence Lead Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --industry "restaurants" --location "New York, NY" --limit 5
  python src/main.py --industry "law firms" --location "San Francisco, CA" --limit 10
  python src/main.py --industry "dental offices" --location "Chicago, IL"
        """
    )
    
    parser.add_argument(
        "--industry",
        required=True,
        help="Industry or business type to search for (e.g., 'restaurants', 'law firms')"
    )
    
    parser.add_argument(
        "--location", 
        required=True,
        help="Location to search in (e.g., 'New York, NY', 'San Francisco, CA')"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=settings.DEFAULT_SEARCH_LIMIT,
        help=f"Maximum number of businesses to find (default: {settings.DEFAULT_SEARCH_LIMIT})"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Ensure exports directory exists
        settings.ensure_exports_dir()
        
        # Create orchestrator and run campaign
        orchestrator = LeadScraperOrchestrator()
        
        export_path = await orchestrator.run_campaign(
            industry=args.industry,
            location=args.location,
            limit=args.limit
        )
        
        if export_path:
            print(f"\n✅ Campaign completed successfully!")
            print(f"📁 Results saved to: {export_path}")
            print(f"📊 Check master_summary.csv for a quick overview")
        else:
            print(f"\n❌ Campaign completed but no results found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Campaign interrupted by user")
        print("\n⏹️ Campaign stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Campaign failed: {e}")
        print(f"\n❌ Campaign failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if we're in mock mode
    if settings.USE_MOCK_DATA:
        print("🔧 Running in MOCK MODE - using simulated data")
        print("📋 No external APIs will be called")
        print()
    
    # Run the async main function
    asyncio.run(main())