"""Contact extraction and enrichment utilities."""

import re
import random
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.profiles.profile_builder import Contact, BusinessProfile
from src.utils.logger import logger
from config.constants import DECISION_MAKER_ROLES


@dataclass
class ExtractedContact:
    """Represents contact information extracted from text."""
    
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    source: str = "text_extraction"
    confidence: float = 0.5


class ContactExtractor:
    """Extracts and processes contact information."""
    
    def __init__(self):
        # Email regex pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone number patterns (US format)
        self.phone_patterns = [
            re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}'),  # (123) 456-7890
            re.compile(r'\d{3}-\d{3}-\d{4}'),        # 123-456-7890
            re.compile(r'\d{3}\.\d{3}\.\d{4}'),      # 123.456.7890
            re.compile(r'\d{10}'),                   # 1234567890
        ]
        
        # Name patterns (simple heuristics)
        self.name_pattern = re.compile(
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'  # First Last
        )
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        if not text:
            return []
        
        matches = self.email_pattern.findall(text)
        return list(set(matches))  # Remove duplicates
    
    def extract_phones_from_text(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        if not text:
            return []
        
        phones = []
        for pattern in self.phone_patterns:
            matches = pattern.findall(text)
            phones.extend(matches)
        
        return list(set(self._normalize_phones(phones)))
    
    def extract_names_from_text(self, text: str) -> List[str]:
        """Extract potential names from text."""
        if not text:
            return []
        
        matches = self.name_pattern.findall(text)
        
        # Filter out common false positives
        filtered_names = []
        for name in matches:
            if not self._is_likely_name(name):
                continue
            filtered_names.append(name)
        
        return list(set(filtered_names))
    
    def extract_contacts_from_profile(self, profile: BusinessProfile) -> List[Contact]:
        """Extract additional contacts from business profile data."""
        logger.debug(f"Extracting contacts from profile: {profile.name}")
        
        extracted_contacts = []
        
        # Extract from website content (mock)
        if profile.website:
            mock_website_content = self._get_mock_website_content(profile)
            website_contacts = self._extract_from_text(mock_website_content, "website")
            extracted_contacts.extend(website_contacts)
        
        # Extract from social media (mock)
        for social in profile.social_media:
            social_contacts = self._extract_from_social_media(social, profile)
            extracted_contacts.extend(social_contacts)
        
        # Deduplicate and enhance existing contacts
        enhanced_contacts = self._enhance_contacts(profile.contacts, extracted_contacts)
        
        return enhanced_contacts
    
    def score_decision_makers(self, contacts: List[Contact]) -> List[Contact]:
        """Score contacts for likelihood of being decision makers."""
        for contact in contacts:
            contact.is_decision_maker = self._is_decision_maker(contact)
        
        return contacts
    
    def _extract_from_text(self, text: str, source: str) -> List[Contact]:
        """Extract contacts from arbitrary text."""
        contacts = []
        
        emails = self.extract_emails_from_text(text)
        phones = self.extract_phones_from_text(text)
        names = self.extract_names_from_text(text)
        
        # Create contacts from extracted information
        # This is a simplified implementation - real version would be more sophisticated
        for email in emails:
            contact = Contact(
                email=email,
                source=source,
                confidence_score=0.7
            )
            
            # Try to infer name from email
            if '@' in email:
                local_part = email.split('@')[0]
                if '.' in local_part:
                    name_parts = local_part.split('.')
                    if len(name_parts) == 2:
                        contact.name = f"{name_parts[0].title()} {name_parts[1].title()}"
                        contact.confidence_score = 0.6
            
            contacts.append(contact)
        
        # Create contacts from phone numbers
        for phone in phones:
            contact = Contact(
                phone=phone,
                source=source,
                confidence_score=0.5
            )
            contacts.append(contact)
        
        return contacts
    
    def _extract_from_social_media(self, social_profile, business_profile) -> List[Contact]:
        """Extract contacts from social media profiles (mock)."""
        contacts = []
        
        # Mock extraction based on platform
        if social_profile.platform.lower() == "linkedin":
            # Mock LinkedIn contacts
            mock_contact = Contact(
                name=f"Manager at {business_profile.name}",
                title="Business Manager",
                source="linkedin",
                confidence_score=0.6
            )
            contacts.append(mock_contact)
        
        return contacts
    
    def _enhance_contacts(self, existing_contacts: List[Contact], extracted_contacts: List[Contact]) -> List[Contact]:
        """Enhance existing contacts with extracted information."""
        enhanced = existing_contacts.copy()
        
        # Simple enhancement: add extracted contacts that don't already exist
        existing_emails = {c.email for c in existing_contacts if c.email}
        existing_phones = {c.phone for c in existing_contacts if c.phone}
        
        for extracted in extracted_contacts:
            is_duplicate = False
            
            if extracted.email and extracted.email in existing_emails:
                is_duplicate = True
            if extracted.phone and extracted.phone in existing_phones:
                is_duplicate = True
            
            if not is_duplicate:
                enhanced.append(extracted)
        
        return enhanced
    
    def _normalize_phones(self, phones: List[str]) -> List[str]:
        """Normalize phone number formats."""
        normalized = []
        
        for phone in phones:
            # Remove all non-digits
            digits_only = re.sub(r'\D', '', phone)
            
            # Format as (XXX) XXX-XXXX if 10 digits
            if len(digits_only) == 10:
                formatted = f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
                normalized.append(formatted)
            elif len(digits_only) == 11 and digits_only.startswith('1'):
                # Remove leading 1
                digits_only = digits_only[1:]
                formatted = f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
                normalized.append(formatted)
            else:
                # Keep original if not standard format
                normalized.append(phone)
        
        return normalized
    
    def _is_likely_name(self, name: str) -> bool:
        """Check if extracted text is likely a real name."""
        # Simple heuristics to filter out false positives
        common_false_positives = {
            "About Us", "Contact Us", "Our Team", "Get Started",
            "Read More", "Learn More", "Sign Up", "Log In"
        }
        
        return name not in common_false_positives and len(name.split()) == 2
    
    def _is_decision_maker(self, contact: Contact) -> bool:
        """Determine if contact is likely a decision maker."""
        if not contact.title:
            return False
        
        title_lower = contact.title.lower()
        
        # Check for decision maker keywords
        for role in DECISION_MAKER_ROLES:
            if role.lower() in title_lower:
                return True
        
        return False
    
    def _get_mock_website_content(self, profile: BusinessProfile) -> str:
        """Generate mock website content for extraction testing."""
        mock_content = f"""
        Welcome to {profile.name}
        
        Contact Information:
        Phone: {profile.phone or '(555) 123-4567'}
        Email: info@{profile.name.lower().replace(' ', '')}.com
        
        About Our Team:
        John Smith - Owner and CEO
        Email: john.smith@{profile.name.lower().replace(' ', '')}.com
        
        Sarah Johnson - Operations Manager  
        Phone: (555) 987-6543
        
        For business inquiries, contact us at:
        business@{profile.name.lower().replace(' ', '')}.com
        """
        
        return mock_content
    
    def deduplicate_contacts(self, contacts: List[Contact]) -> List[Contact]:
        """Remove duplicate contacts based on email and phone."""
        seen_emails: Set[str] = set()
        seen_phones: Set[str] = set()
        unique_contacts = []
        
        for contact in contacts:
            is_duplicate = False
            
            if contact.email:
                if contact.email in seen_emails:
                    is_duplicate = True
                else:
                    seen_emails.add(contact.email)
            
            if contact.phone:
                if contact.phone in seen_phones:
                    is_duplicate = True
                else:
                    seen_phones.add(contact.phone)
            
            if not is_duplicate:
                unique_contacts.append(contact)
        
        return unique_contacts
    
    def enrich_contact_names(self, contacts: List[Contact]) -> List[Contact]:
        """Enhance contact names using various heuristics."""
        for contact in contacts:
            if not contact.name and contact.email:
                # Try to infer name from email
                local_part = contact.email.split('@')[0]
                if '.' in local_part:
                    parts = local_part.split('.')
                    if len(parts) == 2:
                        contact.name = f"{parts[0].title()} {parts[1].title()}"
                elif '_' in local_part:
                    parts = local_part.split('_')
                    if len(parts) == 2:
                        contact.name = f"{parts[0].title()} {parts[1].title()}"
        
        return contacts