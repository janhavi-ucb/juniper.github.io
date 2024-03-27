from presidio_analyzer.recognizer_result import RecognizerResult
from typing import Dict, List, Tuple
import usaddress
from uszipcode import SearchEngine
import re



class AddressGenerator:
    """
    Class for an address generator
    """

    def __init__(self):
        pass


    def __minimize_address(self, address: str) -> str:
        """
        Use usaddress package to parse the address and minimize it

        Args:
            address (str): A string containing the address

        Returns:
            minimized_address (str): A string containing a part of the address
        """
        minimized_address = ""

        parsed_address = usaddress.parse(address)
        place_names = list()
        state_name = ""
        zip_code = ""

        for token, tag in parsed_address:
            if tag == "PlaceName":
                place_names.append(token.strip())
            if tag == "StateName":
                state_name = token.strip()
            if tag == "ZipCode":
                zip_code = token.strip()
        
        if place_names and state_name:
            minimized_address = " ".join(place_names) + " " + state_name
        elif zip_code:
            zipcode = SearchEngine().by_zipcode(zip_code)
            if zipcode:
                minimized_address = zipcode.post_office_city
        elif state_name:
            minimized_address = state_name
        
        
        # # if placename and statename are both available, then use them as is
        # if "PlaceName" in components and "StateName" in components:
        #     minimized_address = components.get("PlaceName") + ", " + components.get("StateName")
        
        # # if zip code is provided, then look up the post office city
        # elif "ZipCode" in components:
        #     zipcode = SearchEngine().by_zipcode(components.get("ZipCode"))
        #     if zipcode:
        #         minimized_address = zipcode.post_office_city

        # # if only state name is provided, then use it
        # elif "StateName" in components:
        #     minimized_address = components.get("StateName")

        return minimized_address


    def generate(self, text: str, result: RecognizerResult) -> Dict[str, str]:
        """
        Generate a mapping from the original named entity to the synthesized
        named entity based on the original text and result from Analyzer

        Args:
            text (str): Prompt as processed by Analyzer
            result (RecognizerResult): A RecognizerResult as generated from
                Analyzer
        
        Returns:
            result (Dict[str, str]): A dictionary containing a mapping from
                the original named entity to the synthesized named entity
        """
        default_result = {"mapper": dict(), "add_info": list()}

        if result.entity_type != "ADDRESS":
            return default_result
        
        original_named_entity = text[result.start:result.end].strip()
        synthesized_named_entity = self.__minimize_address(original_named_entity)

        # if nothing was recognized, then skip the named entity
        if not synthesized_named_entity:
            return default_result
        
        result = {
            "mapper": {original_named_entity: synthesized_named_entity}, 
            "add_info": []
        }
        return result
