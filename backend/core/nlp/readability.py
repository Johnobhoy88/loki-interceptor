"""
Readability Scorer - Assess and improve document readability
Implements Flesch-Kincaid, SMOG, Gunning Fog, and UK-specific readability metrics
"""

import re
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ReadabilityScores:
    """Container for all readability scores"""
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog: float
    smog_index: float
    coleman_liau_index: float
    automated_readability_index: float
    dale_chall_score: float

    # Counts
    sentence_count: int
    word_count: int
    syllable_count: int
    complex_word_count: int
    avg_sentence_length: float
    avg_syllables_per_word: float

    # UK-specific metrics
    legal_jargon_count: int
    passive_voice_count: int
    long_sentence_count: int

    # Overall assessment
    grade_level: str
    readability_rating: str
    suggestions: List[str]


class ReadabilityScorer:
    """
    Comprehensive readability scoring for compliance documents
    Optimized for UK English and regulatory content
    """

    def __init__(self):
        self.dale_chall_words = self._load_dale_chall_words()
        self.legal_jargon = self._load_legal_jargon()

    def _load_dale_chall_words(self) -> set:
        """Load Dale-Chall easy words list (simplified version)"""
        # This is a subset - full list contains ~3000 words
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
            'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were', 'said', 'did',
            # UK specific common words
            'whilst', 'towards', 'colour', 'favour', 'honour', 'labour', 'behaviour'
        }
        return common_words

    def _load_legal_jargon(self) -> List[str]:
        """Load list of legal/regulatory jargon terms"""
        return [
            'aforementioned', 'herein', 'thereof', 'whereby', 'hereinafter', 'heretofore',
            'notwithstanding', 'pursuant', 'aforethought', 'aforesaid', 'wheresoever',
            'howsoever', 'therein', 'thereto', 'therefrom', 'hereunder', 'herewith',
            'indemnify', 'indemnification', 'subrogation', 'waiver', 'severability'
        ]

    def count_syllables(self, word: str) -> int:
        """
        Count syllables in a word (English approximation)

        Args:
            word: Word to count syllables in

        Returns:
            Number of syllables
        """
        word = word.lower().strip()

        # Remove common endings
        word = re.sub(r'(es|ed|e)$', '', word)

        # Count vowel groups
        syllables = len(re.findall(r'[aeiouy]+', word))

        # Adjust for common patterns
        if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
            syllables += 1

        # Minimum 1 syllable
        return max(1, syllables)

    def count_complex_words(self, words: List[str]) -> int:
        """
        Count complex words (3+ syllables, excluding proper nouns, familiar jargon, compounds)

        Args:
            words: List of words

        Returns:
            Count of complex words
        """
        complex_count = 0
        for word in words:
            # Skip short words
            if len(word) <= 3:
                continue

            # Skip proper nouns (capitalized)
            if word[0].isupper() and word not in ['I', 'A']:
                continue

            # Skip common compound words
            if '-' in word or word.endswith('ing') or word.endswith('ed'):
                continue

            syllables = self.count_syllables(word)
            if syllables >= 3:
                complex_count += 1

        return complex_count

    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Handle common abbreviations that shouldn't split
        text = re.sub(r'\bMr\.', 'Mr', text)
        text = re.sub(r'\bMrs\.', 'Mrs', text)
        text = re.sub(r'\bDr\.', 'Dr', text)
        text = re.sub(r'\bProf\.', 'Prof', text)
        text = re.sub(r'\bi\.e\.', 'ie', text)
        text = re.sub(r'\be\.g\.', 'eg', text)

        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def tokenize_words(self, text: str) -> List[str]:
        """
        Extract words from text

        Args:
            text: Text to tokenize

        Returns:
            List of words
        """
        # Remove punctuation and split
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return words

    def flesch_reading_ease(
        self,
        total_words: int,
        total_sentences: int,
        total_syllables: int
    ) -> float:
        """
        Calculate Flesch Reading Ease score
        Score ranges: 90-100 (very easy) to 0-30 (very difficult)

        Args:
            total_words: Total word count
            total_sentences: Total sentence count
            total_syllables: Total syllable count

        Returns:
            Flesch Reading Ease score
        """
        if total_words == 0 or total_sentences == 0:
            return 0.0

        asl = total_words / total_sentences  # Average sentence length
        asw = total_syllables / total_words  # Average syllables per word

        score = 206.835 - (1.015 * asl) - (84.6 * asw)
        return round(score, 2)

    def flesch_kincaid_grade(
        self,
        total_words: int,
        total_sentences: int,
        total_syllables: int
    ) -> float:
        """
        Calculate Flesch-Kincaid Grade Level
        Indicates US school grade level needed to understand text

        Args:
            total_words: Total word count
            total_sentences: Total sentence count
            total_syllables: Total syllable count

        Returns:
            Grade level (0-18+)
        """
        if total_words == 0 or total_sentences == 0:
            return 0.0

        asl = total_words / total_sentences
        asw = total_syllables / total_words

        grade = (0.39 * asl) + (11.8 * asw) - 15.59
        return round(grade, 2)

    def gunning_fog_index(
        self,
        total_words: int,
        total_sentences: int,
        complex_words: int
    ) -> float:
        """
        Calculate Gunning Fog Index
        Estimates years of education needed to understand text

        Args:
            total_words: Total word count
            total_sentences: Total sentence count
            complex_words: Count of complex words (3+ syllables)

        Returns:
            Fog index (grade level)
        """
        if total_words == 0 or total_sentences == 0:
            return 0.0

        asl = total_words / total_sentences
        pcw = (complex_words / total_words) * 100

        fog = 0.4 * (asl + pcw)
        return round(fog, 2)

    def smog_index(
        self,
        total_sentences: int,
        complex_words: int
    ) -> float:
        """
        Calculate SMOG (Simple Measure of Gobbledygook) Index
        Estimates years of education needed

        Args:
            total_sentences: Total sentence count (minimum 30 for accuracy)
            complex_words: Count of polysyllabic words

        Returns:
            SMOG grade level
        """
        if total_sentences == 0:
            return 0.0

        # SMOG formula
        smog = 1.0430 * math.sqrt(complex_words * (30 / total_sentences)) + 3.1291
        return round(smog, 2)

    def coleman_liau_index(
        self,
        total_words: int,
        total_sentences: int,
        total_letters: int
    ) -> float:
        """
        Calculate Coleman-Liau Index
        Based on characters rather than syllables

        Args:
            total_words: Total word count
            total_sentences: Total sentence count
            total_letters: Total letter count

        Returns:
            Grade level
        """
        if total_words == 0:
            return 0.0

        l = (total_letters / total_words) * 100  # Average letters per 100 words
        s = (total_sentences / total_words) * 100  # Average sentences per 100 words

        cli = (0.0588 * l) - (0.296 * s) - 15.8
        return round(cli, 2)

    def automated_readability_index(
        self,
        total_words: int,
        total_sentences: int,
        total_characters: int
    ) -> float:
        """
        Calculate Automated Readability Index (ARI)

        Args:
            total_words: Total word count
            total_sentences: Total sentence count
            total_characters: Total character count

        Returns:
            Grade level
        """
        if total_words == 0 or total_sentences == 0:
            return 0.0

        ari = (4.71 * (total_characters / total_words)) + \
              (0.5 * (total_words / total_sentences)) - 21.43

        return round(ari, 2)

    def dale_chall_readability(
        self,
        total_words: int,
        total_sentences: int,
        difficult_words: int
    ) -> float:
        """
        Calculate Dale-Chall Readability Score
        Based on familiar vs unfamiliar words

        Args:
            total_words: Total word count
            total_sentences: Total sentence count
            difficult_words: Count of words not in Dale-Chall easy word list

        Returns:
            Dale-Chall score
        """
        if total_words == 0 or total_sentences == 0:
            return 0.0

        asl = total_words / total_sentences
        pdw = (difficult_words / total_words) * 100

        score = 0.1579 * pdw + 0.0496 * asl

        # Adjust if more than 5% difficult words
        if pdw > 5:
            score += 3.6365

        return round(score, 2)

    def count_passive_voice(self, text: str) -> int:
        """
        Count passive voice constructions

        Args:
            text: Text to analyze

        Returns:
            Count of passive voice instances
        """
        # Simple passive voice detection (to be + past participle)
        passive_patterns = [
            r'\b(?:am|is|are|was|were|be|been|being)\s+\w+ed\b',
            r'\b(?:am|is|are|was|were|be|been|being)\s+\w+en\b'
        ]

        count = 0
        for pattern in passive_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))

        return count

    def count_legal_jargon(self, text: str) -> int:
        """
        Count legal jargon terms

        Args:
            text: Text to analyze

        Returns:
            Count of jargon terms
        """
        text_lower = text.lower()
        count = sum(1 for term in self.legal_jargon if term in text_lower)
        return count

    def analyze(self, text: str) -> ReadabilityScores:
        """
        Comprehensive readability analysis

        Args:
            text: Text to analyze

        Returns:
            ReadabilityScores with all metrics
        """
        # Tokenization
        sentences = self.split_sentences(text)
        words = self.tokenize_words(text)

        # Counts
        sentence_count = len(sentences)
        word_count = len(words)
        total_syllables = sum(self.count_syllables(word) for word in words)
        complex_word_count = self.count_complex_words(words)
        total_letters = sum(len(word) for word in words)
        total_characters = sum(len(word) for word in words)

        # Difficult words (not in Dale-Chall list)
        difficult_words = sum(1 for word in words if word.lower() not in self.dale_chall_words)

        # Averages
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        avg_syllables_per_word = total_syllables / word_count if word_count > 0 else 0

        # Calculate all scores
        fre = self.flesch_reading_ease(word_count, sentence_count, total_syllables)
        fkg = self.flesch_kincaid_grade(word_count, sentence_count, total_syllables)
        fog = self.gunning_fog_index(word_count, sentence_count, complex_word_count)
        smog = self.smog_index(sentence_count, complex_word_count)
        cli = self.coleman_liau_index(word_count, sentence_count, total_letters)
        ari = self.automated_readability_index(word_count, sentence_count, total_characters)
        dc = self.dale_chall_readability(word_count, sentence_count, difficult_words)

        # UK-specific metrics
        legal_jargon_count = self.count_legal_jargon(text)
        passive_voice_count = self.count_passive_voice(text)
        long_sentence_count = sum(1 for s in sentences if len(self.tokenize_words(s)) > 25)

        # Overall assessment
        grade_level = self._determine_grade_level(fkg)
        readability_rating = self._determine_rating(fre)
        suggestions = self._generate_suggestions(
            fre, fkg, avg_sentence_length, complex_word_count,
            word_count, passive_voice_count, legal_jargon_count, long_sentence_count
        )

        return ReadabilityScores(
            flesch_reading_ease=fre,
            flesch_kincaid_grade=fkg,
            gunning_fog=fog,
            smog_index=smog,
            coleman_liau_index=cli,
            automated_readability_index=ari,
            dale_chall_score=dc,
            sentence_count=sentence_count,
            word_count=word_count,
            syllable_count=total_syllables,
            complex_word_count=complex_word_count,
            avg_sentence_length=round(avg_sentence_length, 2),
            avg_syllables_per_word=round(avg_syllables_per_word, 2),
            legal_jargon_count=legal_jargon_count,
            passive_voice_count=passive_voice_count,
            long_sentence_count=long_sentence_count,
            grade_level=grade_level,
            readability_rating=readability_rating,
            suggestions=suggestions
        )

    def _determine_grade_level(self, fkg: float) -> str:
        """Determine grade level description"""
        if fkg <= 6:
            return "Primary School (Ages 6-11)"
        elif fkg <= 10:
            return "Secondary School (Ages 11-16)"
        elif fkg <= 12:
            return "A-Level (Ages 16-18)"
        elif fkg <= 16:
            return "University Level"
        else:
            return "Post-Graduate Level"

    def _determine_rating(self, fre: float) -> str:
        """Determine readability rating from Flesch Reading Ease"""
        if fre >= 90:
            return "Very Easy"
        elif fre >= 80:
            return "Easy"
        elif fre >= 70:
            return "Fairly Easy"
        elif fre >= 60:
            return "Standard"
        elif fre >= 50:
            return "Fairly Difficult"
        elif fre >= 30:
            return "Difficult"
        else:
            return "Very Difficult"

    def _generate_suggestions(
        self,
        fre: float,
        fkg: float,
        avg_sentence_length: float,
        complex_word_count: int,
        word_count: int,
        passive_voice_count: int,
        legal_jargon_count: int,
        long_sentence_count: int
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        # Overall readability
        if fre < 60:
            suggestions.append("Document is fairly difficult to read. Consider simplifying language.")

        if fkg > 12:
            suggestions.append("Grade level is high. Aim for 8-12 for general audiences.")

        # Sentence length
        if avg_sentence_length > 20:
            suggestions.append(f"Average sentence length is {avg_sentence_length:.1f} words. Aim for 15-20 words per sentence.")

        if long_sentence_count > 0:
            suggestions.append(f"Found {long_sentence_count} sentences over 25 words. Consider breaking them up.")

        # Word complexity
        complexity_ratio = complex_word_count / word_count if word_count > 0 else 0
        if complexity_ratio > 0.15:
            suggestions.append(f"{complexity_ratio * 100:.1f}% complex words. Try to use simpler alternatives.")

        # Passive voice
        if passive_voice_count > 0:
            passive_ratio = passive_voice_count / (word_count / 100) if word_count > 0 else 0
            if passive_ratio > 5:
                suggestions.append(f"High use of passive voice ({passive_voice_count} instances). Prefer active voice.")

        # Legal jargon
        if legal_jargon_count > 3:
            suggestions.append(f"Contains {legal_jargon_count} legal jargon terms. Consider plain English alternatives.")

        # FCA Consumer Duty compliance
        if fre < 50:
            suggestions.append("FCA Consumer Duty requires clear communication. This text may not meet comprehension standards.")

        if not suggestions:
            suggestions.append("Readability is good. Document is clear and accessible.")

        return suggestions


# Singleton instance
_readability_scorer_instance = None

def get_readability_scorer() -> ReadabilityScorer:
    """Get singleton readability scorer instance"""
    global _readability_scorer_instance
    if _readability_scorer_instance is None:
        _readability_scorer_instance = ReadabilityScorer()
    return _readability_scorer_instance
