"""
Tests for Entity Recognizer
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.core.nlp.entity_recognizer import EntityRecognizer, EntityType, get_entity_recognizer


class TestEntityRecognizer(unittest.TestCase):
    """Test cases for EntityRecognizer"""

    def setUp(self):
        """Set up test fixtures"""
        self.recognizer = EntityRecognizer()

    def test_initialization(self):
        """Test recognizer initializes correctly"""
        self.assertIsNotNone(self.recognizer)
        self.assertIsNotNone(self.recognizer.patterns)
        self.assertIsNotNone(self.recognizer.entity_dictionaries)

    def test_extract_fca_references(self):
        """Test extraction of FCA regulatory references"""
        text = "This complies with FCA COBS 4.2.1 and SYSC 10 requirements."

        entities = self.recognizer.extract_entities(text)

        fca_entities = [e for e in entities if e.entity_type == EntityType.FCA_REFERENCE]
        self.assertTrue(len(fca_entities) > 0)

    def test_extract_gdpr_articles(self):
        """Test extraction of GDPR articles"""
        text = "Under GDPR Article 7 and Data Protection Act 2018, consent must be explicit."

        entities = self.recognizer.extract_entities(text)

        gdpr_entities = [e for e in entities if e.entity_type == EntityType.GDPR_ARTICLE]
        self.assertTrue(len(gdpr_entities) > 0)

    def test_extract_amounts(self):
        """Test extraction of monetary amounts"""
        text = "The VAT registration threshold is £90,000 per year."

        entities = self.recognizer.extract_entities(text)

        amounts = [e for e in entities if e.entity_type == EntityType.AMOUNT]
        self.assertTrue(len(amounts) > 0)
        self.assertIn('90,000', amounts[0].text)

    def test_extract_company_numbers(self):
        """Test extraction of company numbers"""
        text = "Company number: 12345678 registered in England."

        entities = self.recognizer.extract_entities(text)

        company_nums = [e for e in entities if e.entity_type == EntityType.COMPANY_NUMBER]
        self.assertTrue(len(company_nums) > 0)

    def test_extract_vat_numbers(self):
        """Test extraction of VAT numbers"""
        text = "Our VAT number is GB123456789."

        entities = self.recognizer.extract_entities(text)

        vat_nums = [e for e in entities if e.entity_type == EntityType.VAT_NUMBER]
        self.assertTrue(len(vat_nums) > 0)

    def test_extract_dates(self):
        """Test extraction of dates"""
        text = "The tax year ends on 5 April 2024."

        entities = self.recognizer.extract_entities(text)

        dates = [e for e in entities if e.entity_type == EntityType.DATE]
        self.assertTrue(len(dates) > 0)

    def test_extract_percentages(self):
        """Test extraction of percentages"""
        text = "Corporation tax rate is 25% for large companies."

        entities = self.recognizer.extract_entities(text)

        percentages = [e for e in entities if e.entity_type == EntityType.PERCENTAGE]
        self.assertTrue(len(percentages) > 0)

    def test_validate_company_number(self):
        """Test company number validation"""
        self.assertTrue(self.recognizer.validate_company_number("12345678"))
        self.assertTrue(self.recognizer.validate_company_number("SC123456"))
        self.assertFalse(self.recognizer.validate_company_number("123"))

    def test_validate_vat_number(self):
        """Test VAT number validation"""
        self.assertTrue(self.recognizer.validate_vat_number("GB123456789"))
        self.assertTrue(self.recognizer.validate_vat_number("GB 123456789"))
        self.assertFalse(self.recognizer.validate_vat_number("123456789"))

    def test_validate_frn(self):
        """Test FRN validation"""
        self.assertTrue(self.recognizer.validate_frn("123456"))
        self.assertFalse(self.recognizer.validate_frn("12345"))
        self.assertFalse(self.recognizer.validate_frn("1234567"))

    def test_extract_regulatory_references(self):
        """Test extraction of all regulatory references"""
        text = """
        This document complies with FCA COBS 4.2.1, GDPR Article 15,
        HMRC CIS requirements, and Employment Rights Act 1996.
        """

        references = self.recognizer.extract_regulatory_references(text)

        self.assertIn('fca', references)
        self.assertIn('gdpr', references)
        self.assertIn('hmrc', references)
        self.assertIn('uk_law', references)

    def test_has_entity_type(self):
        """Test checking for entity type presence"""
        text = "FCA COBS 4.2.1 compliance required."

        has_fca = self.recognizer.has_entity_type(text, EntityType.FCA_REFERENCE)
        self.assertTrue(has_fca)

        has_tax = self.recognizer.has_entity_type(text, EntityType.TAX_TERM)
        self.assertFalse(has_tax)

    def test_singleton_pattern(self):
        """Test singleton accessor"""
        recognizer1 = get_entity_recognizer()
        recognizer2 = get_entity_recognizer()

        self.assertIs(recognizer1, recognizer2)


if __name__ == '__main__':
    unittest.main()
