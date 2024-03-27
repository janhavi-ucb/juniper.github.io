from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import List
import usaddress
import re


class AddressesRecognizer(EntityRecognizer):
    """
    Custom recognizer for US-based addresses
    """
    expected_confidence_level = 0.9 # expected confidence level for this recognizer
    
    def load(self) -> None:
        """No loading is required."""
        pass


    def analyze(
        self, 
        text: str, 
        entities: List[str], 
        nlp_artifacts: NlpArtifacts) -> List[RecognizerResult]:
        """
        Analyzes test to find tokens which represent numbers (either 123 or One Two Three).
        """
        parsed_address = usaddress.parse(text)

        candidates_regexes = list()
        candidate_tokens = list()
        for token, tag in parsed_address:
            # if the tag is non-address related
            if tag in ["Recipient", "NotAddress"] or ("address" in token.lower()):
                # if no tokens captured, move to the next one
                if not candidate_tokens:
                    continue
                # if at least one token has been captured, convert them to 
                # a candidate
                else:
                    candidates_regexes.append(".*".join(candidate_tokens))
                    candidate_tokens = list()
            # if the tag is address related, add to candidate tokens
            else:
                token = re.escape(token)
                candidate_tokens.append(token)

            # if the last tag is zip code, then convert the tokens to a candidate
            if tag in ["ZipCode"]:
                candidates_regexes.append(".*".join(candidate_tokens))
                candidate_tokens = list()
    
        # check if there are any remaining tokens left
        if candidate_tokens:
            candidates_regexes.append(".*".join(candidate_tokens))

        results = list()
        for candidate_regex in candidates_regexes:
            result = re.search(candidate_regex, text)
            entity_type = "ADDRESS"
            score = self.expected_confidence_level
            result = RecognizerResult(entity_type, result.start(), result.end(), score)
            results.append(result)

        return results