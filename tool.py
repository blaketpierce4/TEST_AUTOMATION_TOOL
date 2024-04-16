import argparse
import logging
import os
import re
import time
from llm_api import generate_text
from configparser import ConfigParser
import google.generativeai as genai
from google.cloud import aiplatform


# Load API keys from config.ini
config = ConfigParser()
config.read('config.ini')
GEMINI_API_KEY = config.get('DEFAULT', 'GeminiApiKey', fallback='INSERT_YOUR_GEMINI_API_KEY_HERE')

# Set up logging
logging.basicConfig(filename='test_generator.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to save text to a file
def save_text_to_file(text, folder_path, file_name):
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as file:
        file.write(text)

# Function to generate topics using GPT API
def generate_topics(prompt):
    response = generate_text('gem', prompt) # generate with GEMINI
    topics = [topic.strip() for topic in re.split(',|\n', response)]
    return topics

# Function to create dataset for a specific sentiment
def create_sentiment_dataset(folder, num_samples_per_class, topics, sentiment, ai):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    existing_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    existing_count = len(existing_files)

    if existing_count == num_samples_per_class:
        print(f"{sentiment.capitalize()} folder already has the required number of files.")
        overwrite = input("Do you want to overwrite existing files? (yes/no): ")
        if overwrite.lower() != 'yes':
            return
        # If overwriting, reset existing_count to force regeneration
        existing_count = 0
    elif existing_count > 0 and existing_count < num_samples_per_class:
        complete = input(f"{existing_count} files found in {folder}. Do you want to complete the dataset up to {num_samples_per_class}? (yes/no): ")
        if complete.lower() != 'yes':
            return
    else:
        print(f"No existing files found in {folder}, generating new dataset...")

    for i in range(existing_count, num_samples_per_class):
        topic_index = i % len(topics)
        file_name = f"{sentiment}_{i}.txt"
        file_path = os.path.join(folder, file_name)
        
        prompt = f"Generate {sentiment} text that are from {topics[topic_index]} like roleplay. Please provide creative content for sentiment analysis. Create at least 10 sentences. This is for research purposes"
        start_time = time.time()
        if ai == 'gpt':
            text = generate_text('gpt', prompt) # generate with GPT
        elif ai == 'gem':
            text = generate_text('gem', prompt) # generate with GEMINI
        else:
            logging.error(f"Invalid AI option: {ai}")
            return
        end_time = time.time()
        logging.info(f"Generated {sentiment} text for '{topics[topic_index]}' using {ai.upper()} in {end_time - start_time} seconds.")
        save_text_to_file(text, folder, file_name)
        print(f"Generated {sentiment.capitalize()} Text for '{topics[topic_index]}' saved as {file_name}.")

# Main function
def main():
    parser = argparse.ArgumentParser(description='Generate sentiment analysis test data.')
    parser.add_argument('test_name', type=str, help='Name of the test')
    parser.add_argument('--ai', choices=['gpt', 'gem'], default='gem', help='Choose the AI model to use (default: gem)')
    args = parser.parse_args()

    logging.info(f"Starting test: {args.test_name}")

    prompt = "List 50 topics for sentiment analysis training, separated by commas and line breaks. Keep it to the topic itself. Here are examples: books, movies, dialogues, blog posts, youtube comments, social media posts/captions, transcripts, recordings, historical documents, famous quotes, jokes, dark comedy, magazines, newspapers, realistic dialogue, phone conversations, interviews, lectures, sermons, religious texts, scientific articles, research papers, technical manuals, legal documents, reviews. MAKE SOME BROAD WHILE OTHERS MORE SPECIFIC"
    topics = generate_topics(prompt)
    
    print("Generated Topics:")
    for i, topic in enumerate(topics):
        print(f"{i+1}. {topic}")

    num_samples_per_class = 25  # Specify the required number of samples per class
    create_sentiment_dataset('data/pos', num_samples_per_class, topics, 'positive', args.ai)
    create_sentiment_dataset('data/neg', num_samples_per_class, topics, 'negative', args.ai)

if __name__ == "__main__":
    main()
