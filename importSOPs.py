import requests
import nltk
import re
from nltk.stem import WordNetLemmatizer
from pathlib import Path
import pandas as pd

nltk.download('punkt')
lemmatizer = WordNetLemmatizer()
nltk.download('wordnet')
headers = {
    'Content-Type': 'application/json',
}

api_key = Path('apikey.txt').read_text()

# Function to get categories
def get_categories():
    response = requests.get(
        'https://cityofgso.freshservice.com/api/v2/solutions/categories?workspace_id=0',
        headers=headers,
        auth=(api_key, 'X'),
    )
    category_data = response.json()
    return [category['id'] for category in category_data.get('categories', [])]

# Function to get folders
def get_folders(category_ids):
    folder_data = []
    for cat_id in category_ids:
        response = requests.get(
            f'https://cityofgso.freshservice.com/api/v2/solutions/folders?category_id={cat_id}',
            headers=headers,
            auth=(api_key, 'X'),
        )
        folders = response.json().get('folders', [])
        folder_data.extend([folder['id'] for folder in folders])
    return folder_data

# Function to get articles
def get_articles(folder_ids):
    article_data = []
    for folder_id in folder_ids:
        response = requests.get(
            f'https://cityofgso.freshservice.com/api/v2/solutions/articles?folder_id={folder_id}&per_page=100',
            headers=headers,
            auth=(api_key, 'X'),
        )
        articles = response.json().get('articles', [])
        for article in articles:
            article_data.append({
                'id': article['id'],
                'title': article['title'],
                'description_text': article['description_text']
            })
    return article_data

# Function to clean noise from text
def clean_noise(text):
    text = re.sub(r'[^a-zA-Z\s\U0001F600-\U0001F64F]', '', text)
    text = text.lower()
    text = ' '.join([lemmatizer.lemmatize(w) for w in nltk.word_tokenize(text)])
    return text

# Get categories, folders, and articles
category_ids = get_categories()
folder_ids = get_folders(category_ids)
articles = get_articles(folder_ids)

# Create DataFrame from articles data
articles_df = pd.DataFrame(articles)

# Clean noise from text columns - Needs further testing
#articles_df['title'] = articles_df['title'].apply(clean_noise)
#articles_df['description_text'] = articles_df['description_text'].apply(clean_noise)

# Save DataFrame to JSON file
articles_df.to_json('articles.json', orient='index')
