import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class CargillsProductScraper:
    def __init__(self, target_keyword="GetMenuCategoryItems"):
        self.target_keyword = target_keyword.lower()
        self.driver = self._setup_driver()
        self.captured_response = None

    def _setup_driver(self):
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def capture(self, url: str):
        self.captured_response = None

        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.get(url)

        time.sleep(6)  # allow XHR to load

        logs = self.driver.get_log("performance")

        for entry in logs:
            try:
                message = json.loads(entry["message"])["message"]

                if message.get("method") == "Network.responseReceived":
                    response = message["params"]["response"]
                    request_id = message["params"]["requestId"]
                    req_url = response.get("url", "").lower()

                    if self.target_keyword in req_url:
                        body = self.driver.execute_cdp_cmd(
                            "Network.getResponseBody",
                            {"requestId": request_id}
                        )
                        self.captured_response = body.get("body")
                        break

            except Exception:
                continue

    # 🔹 added
    def scrape_product_by_search(self, search_term: str):
        search_url = f"https://cargillsonline.com/product/{search_term}?PS={search_term}"
        self.capture(search_url)

        if not self.captured_response:
            return None

        try:
            return json.loads(self.captured_response)
        except Exception:
            return None

    # 🔹 added
    def save_to_json(self, data, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved data to {filename}")

    def close(self):
        self.driver.quit()


def main():
    scraper = CargillsProductScraper()

    try:
        search_terms = ["carrots", "white sugar"]

        all_products = []

        for term in search_terms:
            print(f"\nSearching for: '{term}'")
            products = scraper.scrape_product_by_search(term)

            if products:
                all_products.append({
                    "search_term": term,
                    "data": products
                })
                print(f"Found data for '{term}'")
            else:
                print(f"No products found for '{term}'")

        if all_products:
            scraper.save_to_json(all_products, "cargills_products.json")
        else:
            print("No products found at all")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
