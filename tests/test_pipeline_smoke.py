"""Smoke test for the complete Lead Scraper pipeline."""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from discovery.search_engine import SearchEngine
from profiles.profile_builder import ProfileBuilder
from extractors.contact_extractor import ContactExtractor
from export.export_manager import ExportManager

class TestPipelineSmoke:
    """Smoke tests for the complete pipeline."""
    
    def test_pipeline_components_import(self):
        """Test that all pipeline components can be imported."""
        # If we get here without import errors, the test passes
        assert SearchEngine is not None
        assert ProfileBuilder is not None
        assert ContactExtractor is not None
        assert ExportManager is not None
    
    @pytest.mark.asyncio
    async def test_discovery_engine(self):
        """Test the discovery engine with simulated data."""
        search_engine = SearchEngine()
        
        leads = await search_engine.search_businesses(
            industry="restaurants",
            location="Test City",
            limit=3
        )
        
        assert leads is not None
        assert len(leads) > 0
        assert len(leads) <= 3
        
        # Check lead structure
        lead = leads[0]
        assert lead.name is not None
        assert lead.business_id is not None
        assert lead.source is not None
        assert lead.industry == "restaurants"
        assert lead.location == "Test City"
        assert 0 <= lead.confidence_score <= 1
    
    @pytest.mark.asyncio
    async def test_profile_builder(self):
        """Test the profile builder with mock leads."""
        search_engine = SearchEngine()
        profile_builder = ProfileBuilder()
        
        # Get some test leads
        leads = await search_engine.search_businesses(
            industry="technology",
            location="Test City",
            limit=2
        )
        
        # Build profiles
        profiles = await profile_builder.build_profiles(leads)
        
        assert profiles is not None
        assert len(profiles) == len(leads)
        
        # Check profile structure
        profile = profiles[0]
        assert profile.lead is not None
        assert 0 <= profile.enrichment_score <= 1
        assert profile.enriched_at is not None
    
    @pytest.mark.asyncio
    async def test_contact_extractor(self):
        """Test the contact extractor with mock profiles."""
        search_engine = SearchEngine()
        profile_builder = ProfileBuilder()
        contact_extractor = ContactExtractor()
        
        # Build the pipeline up to profiles
        leads = await search_engine.search_businesses(
            industry="retail",
            location="Test City",
            limit=2
        )
        profiles = await profile_builder.build_profiles(leads)
        
        # Extract contacts
        contact_results = await contact_extractor.extract_contacts(profiles)
        
        assert contact_results is not None
        assert len(contact_results) == len(profiles)
        
        # Check contact result structure
        if contact_results:
            result = contact_results[0]
            assert result.business_name is not None
            assert result.business_id is not None
            assert result.all_contacts is not None
            assert result.decision_makers is not None
            assert 0 <= result.extraction_score <= 1
    
    def test_export_manager(self):
        """Test the export manager with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager = ExportManager(temp_dir)
            
            # Test that export manager initializes correctly
            assert export_manager.export_base_dir.exists()
            assert str(export_manager.export_base_dir) == temp_dir
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self):
        """Test the complete pipeline end-to-end."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize all components
            search_engine = SearchEngine()
            profile_builder = ProfileBuilder()
            contact_extractor = ContactExtractor()
            export_manager = ExportManager(temp_dir)
            
            # Run the complete pipeline
            leads = await search_engine.search_businesses(
                industry="services",
                location="Test City",
                limit=2
            )
            
            profiles = await profile_builder.build_profiles(leads)
            contact_results = await contact_extractor.extract_contacts(profiles)
            
            export_path = export_manager.export_campaign(
                profiles=profiles,
                contact_results=contact_results,
                industry="services",
                location="Test City"
            )
            
            # Verify export was created
            export_dir = Path(export_path)
            assert export_dir.exists()
            assert export_dir.is_dir()
            
            # Check for expected files
            assert (export_dir / "master_summary.json").exists()
            assert (export_dir / "master_summary.csv").exists()
            assert (export_dir / "statistics.json").exists()
            
            # Check for business folders
            business_dirs = [d for d in export_dir.iterdir() if d.is_dir()]
            assert len(business_dirs) == len(profiles)
            
            # Check structure of first business folder
            if business_dirs:
                business_dir = business_dirs[0]
                assert (business_dir / "profile.json").exists()
                assert (business_dir / "summary.txt").exists()
                
                # Check for contacts folder if contacts were extracted
                if any(len(cr.all_contacts) > 0 for cr in contact_results):
                    contacts_dir = business_dir / "contacts"
                    if contacts_dir.exists():
                        assert (contacts_dir / "all_contacts.json").exists()
                        assert (contacts_dir / "decision_makers.json").exists()

if __name__ == "__main__":
    # Run tests directly
    asyncio.run(TestPipelineSmoke().test_complete_pipeline())
    print("✓ All smoke tests passed!")