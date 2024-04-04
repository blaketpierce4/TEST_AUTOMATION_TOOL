# tool.py
import configparser
import requests
import logging
import time
import subprocess
import os
from base64 import b64decode

# Setup logging
logging.basicConfig(filename='tool.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

# Load API keys
config = configparser.ConfigParser()
config.read('config.ini')
GITHUB_API_KEY = config['DEFAULT']['GitHubApiKey']
OPENAI_API_KEY = config['DEFAULT']['OpenAIApiKey']

def fetch_github_content(repo_url):
    """Fetch content from the specified GitHub repository."""
    start_time = time.time()
    owner_repo = repo_url.split("github.com/")[1]
    api_url = f"https://api.github.com/repos/{owner_repo}/contents/"
    
    headers = {"Authorization": f"token {GITHUB_API_KEY}"}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        duration = time.time() - start_time
        logging.info(f"GitHub content fetched in {duration:.2f} seconds")
        return response.json()
    else:
        logging.error("Failed to fetch GitHub content")
        return None

def analyze_with_openai(prompt):
    """Analyze code or generate test cases using OpenAI."""
    start_time = time.time()
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.5,
        "model": "code-davinci-002"  # Change as needed
    }
    response = requests.post("https://api.openai.com/v1/completions", json=data, headers=headers)
    
    if response.status_code == 200:
        duration = time.time() - start_time
        result = response.json()["choices"][0]["text"]
        logging.info(f"OpenAI analysis completed in {duration:.2f} seconds")
        return result
    else:
        logging.error("Failed to analyze with OpenAI")
        return None

def execute_tests(test_file):
    """Execute tests in the specified test file."""
    if not os.path.exists(test_file):
        logging.error("Test file does not exist")
        return
    start_time = time.time()
    result = subprocess.run(["pytest", test_file], capture_output=True, text=True)
    duration = time.time() - start_time
    logging.info(f"Tests executed in {duration:.2f} seconds")
    logging.info(f"Test results: {result.stdout}")

def main(repo_url):
    # Example prompt for generating test cases based on fetched README content
    content = fetch_github_content(repo_url)
    if content:
        for file in content:
            if file['name'] == "README.md":
                readme_content = b64decode(file['content']).decode('utf-8')
                prompt = f"Write Python test cases for the following project description:\n{readme_content}"
                test_cases = analyze_with_openai(prompt)
                if test_cases:
                    # Assuming test_cases contains valid Python code
                    with open('generated_tests.py', 'w') as f:
                        f.write(test_cases)
                    execute_tests('generated_tests.py')
                break

if __name__ == "__main__":
    repo_url = input("Enter the GitHub repository URL: ")
    main(repo_url)
