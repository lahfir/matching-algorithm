import pandas as pd
import spacy

DATA_BASE = "data/"

# Load the Developers.csv file into a pandas DataFrame
developers_df = pd.read_csv(DATA_BASE + "Developers.csv")

# Load the tags.csv file into a pandas DataFrame
tags_df = pd.read_csv(DATA_BASE + "Tags.csv")

# Load the language model
nlp = spacy.load("en_core_web_sm")
