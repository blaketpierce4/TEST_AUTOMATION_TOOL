import argparse
import logging
import os
import re
import time
from configparser import ConfigParser
from llm_api import generate_text  # Placeholder for the actual API call to generate text

# Load API keys from config.ini
config = ConfigParser()
config.read('config.ini')
GEMINI_API_KEY = config.get('DEFAULT', 'GeminiApiKey', fallback='INSERT_YOUR_GEMINI_API_KEY_HERE')

def setup_logging(test_name):
    log_directory = os.path.join('tests', test_name, 'logs')
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, 'test_generator.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )

def save_text_to_file(text, folder_path, file_name):
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as file:
        file.write(text)

def generate_topics(prompt, ai_model):
    # Assuming generate_text function interacts with an API to generate text based on the AI model
    response = generate_text(ai_model, prompt)
    topics = [topic.strip() for topic in re.split(',|\n', response)]
    return topics

def create_sentiment_dataset(folder, num_samples_per_class, topics, sentiment, ai_models):
    for i in range(num_samples_per_class):
        for ai in ai_models:
            topic_index = i % len(topics)
            file_name = f"{sentiment}_{ai}_{i}.txt"
            file_path = os.path.join(folder, file_name)
            prompt = f"Generate {sentiment} text about {topics[topic_index]} using {ai}. Please provide creative content for sentiment analysis."
            start_time = time.time()
            text = generate_text(ai, prompt)
            end_time = time.time()
            logging.info(f"Generated {sentiment} text for '{topics[topic_index]}' using {ai.upper()} in {end_time - start_time} seconds.")
            save_text_to_file(text, folder, file_name)

def main():
    parser = argparse.ArgumentParser(description='Generate sentiment analysis test data.')
    parser.add_argument('test_name', type=str, help='Name of the test')
    parser.add_argument('--ai', nargs='+', choices=['chat', 'gem', 'both'], default='both', help='Choose the AI models to use (default: both)')
    args = parser.parse_args()

    test_folder = os.path.join('tests', args.test_name)
    setup_logging(args.test_name)
    logging.info(f"Starting test: {args.test_name}")
    
    # Determine which AI models to use for generating text
    ai_models = ['chat', 'gem'] if args.ai == 'both' else [args.ai]
    prompt = "List 50 topics for sentiment analysis training, separated by commas and line breaks."

    # Select AI model for topic generation; default to 'gem' if both are selected
    topics_ai_model = 'gem' if 'gem' in ai_models else 'chat'
    topics = generate_topics(prompt, topics_ai_model)
    
    num_samples_per_class = 25
    for ai_model in ai_models:
        create_sentiment_dataset(os.path.join(test_folder, 'data', 'pos'), num_samples_per_class, topics, 'positive', [ai_model])
        create_sentiment_dataset(os.path.join(test_folder, 'data', 'neg'), num_samples_per_class, topics, 'negative', [ai_model])

if __name__ == "__main__":
    main()
