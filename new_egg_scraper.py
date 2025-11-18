from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random


class NewEggScraper:
    def __init__(self, headless=True):
        options = Options()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

        self.base_url = "https://www.newegg.com/p/pl?N=100006519&page={}"

    def smart_scroll(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5, 2.5))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def extract_product_info(self, product):
        try:
            title_tag = product.find("a", class_="item-title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            price_whole = product.select_one(".price-current strong")
            price_decimal = product.select_one(".price-current sup")
            price = f"${price_whole.text}{price_decimal.text}" if price_whole else ""

            rating_tag = product.find("a", class_="item-rating")
            rating = rating_tag.get("title", "") if rating_tag else ""

            seller_tag = product.find("a", class_="item-brand")
            seller = seller_tag.get_text(strip=True) if seller_tag else ""

            img = product.find("img")
            image = img["src"] if img else ""

            features = product.select("ul.item-features li")
            description = ", ".join([li.get_text(strip=True) for li in features]) if features else ""

            return {
                "title": title,
                "price": price,
                "rating": rating,
                "seller": seller,
                "image": image,
                "description": description
            }
        except:
            return None

    def scrape_page(self, page):
        url = self.base_url.format(page)
        print(f"\nScraping page {page}: {url}")

        self.driver.get(url)

        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item-cell")))
        except:
            print("No products found on this page (blocked or empty).")
            return []

        # Load full content
        self.smart_scroll()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        products = soup.select("div.item-cell")

        print(f" Found {len(products)} products on page {page}")

        items = []
        for product in products:
            info = self.extract_product_info(product)
            if info:
                items.append(info)

        return items

    def scrape_multiple_pages(self, pages=10):
        all_products = []
        for p in range(1, pages + 1):
            products = self.scrape_page(p)

            # Stop if a page returns zero items
            if len(products) == 0:
                print(f"Stopped on page {p} (blocked or no products).")
                break

            all_products.extend(products)

        return all_products

    def close(self):
        self.driver.quit()
