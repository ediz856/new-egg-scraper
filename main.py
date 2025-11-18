from new_egg_scraper import NewEggScraper
from save_to_csv import save_to_csv

def main():
    scraper = NewEggScraper(headless=False)

    products = scraper.scrape_multiple_pages(pages=20)
    save_to_csv(products)

    scraper.close()

if __name__ == "__main__":
    main()
