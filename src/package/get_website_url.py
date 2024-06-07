import os
import re
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv


# AdScraper_LLM : la clé de l'API chatgpt est dans le .env

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
google_serper_api_key = os.getenv("GOOGLE_SERPER_API_KEY")


def extract_url(input_string):
    url_pattern = r'https?://[^\s\]]+'  # Improved regex to avoid extraneous characters
    urls = re.findall(url_pattern, input_string)

    if urls:
        return urls[0]
    else:
        return None

def convert_website_input_to_url(user_website_input):
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"return only the full URL of the website from this query : \"{user_website_input}\""},
        ]
    )

    chatpgt_full_str_response = response.choices[0].message.content.strip()

    return chatpgt_full_str_response

def search_website_url_on_google(user_website_input):

    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": user_website_input,
        "location": "France",
        "gl": "fr",
        "hl": "fr",
        "num": 1
    })
    headers = {
        'X-API-KEY': google_serper_api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()

    if 'organic' in data and len(data['organic']) > 0:
        first_link = data['organic'][0]['link']
        return first_link

    return None

def get_website_url_from_user_input(prompt):
    user_website_input = prompt

    # Check if the user input is a valid URL
    if ensure_correct_url(user_website_input):
        return user_website_input

    # If not a valid URL, proceed with ChatGPT and Google Search
    chatgpt_full_str_response = convert_website_input_to_url(user_website_input)
    url = extract_url(chatgpt_full_str_response)

    print("url: ", url)

    if url:
        website_url = ensure_correct_url(url)
        if not website_url:
            url = search_website_url_on_google(user_website_input)
            print("url de google: ", url)
            if url:
                website_url = ensure_correct_url(url)
            else:
                print("Impossible de trouver l'url du site web. Veuillez réessayer.")
                return
    else:
        url = search_website_url_on_google(user_website_input)
        print("url de google: ", url)
        if url:
            website_url = ensure_correct_url(url)
        else:
            print("Impossible de trouver l'url du site web. Veuillez réessayer.")
            return

    return website_url

def ensure_correct_url(website_url):
    print(f"Vérification de l'URL du site web : \"{website_url}\"...")

    if not website_url:
        return None

    def is_url_reachable(url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return True
        except requests.exceptions.SSLError as e:
            pass
        except requests.exceptions.RequestException as e:
            pass
        return False

    # Try the original URL first
    if is_url_reachable(website_url):
        return website_url

    # Check for variations
    if 'www.' in website_url:
        alternative_url = website_url.replace('www.', '', 1)
    else:
        alternative_url = website_url.replace('://', '://www.', 1)

    if is_url_reachable(alternative_url):
        return alternative_url

    # Try HTTP variants if HTTPS fails
    http_url = website_url.replace('https://', 'http://')
    if is_url_reachable(http_url):
        return http_url

    if is_url_reachable(alternative_url.replace('https://', 'http://')):
        return alternative_url.replace('https://', 'http://')

    return None