import re
import string

def clean_text(text):
    """
    Cleans the input text by removing punctuation, converting to lowercase, and stripping extra whitespace.
    """
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_text(text):
    """
    Normalizes the text by applying cleaning and other normalization techniques.
    """
    return clean_text(text)
