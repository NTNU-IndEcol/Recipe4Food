import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to scrape all recipe links from the category page
def get_recipe_links(category_url):
    recipe_links = []
    page = 1
    
    while True:
        # Construct the correct URL for each page (handle first page and subsequent pages)
        if page == 1:
            url = category_url  # First page
        else:
            url = f"{category_url}/page/{page}/"  # Subsequent pages
        
        print(f"Scraping page: {url}")
        
        # Start the Selenium WebDriver
        service = Service("/snap/bin/geckodriver")  # Use webdriver manager for automatic geckodriver installation
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(service=service, options=options)
        
        driver.get(url)
        
        # Wait until the page content loads (wait for recipe links to be visible)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.noskim[rel="entry-title-link"]'))
            )
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            driver.quit()
            break
        
        page_source = driver.page_source  # Get the page source for debugging
     #   print(page_source)  # Print the page source to verify it's loaded correctly
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all recipe links on the page
        found_links = soup.select('a.noskim[rel="entry-title-link"]')
        if not found_links:
            print(f"No more recipes found on page {page}")
            break
        
        # Extract recipe links
        for a_tag in found_links:
            recipe_links.append(a_tag['href'])
        
        page += 1
        driver.quit()  # Close the browser after scraping the page
    
    return recipe_links


# Function to download and save images
def download_image(img_url, recipe_id, recipe_name, folder='../images'):
    os.makedirs(folder, exist_ok=True)
    sanitized_name = re.sub(r'\W+', '_', recipe_name.strip().lower())
    img_path = f"{folder}/recipe_{recipe_id}_{sanitized_name}.jpg"
    
    img_data = requests.get(img_url).content
    with open(img_path, 'wb') as handler:
        handler.write(img_data)
    return img_path

# Function to clean and process the ingredient text
def clean_ingredient_text(raw_text):
    """Extract amount, unit, and name from raw ingredient text."""
    amount_pattern = r"^(\d+\.?\d*)\s*"
    unit_pattern = r"\b(cup|teaspoon|tablespoon|gram|ounce|ml|liter|kg|lb|pinch|dash|slice)\b"

    # Extract amount
    amount_match = re.search(amount_pattern, raw_text)
    amount = amount_match.group(1) if amount_match else ""

    # Extract unit
    unit_match = re.search(unit_pattern, raw_text, re.IGNORECASE)
    unit = unit_match.group(0) if unit_match else ""

    # Extract ingredient name
    name = re.sub(amount_pattern, "", raw_text)
    name = re.sub(unit_pattern, "", name, flags=re.IGNORECASE).strip()

    return {
        "amount": amount,
        "unit": unit,
        "name": name
    }

# Function to extract recipe details from a single recipe page
def extract_recipe_details(url, recipe_id):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', class_='entry-title').get_text(strip=True)

    # Attempt to get the category from breadcrumbs
    category = soup.select_one('div.breadcrumbs a')
    category = category.get_text(strip=True) if category else "Unknown Category"

    # Attempt to extract category from schema (JSON-LD)
    schema_data = soup.find('script', type='application/ld+json')
    if schema_data:
        try:
            schema_json = json.loads(schema_data.string)
            if 'recipeCategory' in schema_json:
                category = schema_json['recipeCategory'][0]
                print(f"Category from schema: {category}")
        except json.JSONDecodeError:
            print("Error decoding JSON schema.")

    # Extract ingredients
    ingredients = [ingredient.get_text(strip=True) for ingredient in soup.select('li.wprm-recipe-ingredient')]
    
    # Extract instructions
    instructions = [instruction.get_text(strip=True) for instruction in soup.select('div.wprm-recipe-instruction-text')]
    
    # Extract prep time and cook time
    prep_time = soup.find('div', class_='wprm-recipe-prep-time-container')
    cook_time = soup.find('div', class_='wprm-recipe-cook-time-container')
    prep_time_cleaned = prep_time.get_text(strip=True) if prep_time else None
    cook_time_cleaned = cook_time.get_text(strip=True) if cook_time else None
    
    # Extract servings
    servings = soup.find('div', class_='wprm-recipe-servings-container')
    servings = servings.get_text(strip=True) if servings else None
    
    # Extract image URL
    image_url = soup.find('meta', property='og:image')
    image_url = image_url['content'] if image_url else None
    
    # Prepare the final recipe schema
    schema_recipe = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "id": recipe_id,
        "name": title,
        "author": "Omnivore's Cookbook",
        "datePublished": time.strftime('%Y-%m-%d'),
        "category": category,
        "recipeIngredient": ingredients,
        "recipeInstructions": [{"@type": "HowToStep", "text": instruction} for instruction in instructions],
        "recipeYield": servings,
        "prepTime": prep_time_cleaned,
        "cookTime": cook_time_cleaned,
        "image": image_url,
        "description": soup.find('meta', attrs={"name": "description"})['content'] if soup.find('meta', attrs={"name": "description"}) else title,
        "environmentalImpact": {  # Placeholder for environmental impact calculations
            "co2Emissions": None,  # Later filled in kg CO2 equivalent
            "waterUse": None       # Later filled in liters
        }
    }

    return schema_recipe


# Function to save data to a JSON file
def save_to_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Recipe data saved to {file_name}")

if __name__ == "__main__":
    # Load existing recipes
    file_name = 'recipes_omnivorscookbook.json'
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            all_recipes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_recipes = []

    # Extract recipes from "appetizer" category
    category_url = "https://omnivorescookbook.com/category/recipe/appetizer"
    recipe_links = get_recipe_links(category_url)
    
    recipe_id = len(all_recipes) + 1
    for link in recipe_links:
        print(f"Extracting recipe from {link}")
        recipe_data = extract_recipe_details(link, recipe_id)
        if recipe_data:
            all_recipes.append(recipe_data)
            recipe_id += 1

    # Save updated recipes list
    save_to_json(all_recipes, file_name)
