"""
Sentiment Analyzer - Tone compliance and sentiment analysis
Ensures regulatory documents maintain appropriate tone (professional, clear, not misleading)
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToneType(Enum):
    """Document tone types"""
    PROFESSIONAL = "professional"
    AGGRESSIVE = "aggressive"
    MISLEADING = "misleading"
    COERCIVE = "coercive"
    FEARFUL = "fearful"
    OVERPROMISING = "overpromising"
    NEUTRAL = "neutral"
    EDUCATIONAL = "educational"
    WARNING = "warning"


@dataclass
class SentimentAnalysis:
    """Sentiment analysis results"""
    overall_sentiment: str  # positive, negative, neutral
    confidence: float
    tone_type: ToneType
    polarity_score: float  # -1 (negative) to +1 (positive)
    subjectivity_score: float  # 0 (objective) to 1 (subjective)

    # Compliance-specific scores
    urgency_score: float
    fear_score: float
    hype_score: float
    coercion_score: float

    # Flags
    is_misleading: bool
    is_coercive: bool
    is_overpromising: bool
    is_compliant_tone: bool

    # Details
    flagged_phrases: List[str]
    suggestions: List[str]


class SentimentAnalyzer:
    """
    Analyze sentiment and tone for regulatory compliance
    Specialized for FCA Consumer Duty and fair communication requirements
    """

    def __init__(self):
        self.lexicons = self._build_lexicons()
        self._init_models()

    def _init_models(self):
        """Initialize sentiment models if available"""
        try:
            from textblob import TextBlob
            self.textblob_available = True
            logger.info("TextBlob available for sentiment analysis")
        except ImportError:
            self.textblob_available = False
            logger.warning("TextBlob not available. Using rule-based sentiment only.")

    def _build_lexicons(self) -> Dict[str, Dict[str, List[str]]]:
        """Build sentiment and tone lexicons"""
        return {
            'positive': {
                'financial': [
                    'benefit', 'advantage', 'protect', 'secure', 'gain', 'profit',
                    'opportunity', 'growth', 'return', 'reward', 'success'
                ],
                'general': [
                    'good', 'great', 'excellent', 'outstanding', 'superior',
                    'effective', 'reliable', 'trusted', 'proven', 'quality'
                ]
            },

            'negative': {
                'risk': [
                    'risk', 'loss', 'decline', 'fall', 'drop', 'penalty',
                    'breach', 'violation', 'fail', 'damage', 'harm'
                ],
                'general': [
                    'bad', 'poor', 'weak', 'inferior', 'inadequate',
                    'disappointing', 'unsatisfactory', 'problematic'
                ]
            },

            'misleading': {
                'guarantees': [
                    'guaranteed', 'certain', 'sure', 'definite', 'promise',
                    'assure', 'no risk', 'risk-free', 'safe investment', 'cant lose',
                    'no chance of loss', 'zero risk'
                ],
                'hype': [
                    'amazing', 'incredible', 'unbelievable', 'revolutionary',
                    'once in a lifetime', 'unique opportunity', 'limited time',
                    'act now', 'dont miss out', 'secret', 'exclusive deal'
                ]
            },

            'coercive': {
                'urgency': [
                    'must', 'required', 'mandatory', 'compulsory', 'obligation',
                    'immediately', 'urgent', 'act now', 'hurry', 'running out',
                    'last chance', 'deadline approaching', 'time sensitive'
                ],
                'pressure': [
                    'you should', 'you must', 'you need to', 'dont wait',
                    'act fast', 'limited availability', 'only a few left',
                    'pressure', 'force', 'require'
                ]
            },

            'fearful': {
                'threats': [
                    'lose out', 'miss out', 'regret', 'behind', 'penalty',
                    'consequences', 'prosecution', 'arrest', 'legal action',
                    'enforcement', 'punishment', 'suffer'
                ],
                'anxiety': [
                    'worry', 'concern', 'fear', 'anxious', 'nervous',
                    'uncertain', 'insecure', 'vulnerable', 'exposed'
                ]
            },

            'overpromising': {
                'exaggeration': [
                    'best', 'highest', 'maximum', 'optimal', 'perfect',
                    'ultimate', 'supreme', 'unmatched', 'unbeatable', 'number one'
                ],
                'unrealistic': [
                    'double your money', 'triple returns', 'exponential growth',
                    'sky high', 'unlimited', 'infinite', 'massive returns',
                    'get rich', 'wealthy', 'millionaire'
                ]
            },

            'professional': {
                'clear': [
                    'clear', 'transparent', 'straightforward', 'simple',
                    'plain', 'accessible', 'understandable', 'explain'
                ],
                'balanced': [
                    'balanced', 'fair', 'objective', 'reasonable',
                    'appropriate', 'suitable', 'proportionate'
                ]
            }
        }

    def calculate_polarity(self, text: str) -> float:
        """
        Calculate sentiment polarity (-1 to +1)

        Args:
            text: Text to analyze

        Returns:
            Polarity score
        """
        if self.textblob_available:
            try:
                from textblob import TextBlob
                blob = TextBlob(text)
                return blob.sentiment.polarity
            except Exception as e:
                logger.error(f"TextBlob polarity error: {e}")

        # Fallback: Rule-based polarity
        text_lower = text.lower()

        positive_count = 0
        for category in self.lexicons['positive'].values():
            positive_count += sum(1 for word in category if word in text_lower)

        negative_count = 0
        for category in self.lexicons['negative'].values():
            negative_count += sum(1 for word in category if word in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        polarity = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, polarity))

    def calculate_subjectivity(self, text: str) -> float:
        """
        Calculate subjectivity (0 to 1)

        Args:
            text: Text to analyze

        Returns:
            Subjectivity score
        """
        if self.textblob_available:
            try:
                from textblob import TextBlob
                blob = TextBlob(text)
                return blob.sentiment.subjectivity
            except Exception as e:
                logger.error(f"TextBlob subjectivity error: {e}")

        # Fallback: Count subjective words
        text_lower = text.lower()

        subjective_patterns = [
            r'\b(?:i think|i believe|in my opinion|seems|appears|probably|perhaps|maybe)\b',
            r'\b(?:amazing|terrible|wonderful|awful|excellent|poor)\b',
            r'\b(?:very|extremely|highly|incredibly|absolutely)\b'
        ]

        subjective_count = sum(
            len(re.findall(pattern, text_lower))
            for pattern in subjective_patterns
        )

        words = len(text.split())
        if words == 0:
            return 0.0

        return min(1.0, subjective_count / (words / 10))

    def detect_misleading_language(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect misleading language (FCA COBS 4.2.1 - Fair, Clear, Not Misleading)

        Args:
            text: Text to analyze

        Returns:
            (is_misleading, flagged_phrases)
        """
        text_lower = text.lower()
        flagged = []

        for category, words in self.lexicons['misleading'].items():
            for word in words:
                if word in text_lower:
                    # Find actual phrase in text
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    matches = pattern.findall(text)
                    flagged.extend(matches)

        return len(flagged) > 0, flagged

    def detect_coercive_language(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect coercive language (FCA Consumer Duty - Act in Good Faith)

        Args:
            text: Text to analyze

        Returns:
            (is_coercive, flagged_phrases)
        """
        text_lower = text.lower()
        flagged = []

        for category, words in self.lexicons['coercive'].items():
            for word in words:
                if word in text_lower:
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    matches = pattern.findall(text)
                    flagged.extend(matches)

        return len(flagged) > 2, flagged  # Threshold: 3+ coercive terms

    def detect_overpromising(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect overpromising language

        Args:
            text: Text to analyze

        Returns:
            (is_overpromising, flagged_phrases)
        """
        text_lower = text.lower()
        flagged = []

        for category, words in self.lexicons['overpromising'].items():
            for word in words:
                if word in text_lower:
                    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                    matches = pattern.findall(text)
                    flagged.extend(matches)

        return len(flagged) > 1, flagged  # Threshold: 2+ overpromising terms

    def calculate_urgency_score(self, text: str) -> float:
        """
        Calculate urgency/pressure score (0-1)

        Args:
            text: Text to analyze

        Returns:
            Urgency score
        """
        text_lower = text.lower()

        urgency_words = self.lexicons['coercive']['urgency']
        count = sum(1 for word in urgency_words if word in text_lower)

        words = len(text.split())
        if words == 0:
            return 0.0

        # Normalize to 0-1
        return min(1.0, count / (words / 50))  # 1 urgency word per 50 words = 1.0

    def calculate_fear_score(self, text: str) -> float:
        """
        Calculate fear/anxiety score (0-1)

        Args:
            text: Text to analyze

        Returns:
            Fear score
        """
        text_lower = text.lower()

        fear_count = 0
        for category in self.lexicons['fearful'].values():
            fear_count += sum(1 for word in category if word in text_lower)

        words = len(text.split())
        if words == 0:
            return 0.0

        return min(1.0, fear_count / (words / 50))

    def calculate_hype_score(self, text: str) -> float:
        """
        Calculate hype/exaggeration score (0-1)

        Args:
            text: Text to analyze

        Returns:
            Hype score
        """
        text_lower = text.lower()

        hype_words = self.lexicons['misleading']['hype'] + \
                     self.lexicons['overpromising']['exaggeration']

        count = sum(1 for word in hype_words if word in text_lower)

        words = len(text.split())
        if words == 0:
            return 0.0

        return min(1.0, count / (words / 30))

    def determine_tone(self, text: str) -> ToneType:
        """
        Determine overall tone type

        Args:
            text: Text to analyze

        Returns:
            ToneType
        """
        text_lower = text.lower()

        # Count indicators for each tone
        scores = {}

        # Professional tone
        professional_count = sum(
            sum(1 for word in words if word in text_lower)
            for words in self.lexicons['professional'].values()
        )
        scores[ToneType.PROFESSIONAL] = professional_count

        # Aggressive/coercive tone
        coercive_count = sum(
            sum(1 for word in words if word in text_lower)
            for words in self.lexicons['coercive'].values()
        )
        scores[ToneType.COERCIVE] = coercive_count

        # Misleading tone
        misleading_count = sum(
            sum(1 for word in words if word in text_lower)
            for words in self.lexicons['misleading'].values()
        )
        scores[ToneType.MISLEADING] = misleading_count

        # Fearful tone
        fearful_count = sum(
            sum(1 for word in words if word in text_lower)
            for words in self.lexicons['fearful'].values()
        )
        scores[ToneType.FEARFUL] = fearful_count

        # Overpromising tone
        overpromising_count = sum(
            sum(1 for word in words if word in text_lower)
            for words in self.lexicons['overpromising'].values()
        )
        scores[ToneType.OVERPROMISING] = overpromising_count

        # Warning tone (risk warnings present)
        if re.search(r'\b(?:warning|risk|capital at risk|may lose)\b', text_lower):
            scores[ToneType.WARNING] = 5

        # Determine dominant tone
        if max(scores.values()) == 0:
            return ToneType.NEUTRAL

        return max(scores, key=scores.get)

    def analyze(self, text: str) -> SentimentAnalysis:
        """
        Comprehensive sentiment and tone analysis

        Args:
            text: Text to analyze

        Returns:
            SentimentAnalysis with all metrics
        """
        # Calculate basic sentiment
        polarity = self.calculate_polarity(text)
        subjectivity = self.calculate_subjectivity(text)

        # Determine overall sentiment
        if polarity > 0.1:
            overall_sentiment = 'positive'
            confidence = abs(polarity)
        elif polarity < -0.1:
            overall_sentiment = 'negative'
            confidence = abs(polarity)
        else:
            overall_sentiment = 'neutral'
            confidence = 1.0 - abs(polarity)

        # Determine tone
        tone_type = self.determine_tone(text)

        # Compliance checks
        is_misleading, misleading_phrases = self.detect_misleading_language(text)
        is_coercive, coercive_phrases = self.detect_coercive_language(text)
        is_overpromising, overpromising_phrases = self.detect_overpromising(text)

        # Scores
        urgency_score = self.calculate_urgency_score(text)
        fear_score = self.calculate_fear_score(text)
        hype_score = self.calculate_hype_score(text)
        coercion_score = urgency_score * 0.6 + fear_score * 0.4

        # Compliance determination
        is_compliant_tone = not (is_misleading or is_coercive or is_overpromising)

        # Collect all flagged phrases
        flagged_phrases = list(set(
            misleading_phrases + coercive_phrases + overpromising_phrases
        ))

        # Generate suggestions
        suggestions = self._generate_suggestions(
            is_misleading, is_coercive, is_overpromising,
            urgency_score, fear_score, hype_score, tone_type
        )

        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            confidence=round(confidence, 3),
            tone_type=tone_type,
            polarity_score=round(polarity, 3),
            subjectivity_score=round(subjectivity, 3),
            urgency_score=round(urgency_score, 3),
            fear_score=round(fear_score, 3),
            hype_score=round(hype_score, 3),
            coercion_score=round(coercion_score, 3),
            is_misleading=is_misleading,
            is_coercive=is_coercive,
            is_overpromising=is_overpromising,
            is_compliant_tone=is_compliant_tone,
            flagged_phrases=flagged_phrases,
            suggestions=suggestions
        )

    def _generate_suggestions(
        self,
        is_misleading: bool,
        is_coercive: bool,
        is_overpromising: bool,
        urgency_score: float,
        fear_score: float,
        hype_score: float,
        tone_type: ToneType
    ) -> List[str]:
        """Generate tone improvement suggestions"""
        suggestions = []

        if is_misleading:
            suggestions.append(
                "MISLEADING LANGUAGE: Remove guarantees and absolute promises. "
                "FCA COBS 4.2.1 requires communications to be fair, clear, and not misleading."
            )

        if is_coercive:
            suggestions.append(
                "COERCIVE LANGUAGE: Remove pressure tactics and mandatory language. "
                "FCA Consumer Duty requires acting in good faith without foreseeable harm."
            )

        if is_overpromising:
            suggestions.append(
                "OVERPROMISING: Avoid unrealistic claims and exaggerations. "
                "Provide balanced information about outcomes."
            )

        if urgency_score > 0.5:
            suggestions.append(
                "HIGH URGENCY: Reduce time pressure and urgency language. "
                "Allow customers time to make informed decisions."
            )

        if fear_score > 0.3:
            suggestions.append(
                "FEAR-BASED LANGUAGE: Avoid inducing anxiety or fear. "
                "Use neutral, informative language."
            )

        if hype_score > 0.4:
            suggestions.append(
                "EXCESSIVE HYPE: Tone down marketing language. "
                "Use factual, substantiated statements."
            )

        if tone_type == ToneType.AGGRESSIVE:
            suggestions.append(
                "AGGRESSIVE TONE: Adopt a more professional, balanced tone. "
                "Ensure communications are customer-friendly."
            )

        if tone_type == ToneType.PROFESSIONAL:
            suggestions.append(
                "TONE COMPLIANT: Professional and appropriate tone for regulatory communications."
            )

        if not suggestions:
            suggestions.append(
                "Tone analysis complete. Consider balancing promotional content with risk warnings."
            )

        return suggestions

    def is_fca_compliant_tone(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check if tone meets FCA compliance standards

        Args:
            text: Text to check

        Returns:
            (is_compliant, issues)
        """
        analysis = self.analyze(text)

        issues = []

        if analysis.is_misleading:
            issues.append("Contains misleading language (FCA COBS 4.2.1)")

        if analysis.is_coercive:
            issues.append("Contains coercive language (Consumer Duty)")

        if analysis.is_overpromising:
            issues.append("Contains overpromising language")

        if analysis.urgency_score > 0.6:
            issues.append("Excessive urgency/pressure tactics")

        if analysis.hype_score > 0.5:
            issues.append("Excessive marketing hype")

        return len(issues) == 0, issues


# Singleton instance
_sentiment_analyzer_instance = None

def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get singleton sentiment analyzer instance"""
    global _sentiment_analyzer_instance
    if _sentiment_analyzer_instance is None:
        _sentiment_analyzer_instance = SentimentAnalyzer()
    return _sentiment_analyzer_instance
