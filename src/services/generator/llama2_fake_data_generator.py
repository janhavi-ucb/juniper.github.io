
# https://vilsonrodrigues.medium.com/run-llama-2-models-in-a-colab-instance-using-ggml-and-ctransformers-41c1d6f0e6ad
# !CT_CUBLAS=1 pip install ctransformers --no-binary ctransformers

from ctransformers import AutoModelForCausalLM
from typing import Optional
import logging

logger = logging.getLogger("presidio-streamlit")

def call_completion_model(
    prompt: str,
    max_tokens: Optional[int] = 256,
    ) -> str:
    """Creates a request for the Llama2 Completion service and returns the response.

    :param prompt: The prompt for the completion model
    :param max_tokens: The maximum number of tokens to generate.
    """

    model_id = "TheBloke/Llama-2-7B-chat-GGML"
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        model_type = "llama",                                           
        #lib = 'avx2', for cpu use
        gpu_layers = 110, #110 for 7b, 130 for 13b
        max_new_tokens = max_tokens,
        repetition_penalty = 1.1,
        temperature = 0.1, 
        stream = False,
    )
    result = model(prompt)

    return result


def create_prompt(anonymized_text: str) -> str:
    """
    Create the prompt with instructions to Llama2.

    :param anonymized_text: Text with placeholders instead of PII values, e.g. My name is <PERSON>.
    """

    prompt = f"""
    <s>[INST] <<SYS>>
    Your role is to create synthetic text based on de-identified text with placeholders instead of Personally Identifiable Information (PII).
    Replace the placeholders (e.g. ,<PERSON>, {{DATE}}, {{ip_address}}) with fake values.

    Instructions:

    a. Use completely random numbers, so every digit is drawn between 0 and 9.
    b. Use realistic names that come from diverse genders, ethnicities and countries.
    c. If there are no placeholders, return the text as is.
    d. Keep the formatting as close to the original as possible.
    e. If PII exists in the input, replace it with fake values in the output.
    f. Remove whitespace before and after the generated text
    <</SYS>>
    
    input: How do I change the limit on my credit card {{credit_card_number}}? [/INST]
    output: How do I change the limit on my credit card 2539 3519 2345 1555? </s>
    <s>[INST] input: <PERSON> was the chief science officer at <ORGANIZATION>. [/INST]
    output: Katherine Buckjov was the chief science officer at NASA. </s>
    <s>[INST] input: Cameroon lives in <LOCATION>. [/INST]
    output: Vladimir lives in Moscow. </s>
    <s>[INST] input: {anonymized_text} 
    output: [/INST]
    """

    return prompt