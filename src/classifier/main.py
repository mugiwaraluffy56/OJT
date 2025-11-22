from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

from src.preprocessing.text import normalize_text

class LicenseClassifier:
    def __init__(self):
        self.model = make_pipeline(
            TfidfVectorizer(),
            MultinomialNB()
        )

    def train(self, X, y):
        """
        Trains the classifier.
        X: list of license texts
        y: list of license labels
        """
        X_normalized = [normalize_text(text) for text in X]
        self.model.fit(X_normalized, y)

    def predict(self, text):
        """
        Predicts the license for a given text.
        """
        normalized_text = normalize_text(text)
        return self.model.predict([normalized_text])[0]
