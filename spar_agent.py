import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class SparProductScraper:
    def __init__(self):
        """Initialize the scraper"""
        self.base_url = "https://spar2u.lk"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def scrape_product_by_search(self, search_term):
        try:
            search_url = f"{self.base_url}/search?q={search_term}"
            print(f"Searching for: {search_term}")
            print(f"URL: {search_url}")

            self.driver.get(search_url)

            # DEBUG: save page source
            # with open("page.html", "w", encoding="utf-8") as f:
            #     f.write(self.driver.page_source)

            # Wait until at least one product card is loaded
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.card__information")
                )
            )

            # Each product is inside a card__information block
            product_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "div.card__information"
            )

            products = []

            for i, element in enumerate(product_elements):
                try:
                    product_data = {
                        "product_id": f"{search_term}_{i}",

                        # Product name
                        "name": element.find_element(
                            By.CSS_SELECTOR,
                            "h3.card__heading a"
                        ).text.strip(),

                        # Product price (regular price)
                        "price": element.find_element(
                            By.CSS_SELECTOR,
                            "span.price-item.price-item--regular"
                        ).text.strip(),

                        # Product URL
                        "product_url": element.find_element(
                            By.CSS_SELECTOR,
                            "h3.card__heading a"
                        ).get_attribute("href")
                    }

                    products.append(product_data)

                except Exception:
                   continue

            return products

        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def save_to_json(self, products, filename="spar_products.json"):
        if products:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(products, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(products)} products to {filename}")
        else:
            print("No products to save")

    def close(self):
        self.driver.quit()


def main():
    scraper = SparProductScraper()

    try:
        search_terms = ["carrots", "white sugar"]
        all_products = []

        for term in search_terms:
            products = scraper.scrape_product_by_search(term)

            if products:
                print(f"Found {len(products)} products for '{term}'")
                all_products.extend(products)
            else:
                print(f"No products found for '{term}'")

        scraper.save_to_json(all_products, "spar_products.json")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
