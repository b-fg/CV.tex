#!/usr/bin/env python3

import os
import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScholarStats:
    def __init__(self, scholar_id='FSwTh_gAAAAJ'):
        self.SCHOLAR_ID = scholar_id
        self.SCHOLAR_URL = 'http://scholar.google.com/citations?hl=en&user='
        self.SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')
        self.SERPAPI_URL = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={self.SCHOLAR_ID}&api_key={self.SERPAPI_API_KEY}"
        self.CACHE_DIR = Path('./.scholar_cache')
        self.CACHE_FILE_JSON = self.CACHE_DIR / 'scholar_data.json'
        self.CACHE_FILE_TEX = self.CACHE_DIR / 'scholar_data.tex'

    def run(self):
        """Main entry point to fetch scholar data"""
        try:
            # Check if we're running in CI
            if os.environ.get('CI'):
                logger.info("Running in CI environment")
                self.fetch_scholar_data_from_serpapi()
            else:
                logger.info("Running in local environment")
                self.fetch_scholar_data_locally()
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def fetch_scholar_data_from_serpapi(self):
        """Fetch data using SerpAPI"""
        try:
            if not self.SERPAPI_API_KEY:
                raise ValueError("SERPAPI_API_KEY environment variable not set")


            logger.info(f"SerpAPI {self.SERPAPI_API_KEY}")
            logger.info("Fetching data from SerpAPI...")
            response = requests.get(self.SERPAPI_URL, timeout=30)
            response.raise_for_status()

            data = response.json()
            scholar_data = {
                'id': self.SCHOLAR_ID,
                'citations': self._safe_get(data, ['cited_by', 'table', 0, 'citations', 'all']),
                'h_index': self._safe_get(data, ['cited_by', 'table', 1, 'h_index', 'all']),
                'i10_index': self._safe_get(data, ['cited_by', 'table', 2, 'i10_index', 'all'])
            }

            logger.info(f"Loaded data for {self.SCHOLAR_ID} from SerpAPI")
            self.save_to_cache(scholar_data)
            self.save_data_file(scholar_data)

        except Exception as e:
            logger.warning(f"Failed to fetch from SerpAPI: {e}")
            logger.info("Loading from cached file instead.")

            cached_data = self.load_from_cache()
            if cached_data:
                logger.info(f"Using cached data for {self.SCHOLAR_ID}")
                self.save_data_file(cached_data)
            else:
                logger.error("No cached data available")
                raise

    def fetch_scholar_data_locally(self):
        """Fetch data by scraping Google Scholar directly"""
        try:
            url = self.SCHOLAR_URL + self.SCHOLAR_ID
            logger.info("Fetching data from Google Scholar...")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the stats table
            table = soup.find('table')
            if not table:
                raise ValueError(f"No stats table found at {url}")

            scholar_data = {'id': self.SCHOLAR_ID}

            # Extract data from table rows (skip header row)
            rows = table.find_all('tr')[1:]
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower().replace('-', '_')
                    value = cells[1].get_text(strip=True)
                    try:
                        scholar_data[key] = int(value.replace(',', ''))
                    except ValueError:
                        scholar_data[key] = value

            logger.info(f"Loaded data for {self.SCHOLAR_ID} from HTTP request")
            self.save_to_cache(scholar_data)
            self.save_data_file(scholar_data)

        except Exception as e:
            logger.warning(f"Error fetching data locally: {e}")

            cached_data = self.load_from_cache()
            if cached_data:
                logger.info(f"Using cached data for {self.SCHOLAR_ID}")
                self.save_data_file(cached_data)
            else:
                logger.error("No cached data available")
                raise

    def save_to_cache(self, data):
        """Save data to cache file"""
        try:
            # Ensure cache directory exists
            self.CACHE_DIR.mkdir(exist_ok=True)

            # Write data to cache file
            with open(self.CACHE_FILE_JSON, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info("Data saved to cache")
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")

    def load_from_cache(self):
        """Load data from cache file"""
        try:
            if self.CACHE_FILE_JSON.exists():
                with open(self.CACHE_FILE_JSON, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load from cache: {e}")

        return None

    def save_data_file(self, data):
        """Save data to LaTeX file for CV compilation"""
        # Extract values with defaults
        citations = data.get('citations', 0)
        h_index = data.get('h_index', 0)
        i10_index = data.get('i10_index', 0)

        # Write LaTeX commands
        latex_content = f"""\\newcommand{{\\citations}}{{{citations}}}
\\newcommand{{\\hindex}}{{{h_index}}}
\\newcommand{{\\iindex}}{{{i10_index}}}
"""

        with open(self.CACHE_FILE_TEX, 'w') as f:
            f.write(latex_content)

        logger.info(f"Scholar data saved to {self.CACHE_FILE_TEX}")

        # Also print the data for verification
        print("\n=== Scholar Statistics ===")
        print(f"Scholar ID: {data.get('id', 'N/A')}")
        print(f"Citations: {citations}")
        print(f"H-index: {h_index}")
        print(f"i10-index: {i10_index}")
        print(f"LaTeX file: {self.CACHE_FILE_TEX}")
        print("==========================\n")

    def _safe_get(self, data, keys):
        """Safely navigate nested dictionary"""
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            elif isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
                data = data[key]
            else:
                return None
        return data

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Fetch Google Scholar statistics')
    parser.add_argument('--scholar-id', default='FSwTh_gAAAAJ',
                       help='Google Scholar ID (default: FSwTh_gAAAAJ)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scholar_stats = ScholarStats(scholar_id=args.scholar_id)
    scholar_stats.run()

if __name__ == '__main__':
    main()