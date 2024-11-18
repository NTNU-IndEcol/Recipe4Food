import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# Function to scrape all recipe links from the category page
def get_recipe_links(category_url):
    recipe_links = []
    page = 1
    service = Service("/snap/bin/geckodriver")  # Dynamically manage geckodriver
    options = webdriver.FirefoxOptions()
    options.headless = True  # Run in headless mode
    
    driver = webdriver.Firefox(service=service, options=options)
    try:
        while True:
            # Construct URL for each page
            url = f"{category_url}/page/{page}" if page > 1 else category_url
            print(f"Scraping page: {url}")
            driver.get(url)
            
            # Wait until recipe links are visible
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.noskim[rel="entry-title-link"]'))
                )
            except Exception:
                print(f"No more recipes found on page {page}. Stopping.")
                break
            
            # Parse page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            found_links = soup.select('a.noskim[rel="entry-title-link"]')
            if not found_links:
                break
            
            # Collect recipe links
            recipe_links.extend(a_tag['href'] for a_tag in found_links)
            
            # Check for "Next" button
            next_button = soup.select_one('a.next')
            if next_button:
                page += 1
            else:
                print("No more pages, stopping.")
                break
    finally:
        driver.quit()  # Ensure the browser closes properly
    
    return recipe_links

# Function to download and save images
def download_image(img_url, recipe_id, recipe_name, folder='images'):
    os.makedirs(folder, exist_ok=True)
    sanitized_name = re.sub(r'\W+', '_', recipe_name.strip().lower())
    img_path = f"{folder}/recipe_{recipe_id}_{sanitized_name}.jpg"
    
    try:
        img_data = requests.get(img_url).content
        with open(img_path, 'wb') as handler:
            handler.write(img_data)
        print(f"Image saved: {img_path}")
    except Exception as e:
        print(f"Failed to download image {img_url}: {e}")
    return img_path

def clean_time_text(time_text):
    match = re.search(r'(\d+)\s*(minutes|hours|seconds|days)', time_text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} {match.group(2).capitalize()}"
    return None

def clean_ingredient_text(ingredient):
    amount = ingredient.select_one('.wprm-recipe-ingredient-amount')
    unit = ingredient.select_one('.wprm-recipe-ingredient-unit')
    name = ingredient.select_one('.wprm-recipe-ingredient-name')
    return {
        "amount": amount.get_text(strip=True) if amount else '',
        "unit": unit.get_text(strip=True) if unit else '',
        "name": name.get_text(strip=True) if name else ''
    }

def extract_category_and_cuisine(soup):
    schema_script = soup.find('script', type='application/ld+json', class_='yoast-schema-graph')
    categories, cuisines = set(), set()
    
    if schema_script:
        try:
            schema_json = json.loads(schema_script.string)
            for graph_item in schema_json.get('@graph', []):
                if graph_item.get('@type') == 'Recipe':
                    recipe_categories = graph_item.get('recipeCategory', [])
                    recipe_cuisines = graph_item.get('recipeCuisine', [])
                    if isinstance(recipe_categories, str):
                        recipe_categories = [recipe_categories]
                    if isinstance(recipe_cuisines, str):
                        recipe_cuisines = [recipe_cuisines]
                    categories.update(recipe_categories)
                    cuisines.update(recipe_cuisines)
                    break
        except json.JSONDecodeError:
            print("Error decoding JSON-LD script.")
    
    return list(categories), list(cuisines)

# Function to extract recipe details
def extract_recipe_details(url, recipe_id):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve URL: {url}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', class_='entry-title').get_text(strip=True)

    categories, cuisines = extract_category_and_cuisine(soup)

    prep_time = clean_time_text(soup.find('div', class_='wprm-recipe-prep-time-container').get_text(strip=True)) if soup.find('div', class_='wprm-recipe-prep-time-container') else None
    cook_time = clean_time_text(soup.find('div', class_='wprm-recipe-cook-time-container').get_text(strip=True)) if soup.find('div', class_='wprm-recipe-cook-time-container') else None

    ingredients = [clean_ingredient_text(ingredient) for ingredient in soup.select('li.wprm-recipe-ingredient')]
    instructions = [step.get_text(strip=True) for step in soup.select('div.wprm-recipe-instruction-text')]
    servings = soup.find('div', class_='wprm-recipe-servings-container')
    servings = servings.get_text(strip=True) if servings else "Unknown servings"
    image_url = soup.find('meta', property='og:image')
    image_url = image_url['content'] if image_url else None

    return {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "id": recipe_id,
        "name": title,
        "author": "Omnivore's Cookbook",
        "datePublished": time.strftime('%Y-%m-%d'),
        "category": categories,
        "cuisine": cuisines,
        "recipeIngredient": ingredients,
        "recipeInstructions": [{"@type": "HowToStep", "text": instruction} for instruction in instructions],
        "recipeYield": servings,
        "prepTime": prep_time,
        "cookTime": cook_time,
   #     "image": download_image(image_url, recipe_id, title) if image_url else None,
        "image": image_url,
        "description": soup.find('meta', attrs={"name": "description"})['content'] if soup.find('meta', attrs={"name": "description"}) else title,
        "environmentalImpact": {
            "co2Emissions": None,
            "waterUse": None
        }
    }

# Function to save recipes to JSON
def save_to_json(data, file_name):
   # os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Recipes saved to {file_name}")

if __name__ == "__main__":
    file_name = 'recipes.json'
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            all_recipes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_recipes = []

    category_url = "https://omnivorescookbook.com/category/recipe/appetizer"
    recipe_links = get_recipe_links(category_url)
    
    recipe_id = len(all_recipes) + 1
    for link in recipe_links:
        print(f"Processing recipe: {link}")
        recipe_data = extract_recipe_details(link, recipe_id)
        if recipe_data:
            all_recipes.append(recipe_data)
            recipe_id += 1

    save_to_json(all_recipes, file_name)
