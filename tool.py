import configparser
import requests
import google.generativeai as genai
import logging
import subprocess
import os
import shutil
import base64

# Setup logging
logging.basicConfig(filename='tool.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

# Load API keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
GITHUB_API_KEY = config.get('DEFAULT', 'GitHubApiKey', fallback='INSERT_YOUR_GITHUB_API_KEY_HERE')
OPENAI_API_KEY = config.get('DEFAULT', 'OpenAIApiKey', fallback='INSERT_YOUR_OPENAI_API_KEY_HERE')
GEMINI_API_KEY = config.get('DEFAULT', 'GeminiApiKey', fallback='INSERT_YOUR_GEMINI_API_KEY_HERE')

def clone_repository(repo_url, local_dir):
    """Clones the specified GitHub repository into a local directory."""
    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)
    os.makedirs(local_dir, exist_ok=True)
    clone_command = ["git", "clone", repo_url, local_dir]
    subprocess.run(clone_command, check=True)
    logging.info(f"Repository cloned into {local_dir}")

def fetch_github_content(repo_url):
    """Fetch README content from the specified GitHub repository."""
    owner_repo = "/".join(repo_url.split("github.com/")[1].split('/')[:2])
    api_url = f"https://api.github.com/repos/{owner_repo}/contents/README.md"
    
    headers = {"Authorization": f"token {GITHUB_API_KEY}"}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content
    else:
        logging.error("Failed to fetch GitHub content")
        return None

def analyze_with_openai(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "prompt": prompt,
        "max_tokens": 1000,
        "temperature": 0.5,
        "model": "gpt-4-0125-preview"  # Updated model name
    }
    response = requests.post("https://api.openai.com/v1/completions", json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()["choices"][0]["text"]
        logging.info(f"OpenAI analysis result: {result}")
        return result
    else:
        error_message = response.text
        logging.error(f"Failed to analyze with OpenAI: {error_message}")
        return None

def analyze_with_google_gemini(prompt):
    """Analyze code or generate test cases using Google Gemini.""" 
    genai.configure(api_key=GEMINI_API_KEY)   
    try:
        model = genai.GenerativeModel('gemini-pro')  # Adjust the model name as necessary
        response = model.generate_content(prompt)
        
        if response:
            result = response.text
            logging.info(f"Google Gemini analysis result: {result}")
            return result
    except Exception as e:
        logging.error(f"Failed to analyze with Google Gemini: {e}")

    return None

def execute_tests(repo_dir):
    """Execute tests within the cloned repository directory without changing global working directory."""
    test_log_file = os.path.join(repo_dir, "test_log.txt")
    test_error_file = os.path.join(repo_dir, "test_error.txt")
    
    with open(test_log_file, 'w') as stdout_file, open(test_error_file, 'w') as stderr_file:
        result = subprocess.run(["pytest"], cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_file.write(result.stdout)
        stderr_file.write(result.stderr)
    
    logging.info(f"Tests executed. Results saved to {test_log_file} and errors to {test_error_file}")

def main(repo_url):
    repo_name = repo_url.split('/')[-1]
    local_dir = f"./cloned_repos/{repo_name}"
    clone_repository(repo_url, local_dir)
    
    readme_content = fetch_github_content(repo_url)
    if readme_content:
        prompt = f"Write Python test cases for the following project description:\n{readme_content}"
        test_cases = analyze_with_openai(prompt)
        if test_cases:
            test_file_path = os.path.join(local_dir, 'generated_tests.py')
            with open(test_file_path, 'w') as test_file:
                test_file.write(test_cases)
            execute_tests(local_dir)
    else:
        logging.error("No README.md content to analyze or failed to generate test cases.")

if __name__ == "__main__":
    repo_url = input("Enter the GitHub repository URL: ")
    main(repo_url)
