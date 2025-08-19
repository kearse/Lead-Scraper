"""Export manager for structured output generation."""

import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.profiles.profile_builder import BusinessProfile, Contact
from src.utils.logger import logger
from config.settings import settings


class ExportManager:
    """Manages export of business intelligence data to structured formats."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def create_campaign_export(
        self, 
        profiles: List[BusinessProfile], 
        industry: str, 
        location: str
    ) -> Path:
        """Create a complete campaign export with folder structure."""
        
        # Create campaign folder name
        safe_industry = self._sanitize_filename(industry)
        safe_location = self._sanitize_filename(location)
        campaign_name = f"{safe_industry}_{safe_location}_{self.timestamp}"
        
        # Create export directory
        export_path = settings.get_export_path(campaign_name)
        export_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating campaign export at: {export_path}")
        
        # Generate master summary files
        self._create_master_summary(profiles, export_path)
        
        # Generate statistics
        self._create_statistics(profiles, export_path, industry, location)
        
        # Create individual business folders
        for profile in profiles:
            self._create_business_folder(profile, export_path)
        
        logger.info(f"Campaign export completed: {campaign_name}")
        return export_path
    
    def _create_master_summary(self, profiles: List[BusinessProfile], export_path: Path) -> None:
        """Create master summary files (JSON and CSV)."""
        logger.debug("Creating master summary files")
        
        # Prepare summary data
        summary_data = []
        for profile in profiles:
            summary_item = {
                "name": profile.name,
                "address": profile.address,
                "phone": profile.phone,
                "website": profile.website,
                "industry": profile.industry,
                "employee_count": profile.employee_count,
                "confidence_score": profile.confidence_score,
                "total_contacts": len(profile.contacts),
                "decision_makers": len(profile.get_decision_makers()),
                "sources": ", ".join(profile.sources),
                "last_updated": profile.last_updated
            }
            summary_data.append(summary_item)
        
        # Write JSON summary
        json_path = export_path / "master_summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        # Write CSV summary
        csv_path = export_path / "master_summary.csv"
        if summary_data:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
                writer.writeheader()
                writer.writerows(summary_data)
        
        logger.info(f"Master summary created: {len(summary_data)} businesses")
    
    def _create_statistics(
        self, 
        profiles: List[BusinessProfile], 
        export_path: Path, 
        industry: str, 
        location: str
    ) -> None:
        """Create campaign statistics."""
        logger.debug("Creating campaign statistics")
        
        total_contacts = sum(len(p.contacts) for p in profiles)
        total_decision_makers = sum(len(p.get_decision_makers()) for p in profiles)
        total_emails = sum(len(p.get_all_emails()) for p in profiles)
        total_phones = sum(len(p.get_all_phones()) for p in profiles)
        
        # Calculate average confidence
        avg_confidence = sum(p.confidence_score for p in profiles) / len(profiles) if profiles else 0
        
        # Source breakdown
        source_counts = {}
        for profile in profiles:
            for source in profile.sources:
                source_counts[source] = source_counts.get(source, 0) + 1
        
        # Industry breakdown (in case of mixed results)
        industry_counts = {}
        for profile in profiles:
            industry = profile.industry or "Unknown"
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        statistics = {
            "campaign_info": {
                "search_industry": industry,
                "search_location": location,
                "timestamp": self.timestamp,
                "total_businesses": len(profiles)
            },
            "contact_summary": {
                "total_contacts": total_contacts,
                "total_decision_makers": total_decision_makers,
                "total_emails": total_emails,
                "total_phones": total_phones,
                "avg_contacts_per_business": round(total_contacts / len(profiles), 2) if profiles else 0
            },
            "quality_metrics": {
                "average_confidence_score": round(avg_confidence, 3),
                "businesses_with_contacts": len([p for p in profiles if p.contacts]),
                "businesses_with_decision_makers": len([p for p in profiles if p.get_decision_makers()]),
                "businesses_with_social_media": len([p for p in profiles if p.social_media])
            },
            "source_breakdown": source_counts,
            "industry_breakdown": industry_counts
        }
        
        # Write statistics file
        stats_path = export_path / "statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)
        
        logger.info("Campaign statistics created")
    
    def _create_business_folder(self, profile: BusinessProfile, export_path: Path) -> None:
        """Create individual business folder with all data."""
        logger.debug(f"Creating business folder for: {profile.name}")
        
        # Create business folder
        folder_name = self._sanitize_filename(profile.name)
        business_path = export_path / folder_name
        business_path.mkdir(exist_ok=True)
        
        # Create main profile JSON
        profile_path = business_path / "profile.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Create human-readable summary
        self._create_business_summary(profile, business_path)
        
        # Create subfolders for different data types
        self._create_contacts_folder(profile, business_path)
        self._create_google_business_folder(profile, business_path)
        self._create_social_media_folder(profile, business_path)
        self._create_news_mentions_folder(profile, business_path)
    
    def _create_business_summary(self, profile: BusinessProfile, business_path: Path) -> None:
        """Create human-readable business summary."""
        summary_lines = [
            f"Business Profile Summary",
            f"=" * 40,
            f"",
            f"Name: {profile.name}",
            f"Industry: {profile.industry or 'Unknown'}",
            f"Address: {profile.address or 'Not available'}",
            f"Phone: {profile.phone or 'Not available'}",
            f"Website: {profile.website or 'Not available'}",
            f"",
            f"Company Information:",
            f"  Founded: {profile.founded_year or 'Unknown'}",
            f"  Employees: {profile.employee_count or 'Unknown'}",
            f"  Revenue: {profile.annual_revenue or 'Unknown'}",
            f"  Description: {profile.description or 'No description available'}",
            f"",
            f"Contact Summary:",
            f"  Total Contacts: {len(profile.contacts)}",
            f"  Decision Makers: {len(profile.get_decision_makers())}",
            f"  Email Addresses: {len(profile.get_all_emails())}",
            f"  Phone Numbers: {len(profile.get_all_phones())}",
            f"",
            f"Social Media Presence:",
            f"  Platforms: {len(profile.social_media)}",
        ]
        
        if profile.social_media:
            for social in profile.social_media:
                summary_lines.append(f"    {social.platform}: {social.url or 'URL not available'}")
        
        summary_lines.extend([
            f"",
            f"Data Quality:",
            f"  Confidence Score: {profile.confidence_score:.2f}",
            f"  Sources: {', '.join(profile.sources)}",
            f"  Last Updated: {profile.last_updated}",
            f"",
            f"News Mentions: {len(profile.news_mentions)}",
        ])
        
        if profile.news_mentions:
            for article in profile.news_mentions[:3]:  # Show up to 3 articles
                summary_lines.append(f"  - {article.title} ({article.source})")
        
        summary_text = "\n".join(summary_lines)
        
        summary_path = business_path / "summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
    
    def _create_contacts_folder(self, profile: BusinessProfile, business_path: Path) -> None:
        """Create contacts subfolder with all contact data."""
        if not profile.contacts:
            return
        
        contacts_path = business_path / "contacts"
        contacts_path.mkdir(exist_ok=True)
        
        # All contacts JSON
        all_contacts_data = [contact.to_dict() for contact in profile.contacts]
        with open(contacts_path / "all_contacts.json", 'w', encoding='utf-8') as f:
            json.dump(all_contacts_data, f, indent=2, ensure_ascii=False)
        
        # All contacts CSV
        if all_contacts_data:
            with open(contacts_path / "all_contacts.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_contacts_data[0].keys())
                writer.writeheader()
                writer.writerows(all_contacts_data)
        
        # Decision makers only
        decision_makers = profile.get_decision_makers()
        if decision_makers:
            dm_data = [dm.to_dict() for dm in decision_makers]
            
            with open(contacts_path / "decision_makers.json", 'w', encoding='utf-8') as f:
                json.dump(dm_data, f, indent=2, ensure_ascii=False)
            
            with open(contacts_path / "decision_makers.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=dm_data[0].keys())
                writer.writeheader()
                writer.writerows(dm_data)
    
    def _create_google_business_folder(self, profile: BusinessProfile, business_path: Path) -> None:
        """Create Google Business subfolder."""
        google_path = business_path / "google_business"
        google_path.mkdir(exist_ok=True)
        
        # Mock Google Business profile data
        google_data = {
            "business_name": profile.name,
            "google_place_id": f"mock_place_id_{hash(profile.name) % 10000}",
            "rating": round(3.5 + (hash(profile.name) % 15) / 10, 1),
            "review_count": (hash(profile.name) % 500) + 10,
            "categories": [profile.industry] if profile.industry else [],
            "hours": {
                "monday": "9:00 AM - 5:00 PM",
                "tuesday": "9:00 AM - 5:00 PM", 
                "wednesday": "9:00 AM - 5:00 PM",
                "thursday": "9:00 AM - 5:00 PM",
                "friday": "9:00 AM - 5:00 PM",
                "saturday": "10:00 AM - 2:00 PM",
                "sunday": "Closed"
            },
            "photos": [
                f"https://maps.googleapis.com/photo1_{profile.name.replace(' ', '_')}.jpg",
                f"https://maps.googleapis.com/photo2_{profile.name.replace(' ', '_')}.jpg"
            ],
            "reviews_sample": [
                {
                    "author": "John D.",
                    "rating": 5,
                    "text": "Great service and professional staff!",
                    "date": "2023-10-15"
                },
                {
                    "author": "Sarah M.",
                    "rating": 4,
                    "text": "Good experience overall, would recommend.",
                    "date": "2023-09-28"
                }
            ]
        }
        
        with open(google_path / "google_business_profile.json", 'w', encoding='utf-8') as f:
            json.dump(google_data, f, indent=2, ensure_ascii=False)
    
    def _create_social_media_folder(self, profile: BusinessProfile, business_path: Path) -> None:
        """Create social media subfolder."""
        if not profile.social_media:
            return
        
        social_path = business_path / "social_media"
        social_path.mkdir(exist_ok=True)
        
        for social in profile.social_media:
            platform_file = f"{social.platform.lower()}_profile.json"
            social_data = social.to_dict()
            
            # Add mock additional data based on platform
            if social.platform.lower() == "linkedin":
                social_data.update({
                    "company_size": profile.employee_count,
                    "industry": profile.industry,
                    "specialties": [profile.industry, "Customer Service", "Local Business"]
                })
            elif social.platform.lower() == "facebook":
                social_data.update({
                    "page_likes": social.followers,
                    "check_ins": (hash(profile.name) % 100) + 10,
                    "page_category": "Local Business"
                })
            
            with open(social_path / platform_file, 'w', encoding='utf-8') as f:
                json.dump(social_data, f, indent=2, ensure_ascii=False)
    
    def _create_news_mentions_folder(self, profile: BusinessProfile, business_path: Path) -> None:
        """Create news mentions subfolder."""
        if not profile.news_mentions:
            return
        
        news_path = business_path / "news_mentions"
        news_path.mkdir(exist_ok=True)
        
        news_data = [article.to_dict() for article in profile.news_mentions]
        
        with open(news_path / "news_articles.json", 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Replace spaces and other characters with underscores
        sanitized = re.sub(r'[\s,.-]+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized or "unknown_business"