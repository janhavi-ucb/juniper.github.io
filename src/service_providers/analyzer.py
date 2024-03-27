from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.recognizer_result import RecognizerResult
from src.services.recognizer.configuration import recognizer_configs
from src.services.recognizer.transformer_recognizer import TransformersRecognizer
from src.services.recognizer.address_recognizer import AddressesRecognizer
from typing import List
import spacy


class Analyzer:
    """
    This is the base class of an analyzer
    """
    analyzer: AnalyzerEngine


    def __init__(self):
        """
        Initialize the analyzer
        """
        self.analyzer = AnalyzerEngine(
            registry = self.__get_registry(), 
            nlp_engine = self.__get_nlp_engine(),
        )


    def __get_registry(self) -> RecognizerRegistry:
        """
        Set up presidio's recognizer registry
        """
        # set up recognizer registry
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(languages = ["en", "ALL"])

        # remove non-US recognizers
        remove_recognizers = [
            "NhsRecognizer",
            "SgFinRecognizer",
            "AuAbnRecognizer",
            "AuAcnRecognizer",
            "AuTfnRecognizer",
            "AuMedicareRecognizer",
            "InPanRecognizer",
            "InAadhaarRecognizer",
            "InVehicleRegistrationRecognizer",
        ]
        for recognizer in remove_recognizers:
            registry.remove_recognizer(recognizer) 

        # add BERT-based recognizers from huggingface
        for config in recognizer_configs:
            model_path = config.get("DEFAULT_MODEL_PATH")
            supported_entities = config.get("PRESIDIO_SUPPORTED_ENTITIES")
            transformers_recognizer = TransformersRecognizer(
                model_path = model_path, supported_entities = supported_entities)
            transformers_recognizer.load_transformer(**config)
            registry.add_recognizer(transformers_recognizer)

        # add custom address recognizer
        addresses_recognizer = AddressesRecognizer(supported_entities=["ADDRESS"])
        registry.add_recognizer(addresses_recognizer)

        return registry


    def __get_nlp_engine(self) -> NlpEngineProvider:
        """
        Set up presidio's NLP engine using small spacy model
        """
        # Use small spacy model, for faster inference.
        if not spacy.util.is_package("en_core_web_sm"):
            spacy.cli.download("en_core_web_sm")

        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }

        nlp_engine = NlpEngineProvider(nlp_configuration = nlp_configuration).create_engine()

        return nlp_engine
    

    def analyze(self, text: str) -> List[RecognizerResult]:
        """
        Apply named entity recognition based on the supported entities as
        set forth in configuration.py

        Args:
            text (str): Prompt to be NER'ed
        
        Returns:
            results (List[RecognizerResult]): A list of RecognizerResults with 
            the following attributes:
                type: Named entity type as defined in configuration
                start: Start index of the named entity
                end: End index of the named entity
                score: Accuracy
        """
        results = self.analyzer.analyze(
            text, 
            language = "en", 
            return_decision_process = True,
        )
        
        return results