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
    service = Service("/snap/bin/geckodriver")   # Automatically install geckodriver
    options = webdriver.FirefoxOptions()
    options.headless = True  # Run in headless mode to avoid opening a visible browser
    
    # Start the Selenium WebDriver
    driver = webdriver.Firefox(service=service, options=options)

    while True:
        # Construct the correct URL for each page (handle first page and subsequent pages)
        if page == 1:
            url = category_url  # First page
        else:
            url = f"{category_url}/page/{page}/"  # Subsequent pages
        
        print(f"Scraping page: {url}")
        driver.get(url)
        
        # Wait until the page content loads (wait for recipe links to be visible)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.noskim[rel="entry-title-link"]'))
            )
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            break
        
        page_source = driver.page_source  # Get the page source for debugging
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all recipe links on the page
        found_links = soup.select('a.noskim[rel="entry-title-link"]')
        if not found_links:
            print(f"No more recipes found on page {page}")
            break
        
        # Extract recipe links
        for a_tag in found_links:
            recipe_links.append(a_tag['href'])
        
        # Check if there's a "Next" button or a link to the next page
        next_button = soup.select_one('a.next')
        if next_button:
            page += 1  # Go to the next page
        else:
            print("No more pages, stopping.")
            break

    driver.quit()  # Close the browser after scraping
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

def clean_time_text(time_text):
    match = re.search(r'(\d+)\s*(minutes|hours|seconds|days)', time_text, re.IGNORECASE)
    if match:
        quantity = match.group(1)
        unit = match.group(2).lower()
        if "minute" in unit:
            return f"{quantity} Minutes"
        elif "hour" in unit:
            return f"{quantity} Hours"
        elif "second" in unit:
            return f"{quantity} Seconds"
        elif "day" in unit:
            return f"{quantity} Days"
    return None

# Function to clean and process the ingredient text
def clean_ingredient_text(ingredient):
    amount = ingredient.select_one('.wprm-recipe-ingredient-amount')
    unit = ingredient.select_one('.wprm-recipe-ingredient-unit')
    name = ingredient.select_one('.wprm-recipe-ingredient-name')
    
    cleaned_amount = amount.get_text(strip=True) if amount else ''
    cleaned_unit = unit.get_text(strip=True) if unit else ''
    cleaned_name = name.get_text(strip=True) if name else ''
    
    return {
        "amount": cleaned_amount,
        "unit": cleaned_unit,
        "name": cleaned_name
    }

def extract_category_and_cuisine(soup):
    # Find the <script type="application/ld+json"> tag
    schema_script = soup.find('script', type='application/ld+json', class_='yoast-schema-graph')
    
    # If the schema data exists, parse it
    if schema_script:
        try:
            # Load the JSON-LD schema from the script content
            schema_json = json.loads(schema_script.string)
            
            # Extract recipe category and cuisine if available
            category = None
            cuisine = None
            
            for graph_item in schema_json.get('@graph', []):
                if graph_item.get('@type') == 'Recipe':
                    category = graph_item.get('recipeCategory', [])
                    cuisine = graph_item.get('recipeCuisine', [])
                    
                    # If categories or cuisines are lists, join them into strings
                    if category:
                        category = ', '.join(category)
                    if cuisine:
                        cuisine = ', '.join(cuisine)
                    
                    break  # We only need the first Recipe entry
                
            return category, cuisine
        
        except json.JSONDecodeError:
            print("Error decoding JSON-LD script.")
            return None, None
    
    return None, None  # Return None if no schema found


# Function to extract recipe details from a single recipe page
def extract_recipe_details(url, recipe_id):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', class_='entry-title').get_text(strip=True)

    # Extract the category and cuisine
    category, cuisine = extract_category_and_cuisine(soup)

    print(f"Category: {category}")
    print(f"Cuisine: {cuisine}")
    
    # Extract category from schema (JSON-LD)
    schema_data = soup.find('script', type='application/ld+json')
    if schema_data:
        try:
            schema_json = json.loads(schema_data.string)
            if 'recipeCategory' in schema_json:
                category = schema_json['recipeCategory'][0]
        except json.JSONDecodeError:
            print("Error decoding JSON schema.")

    # Extract prep and cook time
    prep_time_element = soup.find('div', class_='wprm-recipe-prep-time-container')
    cook_time_element = soup.find('div', class_='wprm-recipe-cook-time-container')

  #  prep_time = prep_time_element.get_text(strip=True) if prep_time_element else "0 minutes"
  #  cook_time = cook_time_element.get_text(strip=True) if cook_time_element else "0 minutes"

    prep_time_cleaned = clean_time_text(prep_time_element.get_text(strip=True)) if prep_time_element else None
    cook_time_cleaned = clean_time_text(cook_time_element.get_text(strip=True)) if cook_time_element else None

    # Extract ingredients
    ingredients = [clean_ingredient_text(ingredient) for ingredient in soup.select('li.wprm-recipe-ingredient')]

    # Extract instructions
    instructions = [instruction.get_text(strip=True) for instruction in soup.select('div.wprm-recipe-instruction-text')]
    
    # Extract servings
    servings = soup.find('div', class_='wprm-recipe-servings-container')
    servings = servings.get_text(strip=True) if servings else "Unknown servings"

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
