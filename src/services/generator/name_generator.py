from presidio_analyzer.recognizer_result import RecognizerResult
from typing import Dict, Tuple, List
import requests
import json
import re
import pandas as pd
import numpy as np
from nameparser import HumanName


class NameGenerator:
    """
    Class for an email generator
    """

    def __init__(self):
        pass
    

    def __get_gender_info_from_genderize(self, full_name: str) -> str:
        """
        Use genderize to predict gender probabilities

        Args:
            full_name (str): Full name for which the gender will be analyzed
        
        Returns:
            result (str): Textual description of gender distribution
        """
        first_name = HumanName(full_name).first

        # call genderize.io api and parse response
        response = requests.get(F"https://api.genderize.io/?name={first_name}&country_id=US")
        response = json.loads(response.text)
        gender = response.get("gender")
        gender_opposite = "female" if gender == "male" else "male"
        prob = response.get("probability")

        # generate text
        result = (
            F"This person is more likely to identify as a {gender} ({prob*100:.0f}%) "
            F"than a {gender_opposite} ({(1 - prob)*100:.0f}%) based on "
            F"predictions from genderize.io."
        )
        
        return result
    

    def __get_gender_info_from_data(self, full_name: str) -> str:
        """
        Use name, gender dataset to predict gender probabilities

        Args:
            full_name (str): Full name for which the gender will be analyzed
        
        Returns:
            result (str): Textual description of gender distribution
        """
        first_name = HumanName(full_name).first

        # get first name probabilities
        filepath = "../src/services/generator/data/name_gender_dataset.csv"
        df = pd.read_csv(filepath)
        mask = (df["Name"].str.upper() == first_name.upper())
        mask_male = mask & (df["Gender"] == "M")
        mask_female = mask & (df["Gender"] == "F")

        count_male = df.loc[mask_male, "Count"].values[0] if sum(mask_male) else 0
        count_female = df.loc[mask_female, "Count"].values[0] if sum(mask_female) else 0

        # if we have enough data for either gender, generate text.
        if (count_male + count_female) > 0:
            gender = "male" if count_male > count_female else "female"
            gender_opposite = "male" if gender == "female" else "female"
            prob = (
                (count_male if gender == "male" else count_female)
                / (count_male + count_female)
            )
            result = (
                F"This person is more likely to identify as a {gender} "
                F"({prob*100:.0f}%) than a {gender_opposite} "
                F"({(1 - prob)*100:.0f}%) based on open-source government data "
                "from the US, UK, Canada, and Australia."
            )
        # otherwise, don't provide distribution.
        else:
            result = (
                "The distribution of gender cannot be estimated for a person "
                "with the same first name."
            )
        
        return result
    

    def __get_race_info(self, full_name: str) -> str:
        """
        Use research data to predict race probabilities

        Args:
            full_name (str): Full name for which the race will be analyzed
        
        Returns:
            result (str): Textual description of racial distribution
        """
        last_name = HumanName(full_name).last
    
        # get last name probabilities
        filepath = "src/services/generator/data/last_nameRaceProbs.csv"
        df = pd.read_csv(filepath)
        mask = (df["name"] == last_name.upper())

        # if the last name is in the dataset
        if sum(mask):
            race_cols = ["whi","bla","his","asi","oth"]
            race_names = ["White", "Black", "Hispanic", "Asian", "Other"]
            race_probs = dict(zip(race_names, df.loc[mask, race_cols].values[0]))
            race_probs = [
                F"{race} ({prob*100:.0f}%)" for race, prob 
                in sorted(race_probs.items(), key=lambda item: item[1], reverse = True)
            ]
            result = (
                F"This person is most likely to identify as {race_probs[0]} as "
                F"compared to {', '.join(race_probs[1:])} based on open source "
                "voter registration data from six southern US states."
            )
        # otherwise, don't provide distribution
        else:
            result = (
                "The distribution of race cannot be estimated for a person "
                "with the same last name."
            )

        return result


    def __resolve_full_name_indices(self, text: str, start: int, end: int):
        """
        This is a helper function to resolve the indices from starpii. The
        start index may not be correct due to how starpii tokenizes the text.
        
        Args:
            text (str): The original text
            start (int): The start index of a name as predicted by starpii
            end (int): The end index of a name as predicted by starpii
        
        Returns:
            start (int): Resolved start index
            end (int): Resolved end index
        """

        result = [r for r in re.finditer("[^A-Za-z0-9]", text)]

        start_indices = [r.end() for r in result if r.start() <= start]
        start_offset = start_indices[-1]-start if start_indices else start*-1

        end_indices = [r.start() for r in result if r.end() > end]
        end_offset = end_indices[0]-end if end_indices else len(text)-end

        start += start_offset
        end += end_offset

        return start, end


    def __decompose_full_name(self, full_name: str) -> List[str]:
        """
        Decompose full name into parts for mapper
        Args:
            full_name (str): Full name to be decomposed
        
        Returns:
            result (list[str]): List of components of the name
        """
        components = re.findall(R"([A-Za-z]*[^\s]+)", full_name)
        result = [full_name, *components]

        return result
    

    def __is_doctor(self, text: str, named_entity: str) -> bool:
        """
        Check if the word "doctor" (or any of its variations) appear 
        immediately before the full name
        
        Args:
            text (str): Prompt as processed by Analyzer
            full_name (str): Full name to be checked

        Returns:
            is_doctor (bool): Whether the full name is a doctor
        """

        result = re.findall(
            F"(dr|doctor)+(\.|\s)+({named_entity.lower()})", text.lower()
        )
        is_doctor = (len(result) > 0)

        return is_doctor


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
        if result.entity_type != "PERSON" or result.score < 0.80:
            return {"mapper": dict(), "add_info": list()}
        
        start, end = self.__resolve_full_name_indices(text, result.start, result.end)
        original_named_entity = text[start:end].strip()

        # generate mapper
        name_components = self.__decompose_full_name(original_named_entity)
        mapper = {c: "[REDACTED]" for c in name_components}

        # check if doctor
        if self.__is_doctor(text, original_named_entity):
            return {"mapper": mapper, "add_info": []}

        # get additional information
        try:
            gender_info = self.__get_gender_info_from_genderize(original_named_entity)
        except:
            gender_info = self.__get_gender_info_from_data(original_named_entity)
        race_info = self.__get_race_info(original_named_entity)

        result = {
            "mapper": mapper,
            "add_info": [gender_info, race_info],
        }

        return result