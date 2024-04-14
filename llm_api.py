import openai
import google.generativeai as genai
import logging
import configparser


# Load API keys from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
GITHUB_API_KEY = config.get('DEFAULT', 'GitHubApiKey', fallback='INSERT_YOUR_GITHUB_API_KEY_HERE')
OPENAI_API_KEY = config.get('DEFAULT', 'OpenAIApiKey', fallback='INSERT_YOUR_OPENAI_API_KEY_HERE')
GEMINI_API_KEY = config.get('DEFAULT', 'GeminiApiKey', fallback='INSERT_YOUR_GEMINI_API_KEY_HERE')

# Set up OpenAI API
openai.api_key = 'your_openai_api_key'
genai.configure(api_key=GEMINI_API_KEY)   

# Function to generate text using GPT API
def generate_text(ai, prompt):
    if ai == 'gpt':
        response = openai.Completion.create(
            engine="text-davinci-002",  # Choose the GPT model you prefer
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None
        )
        return response.choices[0].text.strip()
    if ai == 'gem':
        try:
            model = genai.GenerativeModel('gemini-pro')  # Adjust the model name as necessary
            response = model.generate_content(prompt)
        
            if response:
                result = response.text
                logging.info(f"Google Gemini analysis result: {result}")
                return result
        except Exception as e:
                response = "Failed to analyze with Google Gemini: {e}"
                logging.error(f"Failed to analyze with Google Gemini: {e}")
                return response
        return None

   