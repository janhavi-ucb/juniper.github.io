from presidio_analyzer.recognizer_result import RecognizerResult
from typing import Dict


class ConstantGenerator:
    """
    Class for constant generator
    """
    mapper: dict

    def __init__(self):
        """
        Initialize the generator
        """
        self.mapper = {
            "EMAIL_ADDRESS": "user@example.net",
            "PHONE_NUMBER": "000-000-0000",
            "US_SSN": "000-00-0000",
            "US_ITIN": "000-00-0000",
            "URL": "http://www.example.net",
            "IP_ADDRESS": "0.0.0.0",
            "US_PASSPORT": "A00000000",
            "US_DRIVER_LICENSE": "000000000",
            "US_BANK_NUMBER": "000000000",
            "IBAN_CODE": "AA00AAAA00000000000000",
            "US_BANK_NUMBER": "000000000",
            "CREDIT_CARD": "0000 0000 0000 0000",
            "CRYPTO": "00000000000000000000000000",
            "NRP": "[REDACTED]"
        }


    def generate(self, text: str, result: RecognizerResult) -> Dict[str, str]:
        """
        Generate a mapping from the original named entity to the synthesized
        named entity based on the original text and result from Analyzer

        Args:
            text (str): Prompt as processed by Analyzer
            result (RecognizerResult): A RecognizerResult as generated from
                Analyzer
        
        Returns:
            mapper (Dict[str, str]): A dictionary containing a mapping from
                the original named entity to the synthesized named entity
        """

        if result.entity_type not in self.mapper:
            return {"mapper": dict(), "add_info": list()}
        
        original_named_entity = text[result.start : result.end].strip()
        synthesized_named_entity = self.mapper.get(result.entity_type)

        mapper = {original_named_entity: synthesized_named_entity}
        result = {"mapper": mapper, "add_info": list()}

        return result