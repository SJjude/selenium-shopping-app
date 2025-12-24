import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class GlomarkProductScraper:
    def __init__(self):
        """Initialize the scraper with browser options."""
        self.base_url = "https://glomark.lk/search?search-text="
        
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
    
    def scrape_product_by_search(self, search_term):
        """
        Search for products and get multiple results.
        
        Args:
            search_term: Product name to search for
        
        Returns:
            list: List of product dictionaries
        """
        try:
            # Navigate to search results
            search_url = f"https://glomark.lk/search?search-text={search_term}"
            print(f"Searching for: {search_term}")
            print(f"URL: {search_url}")
            
            self.driver.get(search_url)

            with open("page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)

            
            # Wait for search results to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item, .product-card, [class*='product']"))
            )
            
            # Find all product elements on the search results page
            # IMPORTANT: Inspect actual website to find correct selectors
            product_elements = self.driver.find_elements(
                By.CSS_SELECTOR, ".product-item, .product-card, .item, .card"
            )
            
            products = []
            
            for i, element in enumerate(product_elements):
                try:
                    # Extract data from each product element
                    # These selectors are examples - you MUST inspect actual website
                    product_data = {
                        "product_id": f"{search_term}_{i}",
                        "name": self._extract_from_element(element, ".product-title, .name, h3, h4"),
                        "price": self._extract_from_element(element, ".price, .product-price, [class*='price']"),
                        "description": self._extract_from_element(element, ".description, .product-desc"),
                        "image_url": self._extract_attribute_from_element(element, "img", "src"),
                        "product_url": self._extract_attribute_from_element(element, "a", "href")
                    }
                    
                    # Clean and validate
                    product_data = {k: v for k, v in product_data.items() if v}
                    
                    if product_data.get('name'):  # Only add if we got at least a name
                        products.append(product_data)
                        
                except Exception as e:
                    print(f"Error processing product {i}: {str(e)}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return []
    
    def _extract_from_element(self, parent_element, css_selector):
        """Extract text from a child element if it exists."""
        try:
            element = parent_element.find_element(By.CSS_SELECTOR, css_selector)
            return element.text.strip()
        except:
            return None
    
    def _extract_attribute_from_element(self, parent_element, tag_name, attribute):
        """Extract attribute from a child element if it exists."""
        try:
            element = parent_element.find_element(By.TAG_NAME, tag_name)
            return element.get_attribute(attribute)
        except:
            return None
    
    def save_to_json(self, products, filename="products.json"):
        """Save product list to JSON file."""
        if products:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(products)} products to {filename}")
            return True
        else:
            print("No products to save")
            return False
    
    def close(self):
        """Close the browser driver."""
        self.driver.quit()

def main():
    scraper = GlomarkProductScraper()
    
    try:
        # Search for products
        search_terms = ["carrots", "white sugar"]  # Example search terms
        
        all_products = []
        
        for term in search_terms:
            print(f"\nSearching for: '{term}'")
            products = scraper.scrape_product_by_search(term)
            
            if products:
                all_products.extend(products)
                print(f"Found {len(products)} products for '{term}'")
            else:
                print(f"No products found for '{term}'")
        
        # Save all products
        if all_products:
            scraper.save_to_json(all_products, "cargills_products.json")
        else:
            print("No products found at all")
            
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
