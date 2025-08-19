"""Simple smoke test for the complete Lead Scraper pipeline."""

import asyncio
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from discovery.search_engine import SearchEngine
from profiles.profile_builder import ProfileBuilder
from extractors.contact_extractor import ContactExtractor
from export.export_manager import ExportManager

async def test_complete_pipeline():
    """Test the complete pipeline end-to-end."""
    print("🧪 Testing complete pipeline...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize all components
        search_engine = SearchEngine()
        profile_builder = ProfileBuilder()
        contact_extractor = ContactExtractor()
        export_manager = ExportManager(temp_dir)
        
        # Run the complete pipeline
        print("  📊 Testing discovery...")
        leads = await search_engine.search_businesses(
            industry="services",
            location="Test City",
            limit=2
        )
        assert leads, "No leads discovered"
        assert len(leads) <= 2, "Too many leads"
        print(f"  ✓ Discovered {len(leads)} leads")
        
        print("  🔍 Testing profile building...")
        profiles = await profile_builder.build_profiles(leads)
        assert profiles, "No profiles built"
        assert len(profiles) == len(leads), "Profile count mismatch"
        print(f"  ✓ Built {len(profiles)} profiles")
        
        print("  👥 Testing contact extraction...")
        contact_results = await contact_extractor.extract_contacts(profiles)
        assert contact_results, "No contact results"
        assert len(contact_results) == len(profiles), "Contact result count mismatch"
        print(f"  ✓ Extracted contacts from {len(contact_results)} businesses")
        
        print("  📁 Testing export...")
        export_path = export_manager.export_campaign(
            profiles=profiles,
            contact_results=contact_results,
            industry="services",
            location="Test City"
        )
        
        # Verify export was created
        export_dir = Path(export_path)
        assert export_dir.exists(), "Export directory not created"
        assert export_dir.is_dir(), "Export path is not directory"
        
        # Check for expected files
        assert (export_dir / "master_summary.json").exists(), "Missing master_summary.json"
        assert (export_dir / "master_summary.csv").exists(), "Missing master_summary.csv"
        assert (export_dir / "statistics.json").exists(), "Missing statistics.json"
        
        # Check for business folders
        business_dirs = [d for d in export_dir.iterdir() if d.is_dir()]
        assert len(business_dirs) == len(profiles), "Wrong number of business directories"
        
        print(f"  ✓ Export created successfully at {export_path}")
        print(f"  ✓ Found {len(business_dirs)} business directories")

async def main():
    """Run all tests."""
    try:
        await test_complete_pipeline()
        print("\n🎉 All smoke tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)