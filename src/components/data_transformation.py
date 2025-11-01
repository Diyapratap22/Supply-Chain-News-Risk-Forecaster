import os
import sys
import spacy # Import spaCy
import pandas as pd
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging

# These are the keywords we will score. (Value: score)
RISK_KEYWORDS = {
    'fire': 3, 'explosion': 3, 'halt': 3, 'shutdown': 3,
    'delay': 2, 'disruption': 2, 'strike': 2, 'protest': 2,
    'shortage': 2, 'bankruptcy': 3, 'closure': 2,
    'earthquake': 3, 'flood': 3, 'hurricane': 3, 'tariff': 2
}

@dataclass
class DataTransformationConfig:
    # We don't need a pickle file, just the path to our processed data
    processed_data_path: str = os.path.join('artifacts', 'processed_articles.csv')
    # We also need the path to the raw data (our input)
    raw_data_path: str = os.path.join('artifacts', 'raw_articles.csv')

class DataTransformation:
    def __init__(self):
        self.transformation_config = DataTransformationConfig()
        try:
            # Load the small English spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logging.info("spaCy model 'en_core_web_sm' loaded")
        except Exception as e:
            raise CustomException(e, sys)

    def get_risk_score_and_entities(self, text):
        """Processes a single piece of text (title + description)"""
        if not isinstance(text, str) or not text.strip():
            return 0, [] # Return empty for empty text
        
        text_lower = text.lower()
        score = 0
        
        # 1. Calculate risk score
        for keyword, value in RISK_KEYWORDS.items():
            if keyword in text_lower:
                score += value
                
        # 2. Extract entities
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            # We only care about companies, locations, and products
            if ent.label_ in ['ORG', 'GPE', 'LOC', 'PRODUCT']:
                entities.append(f"{ent.text} ({ent.label_})")
        
        # Remove duplicate entities
        unique_entities = list(set(entities))
        
        return score, unique_entities

    def initiate_data_transformation(self):
        logging.info("Starting data transformation")
        try:
            # Load the raw "dataset"
            df = pd.read_csv(self.transformation_config.raw_data_path)

            # Combine title and description for fuller analysis
            df['full_text'] = df['title'].fillna('') + " " + df['description'].fillna('')

            logging.info(f"Processing {len(df)} articles...")
            
            # This is the core of our transformation:
            # We apply our function to every row in the DataFrame
            results = df['full_text'].apply(self.get_risk_score_and_entities)
            
            # 'results' is now a Series of tuples, e.g., (5, ['Acme Inc. (ORG)'])
            # Let's split it into two new columns
            df['risk_score'] = results.apply(lambda x: x[0])
            df['entities'] = results.apply(lambda x: x[1])

            # Select and reorder columns
            df_final = df[['publishedAt', 'title', 'risk_score', 'entities', 'source', 'url', 'description']]
            
            # Sort by highest risk first
            df_final = df_final.sort_values(by='risk_score', ascending=False)
            
            # Save the new processed file
            df_final.to_csv(self.transformation_config.processed_data_path, index=False)
            
            logging.info(f"Data transformation complete. Saved processed data to {self.transformation_config.processed_data_path}")
            
            return self.transformation_config.processed_data_path

        except Exception as e:
            raise CustomException(e, sys)

# This part lets you test just this file
if __name__ == "__main__":
    try:
        logging.info("--- Data Transformation Test Run Started ---")
        transformation = DataTransformation()
        transformation.initiate_data_transformation()
        logging.info("--- Data Transformation Test Run Succeeded ---")
    except Exception as e:
        logging.error("--- Data Transformation Test Run Failed ---")
        # We don't re-raise, just log
        pass