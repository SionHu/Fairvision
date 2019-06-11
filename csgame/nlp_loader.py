from en_core_web_md import load
import spacy

nlp = load()  # Single load in memory till killed

if not isinstance(nlp, spacy.lang.en.English):
    raise TypeError("Model given is not of type {}.".format("spacy.lang.en.English"))
