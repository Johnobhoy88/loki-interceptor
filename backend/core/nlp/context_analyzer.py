"""
Context Analyzer - Understand surrounding text for better pattern matching
Provides context-aware corrections by analyzing sentence structure, paragraphs, and document flow
"""

import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context"""
    FINANCIAL = "financial"
    DATA_PROTECTION = "data_protection"
    TAX = "tax"
    LEGAL = "legal"
    HR_EMPLOYMENT = "hr_employment"
    NDA = "nda"
    MARKETING = "marketing"
    TECHNICAL = "technical"


@dataclass
class ContextWindow:
    """Context window around a text position"""
    text: str
    start: int
    end: int
    sentences_before: List[str]
    sentences_after: List[str]
    paragraph: str
    document_section: str
    context_type: Optional[ContextType] = None


class ContextAnalyzer:
    """
    Analyze context around text patterns for intelligent corrections
    Understanding context helps avoid false positives and improve correction relevance
    """

    def __init__(self):
        self.context_indicators = self._build_context_indicators()
        self._init_nlp()

    def _init_nlp(self):
        """Initialize NLP tools"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy for context analysis")
        except (ImportError, OSError):
            logger.warning("spaCy not available. Using rule-based context analysis.")
            self.nlp = None

    def _build_context_indicators(self) -> Dict[ContextType, Dict[str, List[str]]]:
        """Build indicators for different context types"""
        return {
            ContextType.FINANCIAL: {
                'keywords': [
                    'investment', 'portfolio', 'returns', 'yield', 'dividend', 'equity',
                    'bond', 'fund', 'asset', 'risk', 'fca', 'financial conduct authority',
                    'cobs', 'mifid', 'consumer duty', 'financial promotion', 'advice'
                ],
                'phrases': [
                    'capital at risk', 'past performance', 'not guaranteed',
                    'financial advice', 'investment decision', 'risk warning'
                ]
            },

            ContextType.DATA_PROTECTION: {
                'keywords': [
                    'gdpr', 'data protection', 'personal data', 'privacy', 'consent',
                    'data subject', 'controller', 'processor', 'ico', 'dpa 2018'
                ],
                'phrases': [
                    'personal data', 'data protection', 'right to erasure',
                    'data breach', 'lawful basis', 'legitimate interest'
                ]
            },

            ContextType.TAX: {
                'keywords': [
                    'vat', 'hmrc', 'tax', 'corporation tax', 'income tax', 'paye',
                    'national insurance', 'cis', 'mtd', 'self-assessment', 'dividend tax'
                ],
                'phrases': [
                    'tax return', 'vat registration', 'allowable expense',
                    'tax relief', 'hmrc compliance', 'making tax digital'
                ]
            },

            ContextType.LEGAL: {
                'keywords': [
                    'contract', 'agreement', 'clause', 'liability', 'indemnity',
                    'warranty', 'governing law', 'jurisdiction', 'breach', 'termination'
                ],
                'phrases': [
                    'governing law', 'dispute resolution', 'force majeure',
                    'intellectual property', 'limitation of liability'
                ]
            },

            ContextType.HR_EMPLOYMENT: {
                'keywords': [
                    'employee', 'employment', 'disciplinary', 'grievance', 'dismissal',
                    'redundancy', 'tribunal', 'accompanied', 'era 1996', 'acas'
                ],
                'phrases': [
                    'right to be accompanied', 'disciplinary meeting', 'employment tribunal',
                    'unfair dismissal', 'notice period', 'gross misconduct'
                ]
            },

            ContextType.NDA: {
                'keywords': [
                    'confidential', 'nda', 'non-disclosure', 'proprietary', 'trade secret',
                    'confidentiality', 'disclosure', 'whistleblowing'
                ],
                'phrases': [
                    'confidential information', 'non-disclosure agreement',
                    'trade secret', 'proprietary information', 'permitted disclosure'
                ]
            }
        }

    def get_context_window(
        self,
        text: str,
        position: int,
        window_size: int = 200
    ) -> ContextWindow:
        """
        Get context window around a position

        Args:
            text: Full text
            position: Position to center window on
            window_size: Size of context window (characters before/after)

        Returns:
            ContextWindow with surrounding context
        """
        # Calculate window bounds
        start = max(0, position - window_size)
        end = min(len(text), position + window_size)

        window_text = text[start:end]

        # Extract sentences
        sentences = self._split_sentences(text)
        target_sentences_before = []
        target_sentences_after = []
        current_pos = 0

        for sentence in sentences:
            sentence_end = current_pos + len(sentence)

            if sentence_end < position:
                target_sentences_before.append(sentence)
            elif current_pos > position:
                target_sentences_after.append(sentence)

            current_pos = sentence_end + 1  # +1 for space/punctuation

        # Get last 2 sentences before and first 2 after
        sentences_before = target_sentences_before[-2:] if target_sentences_before else []
        sentences_after = target_sentences_after[:2] if target_sentences_after else []

        # Extract paragraph
        paragraph = self._extract_paragraph(text, position)

        # Determine document section
        section = self._determine_section(text, position)

        # Determine context type
        context_type = self.identify_context_type(window_text)

        return ContextWindow(
            text=window_text,
            start=start,
            end=end,
            sentences_before=sentences_before,
            sentences_after=sentences_after,
            paragraph=paragraph,
            document_section=section,
            context_type=context_type
        )

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if self.nlp:
            try:
                doc = self.nlp(text)
                return [sent.text.strip() for sent in doc.sents]
            except Exception as e:
                logger.error(f"spaCy sentence splitting error: {e}")

        # Fallback: Simple rule-based splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_paragraph(self, text: str, position: int) -> str:
        """Extract the paragraph containing the position"""
        # Find paragraph boundaries (double newline or significant spacing)
        paragraphs = re.split(r'\n\s*\n', text)

        current_pos = 0
        for paragraph in paragraphs:
            paragraph_end = current_pos + len(paragraph)
            if current_pos <= position <= paragraph_end:
                return paragraph.strip()
            current_pos = paragraph_end + 2  # +2 for \n\n

        return ""

    def _determine_section(self, text: str, position: int) -> str:
        """Determine which document section the position is in"""
        # Look for section headers before the position
        text_before = text[:position]

        # Common section patterns
        section_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Z\s]+):?\s*$',  # ALL CAPS headers
            r'^(\d+\.?\s+[A-Z].+)$',  # Numbered sections
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):?\s*$'  # Title Case headers
        ]

        lines = text_before.split('\n')
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    return match.group(1).strip()

        return "Unknown Section"

    def identify_context_type(self, text: str) -> Optional[ContextType]:
        """
        Identify the primary context type of text

        Args:
            text: Text to analyze

        Returns:
            Most likely ContextType or None
        """
        text_lower = text.lower()

        scores = {}
        for context_type, indicators in self.context_indicators.items():
            score = 0

            # Score keywords
            for keyword in indicators.get('keywords', []):
                if keyword.lower() in text_lower:
                    score += 1

            # Score phrases (higher weight)
            for phrase in indicators.get('phrases', []):
                if phrase.lower() in text_lower:
                    score += 2

            scores[context_type] = score

        # Return type with highest score (if > 0)
        if scores:
            max_type = max(scores, key=scores.get)
            if scores[max_type] > 0:
                return max_type

        return None

    def is_negated(self, text: str, position: int) -> bool:
        """
        Check if a pattern at position is negated

        Args:
            text: Full text
            position: Position of pattern

        Returns:
            True if pattern is negated
        """
        # Look for negation words before the pattern
        window_start = max(0, position - 50)
        context = text[window_start:position]

        negation_patterns = [
            r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bneither\b', r'\bnor\b',
            r'\bnobody\b', r'\bnothing\b', r'\bnowhere\b', r'\bwithout\b',
            r'\bcannot\b', r'\bcan\'t\b', r'\bwon\'t\b', r'\bshouldn\'t\b',
            r'\bmustn\'t\b', r'\bdidn\'t\b', r'\bdoesn\'t\b', r'\bdon\'t\b'
        ]

        for pattern in negation_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True

        return False

    def is_conditional(self, text: str, position: int) -> bool:
        """
        Check if pattern is in a conditional context

        Args:
            text: Full text
            position: Position of pattern

        Returns:
            True if pattern is conditional
        """
        window_start = max(0, position - 100)
        context = text[window_start:position]

        conditional_patterns = [
            r'\bif\b', r'\bunless\b', r'\bprovided\s+that\b', r'\bin\s+case\b',
            r'\bshould\b', r'\bwould\b', r'\bcould\b', r'\bmight\b', r'\bmay\b'
        ]

        for pattern in conditional_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True

        return False

    def is_in_quote(self, text: str, position: int) -> bool:
        """
        Check if position is inside a quote

        Args:
            text: Full text
            position: Position to check

        Returns:
            True if inside quote
        """
        # Count quotes before position
        text_before = text[:position]
        double_quotes = text_before.count('"') % 2 == 1
        single_quotes = text_before.count("'") % 2 == 1

        return double_quotes or single_quotes

    def get_sentence_sentiment(self, sentence: str) -> str:
        """
        Get sentiment of sentence (positive/negative/neutral)

        Args:
            sentence: Sentence to analyze

        Returns:
            Sentiment label
        """
        # Simple rule-based sentiment
        positive_words = ['good', 'great', 'excellent', 'benefit', 'advantage', 'positive', 'protect']
        negative_words = ['bad', 'poor', 'risk', 'loss', 'fail', 'breach', 'violation', 'penalty']

        sentence_lower = sentence.lower()

        positive_count = sum(1 for word in positive_words if word in sentence_lower)
        negative_count = sum(1 for word in negative_words if word in sentence_lower)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def analyze_pattern_context(
        self,
        text: str,
        pattern_match: re.Match,
        pattern_category: str
    ) -> Dict:
        """
        Comprehensive context analysis for a pattern match

        Args:
            text: Full text
            pattern_match: Regex match object
            pattern_category: Category of pattern (e.g., 'risk_warning')

        Returns:
            Dict with context analysis
        """
        position = pattern_match.start()
        matched_text = pattern_match.group(0)

        context_window = self.get_context_window(text, position)

        analysis = {
            'matched_text': matched_text,
            'position': position,
            'context_type': context_window.context_type,
            'document_section': context_window.document_section,
            'is_negated': self.is_negated(text, position),
            'is_conditional': self.is_conditional(text, position),
            'is_in_quote': self.is_in_quote(text, position),
            'sentences_before': context_window.sentences_before,
            'sentences_after': context_window.sentences_after,
            'paragraph': context_window.paragraph,
            'should_apply': True  # Default
        }

        # Determine if pattern should apply based on context
        analysis['should_apply'] = self._should_apply_pattern(
            pattern_category,
            analysis
        )

        return analysis

    def _should_apply_pattern(
        self,
        pattern_category: str,
        context_analysis: Dict
    ) -> bool:
        """
        Determine if a pattern should apply given the context

        Args:
            pattern_category: Category of pattern
            context_analysis: Context analysis dict

        Returns:
            True if pattern should apply
        """
        # Don't apply if negated (e.g., "not a risk-free investment" - already correct)
        if context_analysis['is_negated']:
            return False

        # Don't apply if in quotes (might be discussing the phrase, not using it)
        if context_analysis['is_in_quote']:
            return False

        # Apply conditionals carefully
        if context_analysis['is_conditional'] and pattern_category in ['risk_warning', 'fair_clear']:
            # Conditional statements may be fine in certain contexts
            return True

        return True

    def find_coreferences(self, text: str) -> List[Dict]:
        """
        Find coreferences (pronouns referring to earlier entities)

        Args:
            text: Text to analyze

        Returns:
            List of coreference chains
        """
        if not self.nlp:
            return []

        # Note: Basic coreference resolution requires neuralcoref or similar
        # This is a placeholder for the functionality
        logger.warning("Advanced coreference resolution requires additional models")
        return []

    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract key phrases from text

        Args:
            text: Text to analyze
            top_n: Number of key phrases to return

        Returns:
            List of (phrase, score) tuples
        """
        if not self.nlp:
            # Simple fallback: most common noun phrases
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            from collections import Counter
            counts = Counter(words)
            return [(phrase, count) for phrase, count in counts.most_common(top_n)]

        try:
            doc = self.nlp(text)

            # Extract noun chunks
            phrases = {}
            for chunk in doc.noun_chunks:
                phrase = chunk.text.lower()
                phrases[phrase] = phrases.get(phrase, 0) + 1

            # Sort by frequency
            sorted_phrases = sorted(phrases.items(), key=lambda x: x[1], reverse=True)
            return sorted_phrases[:top_n]

        except Exception as e:
            logger.error(f"Key phrase extraction error: {e}")
            return []


# Singleton instance
_context_analyzer_instance = None

def get_context_analyzer() -> ContextAnalyzer:
    """Get singleton context analyzer instance"""
    global _context_analyzer_instance
    if _context_analyzer_instance is None:
        _context_analyzer_instance = ContextAnalyzer()
    return _context_analyzer_instance
