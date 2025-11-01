import os
import requests  # For making API calls
import pandas as pd
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging
from dotenv import load_dotenv  # To load our secret key

@dataclass
class DataIngestionConfig:
    # We just need one file: the raw data we get from the API
    raw_data_path: str = os.path.join('artifacts', 'raw_articles.csv')

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()
        load_dotenv() # Load the .env file
        self.api_key = os.getenv("NEWS_API_KEY") # Get the key
        if not self.api_key:
            logging.error("NEWS_API_KEY not found in .env file")
            raise CustomException("NEWS_API_KEY not found in .env file", "API Key Error")

    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion")
        try:
            # 1. Define what we are searching for
            keywords = '"supply chain" OR "factory fire" OR "port closure" OR "shipping delay" OR "supplier bankruptcy"'
            
            # 2. Set up and call the News API
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': keywords,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt', # Get newest first
                'pageSize': 100 # Get the max allowed (100)
            }
            
            logging.info("Fetching news from API")
            response = requests.get(url, params=params)
            
            # This will raise an error if the API call failed (e.g., bad key)
            response.raise_for_status() 
            
            data = response.json()
            articles = data.get('articles', [])
            
            if not articles:
                logging.warning("No articles found for the keywords.")
                # We'll create an empty file to prevent future steps from failing
                df_cleaned = pd.DataFrame(columns=['title', 'description', 'url', 'publishedAt', 'source'])
            
            else:
                # 3. Convert the news data to a Pandas DataFrame
                df = pd.DataFrame(articles)
                
                # We only care about a few columns
                df_cleaned = df[['title', 'description', 'url', 'publishedAt', 'source']]
                
                # 'source' is a dictionary, let's just get the name
                # We use .loc to avoid a common Pandas warning
                df_cleaned.loc[:, 'source'] = df['source'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)

            # 4. Save the "dataset" to our artifacts folder
            os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path), exist_ok=True)
            df_cleaned.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)
            
            logging.info(f"Data ingestion complete. Saved {len(df_cleaned)} articles to {self.ingestion_config.raw_data_path}")
            
            return self.ingestion_config.raw_data_path

        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP error during API call: {err.response.text}")
            raise CustomException(err, "Data Ingestion - API Error")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise CustomException(e, "Data Ingestion")

# This part lets you test just this file
if __name__ == "__main__":
    try:
        ingestion = DataIngestion()
        ingestion.initiate_data_ingestion()
    except Exception as e:
        logging.error("Testing data_ingestion.py failed.")
        # We don't re-raise the exception here so the script doesn't look like it crashed
        pass