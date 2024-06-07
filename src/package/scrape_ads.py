from dotenv import load_dotenv
import os
import json
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from openai import OpenAI
from urllib.parse import urlparse, urlunparse
from get_html_website_with_playwright import get_html_website_with_playwright

# Load the OpenAI API key from the .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")


def get_final_url(url, timeout=2, max_retries=2):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    session = requests.Session()
    retries = Retry(total=max_retries, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, headers=headers, allow_redirects=True, timeout=timeout)
        return response.url
    except requests.RequestException as e:
        print(f"Failed to fetch final URL for {url}: {e}")
        return url

def normalize_url(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

def scrape_ads(url, html):
    print("Scraping ads...")

    reloads=3
    delay=2
    all_ads = []
    seen_ads = set()

    for i in range(reloads):
        print(f"Loading page iteration {i+1}")
        html = get_html_website_with_playwright(url)
        print("len(html): ", len(html))

        ad_info_str = get_ads_with_gpt(html)
        if not ad_info_str:
            print("DEBUG/ No response from ChatGPT")
            continue

        ads = parse_ads_from_response(ad_info_str)
        for ad in ads:
            ad_identifier = (ad["Ad Company Name"], normalize_url(ad["Ad Link"]), ad["Ad Image Link"])
            if ad_identifier in seen_ads:
                print(f"DEBUG/ Skipping already seen ad: {ad_identifier}")
                continue

            final_url = normalize_url(get_final_url(ad["Ad Link"]))
            ad_identifier = (ad["Ad Company Name"], final_url, ad["Ad Image Link"])
            if ad_identifier not in seen_ads:
                seen_ads.add(ad_identifier)
                ad["Ad Link"] = final_url  # Store only the final URL
                all_ads.append(ad)

        time.sleep(delay)  # Wait for a few seconds before reloading

    return all_ads


def parse_ads_from_response(response_str):
    try:
        # Remove the backticks and JSON code block indicators
        response_str = response_str.replace('```json', '').replace('```', '').strip()
        ads_data = json.loads(response_str)

        # Debug: Print the parsed JSON response to check its structure
        print(f"DEBUG/ Parsed JSON response: {ads_data}")

        ads = []

        # Check if ads_data is a dictionary and contains expected keys
        if isinstance(ads_data, dict) and all(key in ads_data for key in ["Ad Company Name", "Ad Link", "Ad Image Link"]):
            ads.append({
                "Ad Company Name": ads_data["Ad Company Name"],
                "Ad Link": ads_data["Ad Link"],
                "Ad Image Link": ads_data["Ad Image Link"]
            })

        # Check if ads_data is a list of dictionaries and contains expected keys
        elif isinstance(ads_data, list) and all(isinstance(ad, dict) for ad in ads_data):
            for ad in ads_data:
                if all(key in ad for key in ["Ad Company Name", "Ad Link", "Ad Image Link"]):
                    ads.append({
                        "Ad Company Name": ad["Ad Company Name"],
                        "Ad Link": ad["Ad Link"],
                        "Ad Image Link": ad["Ad Image Link"]
                    })
        else:
            print("DEBUG/ Unexpected JSON structure")
            return []

        return ads

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        return []


# ask the chatgpt-4o assistant to extract ads information from the HTML
def get_ads_with_gpt(html):
    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract ad information from the following HTML and return it in JSON format with keys 'Ad Company Name', 'Ad Link', and 'Ad Image Link': {html}"}
        ],
        temperature=0,
    )


    chatgpt_full_str_response = response.choices[0].message.content.strip()

    return chatgpt_full_str_response