# Juniper: Proxy interface for LLMs

## MVP for PII level 1 (w/o web UI)

Please refer to `src/usage.ipynb` for sample usage of the code.

## PoC #1: Adding Huggingface models to presidio framework

This is a PoC to see if we can add one or more Huggingface models as new recognizers to the [presidio](https://github.com/microsoft/presidio) framework.

The in-scope models are the following:
 - [ctrlbuzz/bert-addresses](https://huggingface.co/ctrlbuzz/bert-addresses) for U.S. addresses only
 - [bigcode/starpii](https://huggingface.co/bigcode/starpii) for email and IP addresses only

The code to add transformers to the framework, `TransformerRecognizer`, is found in [Presidio's repo](https://github.com/microsoft/presidio/tree/main/docs/samples/python/transformers_recognizer).

`configuration.py` is updated with the label-to-entity mapping for each model and `transformer_recognizer.py` is updated with the following input:
```
Maria lives at 123 Elm St., Apt. 4B, Springfield, IL. Her IP address is 192.0.1.1 and her email address is maria@blah.com.
```

To test this code out, please set up your environment by installing `poetry` and then running the following in the root directory:
```
poetry update
poetry shell
python3 src/transformers_recognizer/transformer_recognizer.py
```

You should get the following output:
```
Found the following entities:
type: ADDRESS, start: 19, end: 56, score: 1.0 ---- 123 Elm St., Apt. 4B, Springfield, IL
type: IP_ADDRESS, start: 76, end: 85, score: 1.0 ---- 192.0.1.1
type: EMAIL, start: 110, end: 125, score: 1.0 ----  maria@blah.com
```