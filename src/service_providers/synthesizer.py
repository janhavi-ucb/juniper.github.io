from presidio_analyzer.recognizer_result import RecognizerResult
from src.services.generator.address_generator import AddressGenerator
from src.services.generator.constant_generator import ConstantGenerator
from src.services.generator.name_generator import NameGenerator
from typing import List
import numpy as np


class Synthesizer:
    """
    This is the base class of a synthesizer
    """
    servicse: dict
    original_text: str
    synthesized_text: str
    results: List[RecognizerResult]
    mappers: dict
    add_infos: list


    def __init__(self, text: str, results: List[RecognizerResult]):
        """
        Initialize the synthesizer

        Args:
            text (str): Text that was NER'ed by Analyzer
            results (List[RecognizerResult]): List of results from Analyzer
        """
        self.original_text = text
        self.synthesized_text = text
        self.results = results
        self.mappers = dict()
        self.add_infos = list() 

        # only include implemented generators here. if the label is not listed
        # here, ConstantGenerator will be used.
        self.services = {
            "ADDRESS": AddressGenerator(),
            "PERSON": NameGenerator(),        
        }


    def __aggregate_mappers(self):
        """
        Aggregate all the mappers based on original text and results from 
        Analyzer
        """
        text_indices = set(np.arange(len(self.original_text)))

        for result in self.results:

            # check if the text indices have been NER'ed
            result_indices = set(np.arange(result.start, result.end))
            if len(result_indices - text_indices) > 0:
                continue

            # if the NER type is not implemented, use constant generator
            if result.entity_type not in self.services:
                generator = ConstantGenerator()

            # otherwise, use implemented generator
            else:
                generator = self.services.get(result.entity_type)

            # generate mapper and additional info
            result = generator.generate(self.original_text, result)

            # if the mapper has not been accounted for, add to mappers
            mapper = result.get("mapper")

            if len(set(mapper.keys()) - set(self.mappers.keys())) > 0:
                self.mappers = {**self.mappers, **mapper}
                self.add_infos.extend(result.get("add_info"))

                # remove NER'ed indices
                text_indices = text_indices - result_indices


    def __find_and_replace(self):
        """
        Find original named entities and replace them with synthesized named
        entities
        """
        for original_named_entity, synthesized_named_entity in self.mappers.items():
            self.synthesized_text = self.synthesized_text.replace(
                original_named_entity, synthesized_named_entity
            )

    
    def __append_additional_info(self):
        """
        Append additional info generated
        """
        if not self.add_infos:
            return
    
        concat_add_infos = "\n - ".join(self.add_infos)
        self.synthesized_text = (
            F"\nOriginal information:{self.synthesized_text}\n"
            F"Additional information:\n - {concat_add_infos}"
        )
            

    def synthesize(self):
        """
        Synthesize data based on original text and results from Analyzer
        """
        self.__aggregate_mappers()
        self.__find_and_replace()
        self.__append_additional_info()

        return self.synthesized_text