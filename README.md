# AdScraper_LLM

## Overview

AdScraper_LLM is a project designed to scrape advertisements and save them to an Excel file. The project uses OpenAI for processing and Playwright for web scraping.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/AdScraper_LLM.git
   cd AdScraper_LLM

2. **Set up a virtual environment:**

    It is recommended to use a virtual environment to manage dependencies. You can create one using venv:

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`

3. **Install dependencies:**

    Install the required packages using pip:

    ```bash
    pip install -r requirements.txt

4. **Set up environment variables:**

    Create a .env file in the root directory of the project and add your API keys:

    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    OPENAI_ASSISTANT_ID=your_openai_assistant_id_api_key_here
    GOOGLE_SERPER_API_KEY=your_google_serper_api_key_here

### Running the Code
    To run the main script, use the following command:

    ```bash
    python src/package/adscraper_llm.py <your_prompt>

    the "<your_prompt>" might be a website URL or a website name.
    example : "itrnews" or "https://itrnews.com/" or even a sentence like "I want to scrape itrnews website"

    This will start the ad scraping process using the provided configurations and save the results to an Excel file.

### Project Structure
    src/package/: Contains the main code for the project.
    static/: Contains generated Excel files.
    .env: Environment variables file (not included in the repository).
    .gitignore: Specifies files and directories to be ignored by Git.
    requirements.txt: Lists the dependencies required for the project.
    setup.py: Setup script for the project.