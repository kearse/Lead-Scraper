"""Export manager for generating structured output files and folders."""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import asdict
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from profiles.profile_builder import BusinessProfile
from extractors.contact_extractor import ContactExtractionResult, Contact
from utils.logger import logger
from config.settings import settings

class ExportManager:
    """Manages export of business intelligence data to structured folders."""
    
    def __init__(self, export_base_dir: str = None):
        self.export_base_dir = Path(export_base_dir or settings.EXPORT_BASE_DIR)
        self.export_base_dir.mkdir(exist_ok=True)
    
    def export_campaign(
        self,
        profiles: List[BusinessProfile],
        contact_results: List[ContactExtractionResult],
        industry: str,
        location: str
    ) -> str:
        """Export a complete campaign to a structured folder.
        
        Args:
            profiles: List of business profiles
            contact_results: List of contact extraction results
            industry: Campaign industry
            location: Campaign location
            
        Returns:
            Path to the created export folder
        """
        # Create campaign folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_location = location.replace(", ", "_").replace(" ", "_")
        campaign_folder = f"{industry}_{safe_location}_{timestamp}"
        campaign_path = self.export_base_dir / campaign_folder
        campaign_path.mkdir(exist_ok=True)
        
        logger.info(f"Exporting campaign to: {campaign_path}")
        
        # Export master summaries
        self._export_master_summary(profiles, contact_results, campaign_path)
        
        # Export statistics
        self._export_statistics(profiles, contact_results, campaign_path)
        
        # Export individual business folders
        for profile in profiles:
            contact_result = self._find_contact_result(profile, contact_results)
            self._export_business_folder(profile, contact_result, campaign_path)
        
        logger.info(f"Campaign export completed: {campaign_path}")
        return str(campaign_path)
    
    def _export_master_summary(
        self,
        profiles: List[BusinessProfile],
        contact_results: List[ContactExtractionResult],
        campaign_path: Path
    ) -> None:
        """Export master summary files (JSON and CSV)."""
        
        # Prepare summary data
        summary_data = []
        for profile in profiles:
            contact_result = self._find_contact_result(profile, contact_results)
            
            business_summary = {
                "business_name": profile.lead.name,
                "business_id": profile.lead.business_id,
                "industry": profile.lead.industry,
                "location": profile.lead.location,
                "address": profile.lead.address,
                "phone": profile.lead.phone,
                "website": profile.lead.website,
                "email": profile.lead.email,
                "source": profile.lead.source,
                "confidence_score": profile.lead.confidence_score,
                "enrichment_score": profile.enrichment_score,
                "extraction_score": contact_result.extraction_score if contact_result else 0.0,
                "total_contacts": len(contact_result.all_contacts) if contact_result else 0,
                "decision_makers": len(contact_result.decision_makers) if contact_result else 0,
                "social_profiles": len(profile.social_profiles),
                "news_articles": len(profile.news_articles),
                "directory_listings": len(profile.directory_listings),
                "discovered_at": profile.lead.discovered_at.isoformat(),
                "enriched_at": profile.enriched_at.isoformat()
            }
            summary_data.append(business_summary)
        
        # Export JSON
        json_path = campaign_path / "master_summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        # Export CSV
        csv_path = campaign_path / "master_summary.csv"
        if summary_data:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
                writer.writeheader()
                writer.writerows(summary_data)
        
        logger.debug(f"Exported master summaries: {json_path}, {csv_path}")
    
    def _export_statistics(
        self,
        profiles: List[BusinessProfile],
        contact_results: List[ContactExtractionResult],
        campaign_path: Path
    ) -> None:
        """Export campaign statistics."""
        
        # Calculate statistics
        total_businesses = len(profiles)
        total_contacts = sum(len(cr.all_contacts) for cr in contact_results)
        total_decision_makers = sum(len(cr.decision_makers) for cr in contact_results)
        
        # Source distribution
        source_counts = {}
        for profile in profiles:
            source = profile.lead.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Enrichment source statistics
        enrichment_sources = {}
        for profile in profiles:
            for source in profile.enrichment_sources:
                enrichment_sources[source] = enrichment_sources.get(source, 0) + 1
        
        # Extraction source statistics
        extraction_sources = {}
        for contact_result in contact_results:
            for source in contact_result.sources_used:
                extraction_sources[source] = extraction_sources.get(source, 0) + 1
        
        # Average scores
        avg_confidence = sum(p.lead.confidence_score for p in profiles) / total_businesses if total_businesses > 0 else 0
        avg_enrichment = sum(p.enrichment_score for p in profiles) / total_businesses if total_businesses > 0 else 0
        avg_extraction = sum(cr.extraction_score for cr in contact_results) / len(contact_results) if contact_results else 0
        
        statistics = {
            "campaign_summary": {
                "total_businesses": total_businesses,
                "total_contacts": total_contacts,
                "total_decision_makers": total_decision_makers,
                "businesses_with_contacts": len([cr for cr in contact_results if cr.all_contacts]),
                "businesses_with_decision_makers": len([cr for cr in contact_results if cr.decision_makers])
            },
            "source_distribution": source_counts,
            "enrichment_sources": enrichment_sources,
            "extraction_sources": extraction_sources,
            "average_scores": {
                "confidence_score": round(avg_confidence, 3),
                "enrichment_score": round(avg_enrichment, 3),
                "extraction_score": round(avg_extraction, 3)
            },
            "export_metadata": {
                "exported_at": datetime.now().isoformat(),
                "export_version": "1.0"
            }
        }
        
        # Export statistics
        stats_path = campaign_path / "statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Exported statistics: {stats_path}")
    
    def _export_business_folder(
        self,
        profile: BusinessProfile,
        contact_result: ContactExtractionResult,
        campaign_path: Path
    ) -> None:
        """Export individual business folder with all data."""
        
        # Create business folder
        safe_name = self._safe_filename(profile.lead.name)
        business_path = campaign_path / safe_name
        business_path.mkdir(exist_ok=True)
        
        # Export business profile
        self._export_business_profile(profile, business_path)
        
        # Export business summary
        self._export_business_summary(profile, contact_result, business_path)
        
        # Export source-specific data
        self._export_source_data(profile, business_path)
        
        # Export contacts
        if contact_result:
            self._export_contacts(contact_result, business_path)
        
        logger.debug(f"Exported business folder: {business_path}")
    
    def _export_business_profile(self, profile: BusinessProfile, business_path: Path) -> None:
        """Export complete business profile as JSON."""
        
        # Convert profile to dictionary (handling nested objects)
        profile_data = {
            "lead": asdict(profile.lead),
            "description": profile.description,
            "founded_year": profile.founded_year,
            "employee_count": profile.employee_count,
            "annual_revenue": profile.annual_revenue,
            "social_profiles": [asdict(sp) for sp in profile.social_profiles],
            "news_articles": [asdict(na) for na in profile.news_articles],
            "directory_listings": profile.directory_listings,
            "enrichment_score": profile.enrichment_score,
            "enriched_at": profile.enriched_at.isoformat(),
            "enrichment_sources": profile.enrichment_sources
        }
        
        # Handle datetime serialization
        if profile_data["lead"]["discovered_at"]:
            profile_data["lead"]["discovered_at"] = profile.lead.discovered_at.isoformat()
        
        for sp in profile_data["social_profiles"]:
            if sp.get("last_post"):
                sp["last_post"] = sp["last_post"].isoformat() if hasattr(sp["last_post"], 'isoformat') else sp["last_post"]
        
        for na in profile_data["news_articles"]:
            if na.get("published_date"):
                na["published_date"] = na["published_date"].isoformat() if hasattr(na["published_date"], 'isoformat') else na["published_date"]
        
        profile_path = business_path / "profile.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
    
    def _export_business_summary(
        self,
        profile: BusinessProfile,
        contact_result: ContactExtractionResult,
        business_path: Path
    ) -> None:
        """Export human-readable business summary."""
        
        summary_lines = [
            f"Business Summary: {profile.lead.name}",
            "=" * 50,
            f"Industry: {profile.lead.industry}",
            f"Location: {profile.lead.location}",
            f"Address: {profile.lead.address or 'Not available'}",
            f"Phone: {profile.lead.phone or 'Not available'}",
            f"Website: {profile.lead.website or 'Not available'}",
            f"Source: {profile.lead.source}",
            "",
            f"Confidence Score: {profile.lead.confidence_score:.2f}",
            f"Enrichment Score: {profile.enrichment_score:.2f}",
            "",
            f"Description: {profile.description or 'Not available'}",
            f"Founded: {profile.founded_year or 'Unknown'}",
            f"Employees: {profile.employee_count or 'Unknown'}",
            f"Revenue: {profile.annual_revenue or 'Unknown'}",
            "",
            f"Social Media Profiles: {len(profile.social_profiles)}",
            f"News Articles: {len(profile.news_articles)}",
            f"Directory Listings: {len(profile.directory_listings)}",
            ""
        ]
        
        if contact_result:
            summary_lines.extend([
                f"Total Contacts: {len(contact_result.all_contacts)}",
                f"Decision Makers: {len(contact_result.decision_makers)}",
                f"Extraction Score: {contact_result.extraction_score:.2f}",
                ""
            ])
            
            if contact_result.decision_makers:
                summary_lines.append("Key Decision Makers:")
                for dm in contact_result.decision_makers[:3]:  # Top 3
                    summary_lines.append(f"  - {dm.name} ({dm.title or 'No title'})")
                    if dm.email:
                        summary_lines.append(f"    Email: {dm.email}")
                    summary_lines.append(f"    Score: {dm.decision_maker_score:.2f}")
                summary_lines.append("")
        
        summary_path = business_path / "summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
    
    def _export_source_data(self, profile: BusinessProfile, business_path: Path) -> None:
        """Export source-specific data folders."""
        
        # Google Business (from lead data)
        if profile.lead.source == "google_places" or profile.lead.raw_data:
            google_path = business_path / "google_business"
            google_path.mkdir(exist_ok=True)
            
            google_data = {
                "business_profile": asdict(profile.lead),
                "raw_data": profile.lead.raw_data
            }
            
            with open(google_path / "google_business_profile.json", 'w', encoding='utf-8') as f:
                json.dump(google_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Social Media
        if profile.social_profiles:
            social_path = business_path / "social_media"
            social_path.mkdir(exist_ok=True)
            
            for social_profile in profile.social_profiles:
                filename = f"{social_profile.platform}_profile.json"
                social_data = asdict(social_profile)
                
                with open(social_path / filename, 'w', encoding='utf-8') as f:
                    json.dump(social_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _export_contacts(self, contact_result: ContactExtractionResult, business_path: Path) -> None:
        """Export all contacts and decision makers."""
        
        contacts_path = business_path / "contacts"
        contacts_path.mkdir(exist_ok=True)
        
        # All contacts JSON
        all_contacts_data = [asdict(contact) for contact in contact_result.all_contacts]
        with open(contacts_path / "all_contacts.json", 'w', encoding='utf-8') as f:
            json.dump(all_contacts_data, f, indent=2, ensure_ascii=False, default=str)
        
        # All contacts CSV
        if contact_result.all_contacts:
            with open(contacts_path / "all_contacts.csv", 'w', newline='', encoding='utf-8') as f:
                # Flatten contact data for CSV
                fieldnames = ['name', 'title', 'email', 'phone', 'linkedin_url', 
                             'confidence_score', 'decision_maker_score', 'source', 'extracted_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for contact in contact_result.all_contacts:
                    row = {
                        'name': contact.name,
                        'title': contact.title,
                        'email': contact.email,
                        'phone': contact.phone,
                        'linkedin_url': contact.linkedin_url,
                        'confidence_score': contact.confidence_score,
                        'decision_maker_score': contact.decision_maker_score,
                        'source': contact.source,
                        'extracted_at': contact.extracted_at.isoformat()
                    }
                    writer.writerow(row)
        
        # Decision makers JSON
        decision_makers_data = [asdict(dm) for dm in contact_result.decision_makers]
        with open(contacts_path / "decision_makers.json", 'w', encoding='utf-8') as f:
            json.dump(decision_makers_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Decision makers CSV
        if contact_result.decision_makers:
            with open(contacts_path / "decision_makers.csv", 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'title', 'email', 'phone', 'linkedin_url', 
                             'confidence_score', 'decision_maker_score', 'source', 'extracted_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for dm in contact_result.decision_makers:
                    row = {
                        'name': dm.name,
                        'title': dm.title,
                        'email': dm.email,
                        'phone': dm.phone,
                        'linkedin_url': dm.linkedin_url,
                        'confidence_score': dm.confidence_score,
                        'decision_maker_score': dm.decision_maker_score,
                        'source': dm.source,
                        'extracted_at': dm.extracted_at.isoformat()
                    }
                    writer.writerow(row)
    
    def _find_contact_result(
        self, 
        profile: BusinessProfile, 
        contact_results: List[ContactExtractionResult]
    ) -> ContactExtractionResult:
        """Find contact result for a specific business profile."""
        for contact_result in contact_results:
            if contact_result.business_id == profile.lead.business_id:
                return contact_result
        return None
    
    def _safe_filename(self, name: str) -> str:
        """Convert business name to safe filename."""
        # Remove/replace unsafe characters
        safe = name.replace('/', '_').replace('\\', '_').replace(':', '_')
        safe = safe.replace('?', '').replace('*', '').replace('<', '').replace('>', '')
        safe = safe.replace('|', '_').replace('"', '').strip()
        
        # Limit length
        if len(safe) > 50:
            safe = safe[:50].strip()
        
        return safe or "Unknown_Business"

# TODO: Future enhancements for export:
# - Excel export with multiple sheets
# - PDF report generation
# - Email integration for automatic delivery
# - Cloud storage integration (S3, Google Drive)
# - Data visualization and charts
# - Template-based custom exports
# - Incremental export updates
# - Export scheduling and automation