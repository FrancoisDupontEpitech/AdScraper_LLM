from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from openai import OpenAI
import os
import requests
from bs4 import BeautifulSoup
from get_website_url import ensure_correct_url
import json
import sys
import io

# Load the OpenAI API key from the .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

def scrape_whitepapers(html_main_page):
    return analyze_html_for_whitepapers(html_main_page)

def analyze_html_for_whitepapers(html_main_page):
    whitepaper_url = get_whitepapers_main_url_page_with_chatgpt(html_main_page)
    if not whitepaper_url:
        return []

    whitepaper_url = ensure_correct_url(whitepaper_url)

    if not whitepaper_url:
        return []

    html_whitepapers_page = scrape_website_with_playwright(whitepaper_url)

    if not html_whitepapers_page:
        return []

    return call_chatgpt_assistant(whitepaper_url, html_whitepapers_page)


def scrape_website_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Scroll down to load dynamic content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)

        # Capture the HTML
        html = page.content()
        browser.close()
        return html


def call_chatgpt_assistant(whitepaper_url, html):
    print("call_chatgpt_assistant: Starting to call the ChatGPT assistant")

    navigation_instructions = get_whitepapers_navigation_instructions_with_chatgpt(html)
    if not navigation_instructions:
        print("Failed to get navigation instructions from ChatGPT.")
        return []

    recovery_instructions = get_whitepapers_recovery_instructions_with_chatgpt(html)
    if not recovery_instructions:
        print("Failed to get recovery instructions from ChatGPT.")
        return []

    max_retries = 3
    retry_count = 0
    whitepaper_data = []

    while retry_count < max_retries and not whitepaper_data:
        python_code = get_python_code_to_scrape_whitepapers_with_chatgpt(whitepaper_url, navigation_instructions, recovery_instructions, temperature=0.5 + (retry_count * 0.1))
        if not python_code:
            print("Failed to get Python code from ChatGPT.")
            retry_count += 1
            continue

        # Remove markdown syntax
        python_code = python_code.replace("```python", "").replace("```", "").strip()

        print(f"call_chatgpt_assistant (python_code):\n\n{python_code}")

        exec_globals = {
            'requests': requests,
            'BeautifulSoup': BeautifulSoup,
            'json': json
        }
        exec_locals = {}

        # Capture the standard output
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        compiled_code = compile(python_code, '<string>', 'exec')

        try:
            exec(compiled_code, exec_globals, exec_locals)
            whitepaper_data = exec_locals.get('extracted_whitepapers', [])
        except Exception as e:
            print(f"Error executing the generated code: {e}")
            whitepaper_data = []

        # Reset standard output
        sys.stdout = old_stdout
        output = new_stdout.getvalue()
        # print(f"DEBUG/ Output from executed code:\n{output}")

        if not whitepaper_data:
            print(f"Retry {retry_count + 1}/{max_retries} failed. Retrying...")
        retry_count += 1

    if not whitepaper_data:
        print("Failed to extract whitepapers after multiple attempts.")

    return whitepaper_data


# récupère l'URL de la page principale des whitepapers
def get_whitepapers_main_url_page_with_chatgpt(html):
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Your are in the website's main page. You have to find the URL of the page where the Whitepapers (\"Livres Blancs\" au pluriel en français) are listed. You Should prompt only the full URL: {html}"}
        ],
        temperature=0
    )
    chatpgt_full_str_response = response.choices[0].message.content.strip()
    return chatpgt_full_str_response


# récupère les instructions de navigation pour les whitepapers
def get_whitepapers_navigation_instructions_with_chatgpt(html):
    print("[START] get_navigation_instructions:")
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze the following HTML and explain how to navigate through first 10 whitepaper pages. Return the navigation instructions. Identify the 'Next' button or link and any other relevant information. Make sure to handle cases where the 'Next' button or link might not be present: {html}"}
        ],
        temperature=0
    )

    chatgpt_response = response.choices[0].message.content.strip()
    print("[END] get_navigation_instructions:")
    return chatgpt_response


# récupère les instructions de récupération des whitepapers
def get_whitepapers_recovery_instructions_with_chatgpt(html):
    print("[START] get_whitepapers_recovery_instructions:")
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze the following HTML and explain how to retrieve Whitepapers Information : ('Whitepaper Company Name', 'Whitepaper URL', 'Whitepaper Image URL'). For the 'Whitepaper Company Name' search only the company Name that sponsoring/displaying/contributing/proposing, not the title or the description. If the company name is not written, try to find it base on the Whitepaper URL (the directory of the link can be the whitepaper name). For 'Whitepaper URL' an 'Whitepaper Image URL' return a complete valid URL. Return the whitepapers recovery instructions. Ensure the instructions handle cases where some elements might be missing or malformed: {html}"}
],
        temperature=0
    )

    chatgpt_response = response.choices[0].message.content.strip()
    print("[END] get_whitepapers_recovery_instructions")
    return chatgpt_response


# génère le code python pour extraire les whitepapers
def get_python_code_to_scrape_whitepapers_with_chatgpt(whitepaper_url, navigation_instructions, recovery_instructions, temperature=0.5):
    print("[START] get_python_code_to_scrape_whitepapers_with_chatgpt")
    client = OpenAI(api_key=openai_api_key)

    instructions = {
        "navigation_instructions": navigation_instructions,
        "recovery_instructions": recovery_instructions
    }

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"From the URL: {whitepaper_url}, analyze the following prompts and create a Python script. The code should include all necessary imports, handle potential errors by checking if elements exist before accessing them, and be free of syntax errors. Ensure the code is tested and returns the extracted whitepapers in a structured format. Capture the result in a variable named 'extracted_whitepapers' and print it and return it. The generated code MUST be only a valid Python script. Do not include any explanatory text, comments, or additional information, only the Python code: {json.dumps(instructions)}"}
        ],
        temperature=temperature,
    )

    chatgpt_response = response.choices[0].message.content.strip()
    print("[END] get_python_code_to_scrape_whitepapers_with_chatgpt")
    return chatgpt_response
