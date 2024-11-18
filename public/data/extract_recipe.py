import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import re


def get_recipe_links(category_url):
    recipe_links = []
    page = 1

    while True:
        url = f"{category_url}/page/{page}/"
        print(f"Scraping page: {url}")
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"No more pages found or failed to retrieve the URL: {url}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        found_links = soup.select('h2.entry-title a')
        if not found_links:
            print(f"No more recipes found on page {page}")
            break
        
        for a_tag in found_links:
            recipe_links.append(a_tag['href'])
        
        page += 1
    
    return recipe_links

def download_image(img_url, recipe_id, recipe_name, folder='../images'):
    os.makedirs(folder, exist_ok=True)
    sanitized_name = re.sub(r'\W+', '_', recipe_name.strip().lower())
    img_path = f"{folder}/recipe_{recipe_id}_{sanitized_name}.jpg"
    
    img_data = requests.get(img_url).content
    with open(img_path, 'wb') as handler:
        handler.write(img_data)
    return img_path

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

def extract_category(soup):
    sub_menu = soup.select_one('ul.sub-menu .current-menu-parent a span')
    return sub_menu.get_text(strip=True) if sub_menu else None

def extract_recipe_details(url, recipe_id):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', class_='entry-title').get_text(strip=True)
    category = extract_category(soup) if extract_category(soup) else ""

    ingredients = [clean_ingredient_text(ingredient) for ingredient in soup.select('li.wprm-recipe-ingredient')]
    instructions = [instruction.get_text(strip=True) for instruction in soup.select('div.wprm-recipe-instruction-text')]

    prep_time = soup.find('div', class_='wprm-recipe-prep-time-container')
    cook_time = soup.find('div', class_='wprm-recipe-cook-time-container')
    prep_time_cleaned = clean_time_text(prep_time.get_text(strip=True)) if prep_time else None
    cook_time_cleaned = clean_time_text(cook_time.get_text(strip=True)) if cook_time else None

    servings = soup.find('div', class_='wprm-recipe-servings-container')
    servings = re.search(r'\d+', servings.get_text(strip=True)).group(0) if servings else None

    image_url = soup.find('meta', property='og:image')
    image_url = image_url['content'] if image_url else None
    local_image_path = download_image(image_url, recipe_id, title) if image_url else None

    schema_recipe = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "id": recipe_id,
        "name": title,
        "author": "Korean Bapsang",
        "datePublished": datetime.now().strftime('%Y-%m-%d'),
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

def save_to_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Recipe data saved to {file_name}")

if __name__ == "__main__":
    # Load existing recipes
    file_name = 'recipes.json'
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            all_recipes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_recipes = []

    # Extract recipes from "main-dish" category
    category_url = "https://www.koreanbapsang.com/category/appetizersnack/"
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
