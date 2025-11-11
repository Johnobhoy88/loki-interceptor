"""
Entity Recognizer - Extract and identify compliance-specific entities
Specialized for FCA, GDPR, HMRC, and legal terminology
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of compliance entities"""
    FCA_REFERENCE = "fca_reference"
    GDPR_ARTICLE = "gdpr_article"
    UK_LAW = "uk_law"
    HMRC_REFERENCE = "hmrc_reference"
    FINANCIAL_TERM = "financial_term"
    DATA_TERM = "data_term"
    TAX_TERM = "tax_term"
    LEGAL_TERM = "legal_term"
    COMPANY_NUMBER = "company_number"
    FRN = "frn"  # Financial Services Register Number
    VAT_NUMBER = "vat_number"
    AMOUNT = "amount"
    DATE = "date"
    PERCENTAGE = "percentage"


@dataclass
class Entity:
    """Recognized entity with metadata"""
    text: str
    entity_type: EntityType
    start: int
    end: int
    confidence: float
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class EntityRecognizer:
    """
    Extract and recognize compliance-specific entities
    Specialized for UK financial, data protection, and tax regulations
    """

    def __init__(self):
        self.patterns = self._build_patterns()
        self.entity_dictionaries = self._build_dictionaries()
        self._init_spacy_model()

    def _init_spacy_model(self):
        """Initialize spaCy model if available"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model for entity recognition")
        except (ImportError, OSError):
            logger.warning("spaCy not available. Using pattern-based extraction only.")
            self.nlp = None

    def _build_patterns(self) -> Dict[EntityType, List[re.Pattern]]:
        """Build regex patterns for entity extraction"""
        return {
            # FCA References
            EntityType.FCA_REFERENCE: [
                re.compile(r'\b(?:FCA\s+)?(?:COBS|SYSC|DISP|CASS|PRIN|TC|SUP|DEPP)\s+\d+(?:\.\d+)*\b', re.IGNORECASE),
                re.compile(r'\bFCA\s+Handbook\b', re.IGNORECASE),
                re.compile(r'\bConsumer\s+Duty\b', re.IGNORECASE),
                re.compile(r'\bSenior\s+Managers?\s+(?:&|and)\s+Certification\s+Regime\b', re.IGNORECASE),
                re.compile(r'\bSMCR\b'),
            ],

            # GDPR Articles
            EntityType.GDPR_ARTICLE: [
                re.compile(r'\bGDPR\s+Article\s+\d+(?:\(\d+\))?(?:\([a-z]\))?\b', re.IGNORECASE),
                re.compile(r'\bArticle\s+\d+\s+GDPR\b', re.IGNORECASE),
                re.compile(r'\b(?:UK\s+)?GDPR\b', re.IGNORECASE),
                re.compile(r'\bData\s+Protection\s+Act\s+2018\b', re.IGNORECASE),
                re.compile(r'\bPECR\b'),  # Privacy and Electronic Communications Regulations
            ],

            # UK Laws
            EntityType.UK_LAW: [
                re.compile(r'\b(?:Employment\s+Rights\s+Act|ERA)\s+1996\b', re.IGNORECASE),
                re.compile(r'\bEquality\s+Act\s+2010\b', re.IGNORECASE),
                re.compile(r'\bPublic\s+Interest\s+Disclosure\s+Act\s+1998\b', re.IGNORECASE),
                re.compile(r'\bEmployment\s+Relations\s+Act\s+1999\b', re.IGNORECASE),
                re.compile(r'\bFinancial\s+Services\s+and\s+Markets\s+Act\s+\d{4}\b', re.IGNORECASE),
                re.compile(r'\bFSMA\s+\d{4}\b', re.IGNORECASE),
            ],

            # HMRC References
            EntityType.HMRC_REFERENCE: [
                re.compile(r'\b(?:CT600|SA100|P11D|P60|P45)\b'),
                re.compile(r'\bMaking\s+Tax\s+Digital\b', re.IGNORECASE),
                re.compile(r'\bMTD\b'),
                re.compile(r'\bPAYE\b'),
                re.compile(r'\bCIS\b(?:\s+(?:scheme|deduction))?', re.IGNORECASE),
                re.compile(r'\bRTI\b(?:\s+return)?', re.IGNORECASE),
            ],

            # Financial Terms
            EntityType.FINANCIAL_TERM: [
                re.compile(r'\b(?:investment|portfolio|returns?|yield|dividend|equity|bond|fund|asset)\b', re.IGNORECASE),
                re.compile(r'\b(?:risk-adjusted|volatility|liquidity|capital|leverage)\b', re.IGNORECASE),
                re.compile(r'\bISA\b'),
                re.compile(r'\b(?:SIPP|pension)\b', re.IGNORECASE),
            ],

            # Data Protection Terms
            EntityType.DATA_TERM: [
                re.compile(r'\b(?:personal\s+data|data\s+subject|data\s+controller|data\s+processor)\b', re.IGNORECASE),
                re.compile(r'\b(?:consent|lawful\s+basis|legitimate\s+interests?)\b', re.IGNORECASE),
                re.compile(r'\b(?:right\s+to\s+(?:erasure|rectification|portability|object))\b', re.IGNORECASE),
                re.compile(r'\b(?:data\s+breach|breach\s+notification)\b', re.IGNORECASE),
            ],

            # Tax Terms
            EntityType.TAX_TERM: [
                re.compile(r'\b(?:VAT|corporation\s+tax|income\s+tax|national\s+insurance)\b', re.IGNORECASE),
                re.compile(r'\b(?:dividend\s+tax|capital\s+gains\s+tax|CGT)\b', re.IGNORECASE),
                re.compile(r'\b(?:allowable\s+expense|tax\s+relief|deduction)\b', re.IGNORECASE),
                re.compile(r'\b(?:self-assessment|tax\s+return)\b', re.IGNORECASE),
            ],

            # Company Numbers
            EntityType.COMPANY_NUMBER: [
                re.compile(r'\b(?:Company\s+(?:No\.?|Number):?\s*)?([A-Z]{2})?(\d{6,8})\b', re.IGNORECASE),
                re.compile(r'\bregistered\s+(?:company\s+)?number:?\s*([A-Z]{2})?(\d{6,8})\b', re.IGNORECASE),
            ],

            # FRN (Financial Services Register Number)
            EntityType.FRN: [
                re.compile(r'\bFRN:?\s*(\d{6})\b', re.IGNORECASE),
                re.compile(r'\bFirm\s+Reference\s+Number:?\s*(\d{6})\b', re.IGNORECASE),
            ],

            # VAT Numbers
            EntityType.VAT_NUMBER: [
                re.compile(r'\bVAT\s+(?:No\.?|Number|Registration):?\s*(GB\s*\d{9}(?:\s*\d{3})?)\b', re.IGNORECASE),
                re.compile(r'\b(GB\s*\d{9}(?:\s*\d{3})?)\b'),
            ],

            # Amounts
            EntityType.AMOUNT: [
                re.compile(r'£\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'),
                re.compile(r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:pounds?|GBP)\b', re.IGNORECASE),
            ],

            # Dates
            EntityType.DATE: [
                re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
                re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b', re.IGNORECASE),
                re.compile(r'\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b', re.IGNORECASE),
            ],

            # Percentages
            EntityType.PERCENTAGE: [
                re.compile(r'\b\d+(?:\.\d+)?%'),
                re.compile(r'\b\d+(?:\.\d+)?\s*percent\b', re.IGNORECASE),
            ],
        }

    def _build_dictionaries(self) -> Dict[EntityType, Set[str]]:
        """Build dictionaries of known entities"""
        return {
            EntityType.FINANCIAL_TERM: {
                'fca', 'financial conduct authority', 'pra', 'prudential regulation authority',
                'financial ombudsman service', 'fos', 'fscs', 'financial services compensation scheme',
                'mifid', 'cobs', 'cass', 'sysc', 'prin', 'disp', 'consumer duty',
                'smcr', 'senior managers regime', 'certification regime',
            },

            EntityType.GDPR_ARTICLE: {
                'gdpr', 'uk gdpr', 'data protection act 2018', 'dpa 2018', 'ico',
                'information commissioner', 'pecr', 'privacy and electronic communications',
            },

            EntityType.TAX_TERM: {
                'hmrc', 'her majesty\'s revenue and customs', 'vat', 'paye', 'cis',
                'construction industry scheme', 'making tax digital', 'mtd',
                'corporation tax', 'self-assessment', 'rti', 'real time information',
            },
        }

    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract all entities from text

        Args:
            text: Text to analyze

        Returns:
            List of recognized entities
        """
        entities = []

        # Pattern-based extraction
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    entity = Entity(
                        text=match.group(0),
                        entity_type=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9,  # High confidence for pattern matches
                        metadata={'pattern': pattern.pattern}
                    )
                    entities.append(entity)

        # spaCy-based extraction (if available)
        if self.nlp:
            try:
                doc = self.nlp(text)

                # Extract named entities
                for ent in doc.ents:
                    # Map spaCy entity types to our types
                    entity_type = self._map_spacy_entity(ent.label_)
                    if entity_type:
                        entity = Entity(
                            text=ent.text,
                            entity_type=entity_type,
                            start=ent.start_char,
                            end=ent.end_char,
                            confidence=0.8,
                            metadata={'spacy_label': ent.label_}
                        )
                        entities.append(entity)

            except Exception as e:
                logger.error(f"spaCy extraction error: {e}")

        # Remove duplicates and overlaps
        entities = self._deduplicate_entities(entities)

        return entities

    def _map_spacy_entity(self, label: str) -> Optional[EntityType]:
        """Map spaCy entity labels to our entity types"""
        mapping = {
            'ORG': EntityType.LEGAL_TERM,
            'MONEY': EntityType.AMOUNT,
            'DATE': EntityType.DATE,
            'PERCENT': EntityType.PERCENTAGE,
            'LAW': EntityType.UK_LAW,
        }
        return mapping.get(label)

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate and overlapping entities, keeping highest confidence"""
        if not entities:
            return []

        # Sort by start position
        entities.sort(key=lambda e: (e.start, -e.confidence))

        deduplicated = []
        last_end = -1

        for entity in entities:
            # Skip if overlaps with previous entity
            if entity.start < last_end:
                continue

            deduplicated.append(entity)
            last_end = entity.end

        return deduplicated

    def get_entities_by_type(self, entities: List[Entity], entity_type: EntityType) -> List[Entity]:
        """Filter entities by type"""
        return [e for e in entities if e.entity_type == entity_type]

    def has_entity_type(self, text: str, entity_type: EntityType) -> bool:
        """Check if text contains entities of specific type"""
        entities = self.extract_entities(text)
        return any(e.entity_type == entity_type for e in entities)

    def extract_regulatory_references(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all regulatory references organized by type

        Args:
            text: Text to analyze

        Returns:
            Dict of {reference_type: [references]}
        """
        entities = self.extract_entities(text)

        references = {
            'fca': [],
            'gdpr': [],
            'hmrc': [],
            'uk_law': [],
        }

        for entity in entities:
            if entity.entity_type == EntityType.FCA_REFERENCE:
                references['fca'].append(entity.text)
            elif entity.entity_type == EntityType.GDPR_ARTICLE:
                references['gdpr'].append(entity.text)
            elif entity.entity_type == EntityType.HMRC_REFERENCE:
                references['hmrc'].append(entity.text)
            elif entity.entity_type == EntityType.UK_LAW:
                references['uk_law'].append(entity.text)

        return references

    def validate_company_number(self, company_number: str) -> bool:
        """Validate UK company number format"""
        # UK company numbers are 6-8 digits, optionally prefixed with 2 letters
        pattern = r'^([A-Z]{2})?\d{6,8}$'
        return bool(re.match(pattern, company_number.upper().replace(' ', '')))

    def validate_vat_number(self, vat_number: str) -> bool:
        """Validate UK VAT number format"""
        # UK VAT: GB + 9 digits or GB + 12 digits
        cleaned = vat_number.upper().replace(' ', '')
        return bool(re.match(r'^GB\d{9}(\d{3})?$', cleaned))

    def validate_frn(self, frn: str) -> bool:
        """Validate FCA Firm Reference Number"""
        # FRN is typically 6 digits
        return bool(re.match(r'^\d{6}$', frn.replace(' ', '')))


# Singleton instance
_entity_recognizer_instance = None

def get_entity_recognizer() -> EntityRecognizer:
    """Get singleton entity recognizer instance"""
    global _entity_recognizer_instance
    if _entity_recognizer_instance is None:
        _entity_recognizer_instance = EntityRecognizer()
    return _entity_recognizer_instance
