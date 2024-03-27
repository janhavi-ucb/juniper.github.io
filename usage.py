from src.service_providers.analyzer import Analyzer
from src.service_providers.synthesizer import Synthesizer
from openai import OpenAI
from huggingface_hub import login

login("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")

# set up text
text = """
    Charlene Nunez, who resides at 500 Center Ridge Dr Austin, TX 78753 and can 
    be contacted via email at charlene.nunez@gmail.com or via phone at 
    123-456-7890, is experiencing a persistent dry cough that has been getting 
    worse over time, along with feelings of fatigue and weakness. She reports 
    waking up multiple times at night due to her coughing fits and feeling short 
    of breath when exerting herself physically or climbing stairs. These 
    symptoms have been affecting her ability to sleep and perform daily 
    activities. 
"""

def get_output(text):

    # use analyzer to run named entity recognition over the text
    analyzer_result = Analyzer().analyze(text)

    # for result in analyzer_result:
    #     print(F"{result}: {text[result.start:result.end]}")

    # use synthesizer to find and replace named entities
    synthesizer = Synthesizer(text, analyzer_result)
    synthesized_text = synthesizer.synthesize()

    # print result
    print(F"original_text:    {text}")
    print(F"synthesized_text: {synthesized_text}")
    return synthesized_text
# get_output(text)

def submit_prompt(text: str) -> str:
    """
    Demo function to show how to submit prompt
    """
    client = OpenAI(api_key = "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")

    system = """
        You are a helpful medical assistant, skilled in making preliminary 
        medical diagnosis. You must:
        - Consider the information provided for gender and race
        - Do not include any diagnosis that do not correspond to the gender or race
        - Respond with a list of names of possible diagnosis, sorted from the most likely diagnosis to the least likely diagonsis
    """

    completion = client.chat.completions.create(
      model = "gpt-3.5-turbo",
      messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": text}
      ]
    )

    return completion.choices[0].message.content