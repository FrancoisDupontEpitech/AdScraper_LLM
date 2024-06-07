import sys
from get_html_website_with_playwright import get_html_website_with_playwright
from get_website_url import *
from scrape_ads import scrape_ads
from save_ads_to_excel import save_ads_to_excel
from scrape_whitepapers import scrape_whitepapers
from save_whitepapers_to_excel import save_whitepapers_to_excel

def main(prompt):
    print("prompt: ", prompt)
    website_url = get_website_url_from_user_input(prompt)
    if not website_url:
        print("Impossible de trouver l'url du site web. Veuillez réessayer.")
        return
    print("L'url du site web est: ", website_url)
    html = get_html_website_with_playwright(website_url)
    print("len(html): ", len(html))


    print("\n\n\n")
    print("SCRAPING ADS ...")
    ads = scrape_ads(website_url, html)
    if not ads:
        print("No ads found or failed to parse ads information.")
    else:
        print(f"Ads found: {len(ads)}")
        excel_path = save_ads_to_excel(ads)
        print("ads information saved to: ", excel_path)

    print("\n\n\n")
    print("SCRAPING WHITEPAPERS ...")
    whitepapers = scrape_whitepapers(html)
    if not whitepapers:
        print("No whitepapers found or failed to parse")
    else:
        print(f"Whitepapers found: {len(whitepapers)}")
        excel_path = save_whitepapers_to_excel(whitepapers)
        print("whitepapers information saved to: ", excel_path)

if __name__ == "__main__":
    n = len(sys.argv)
    if n != 2:
        print("Usage: python adscraper_llm.py <prompt>")
        sys.exit(1)
    prompt = sys.argv[1]
    main(prompt)
