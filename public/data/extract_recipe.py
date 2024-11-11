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

def download_image(img_url, recipe_id, recipe_name, folder='images'):
    os.makedirs(folder, exist_ok=True)
    # Sanitize recipe name for filename
    sanitized_name = re.sub(r'\W+', '_', recipe_name.strip().lower())
    img_path = f"{folder}/recipe_{recipe_id}_{sanitized_name}.jpg"
    
    img_data = requests.get(img_url).content
    with open(img_path, 'wb') as handler:
        handler.write(img_data)
    return img_path

def extract_recipe_details(url, recipe_id):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', class_='entry-title').get_text(strip=True)

    ingredients = []
    for ingredient in soup.select('li.wprm-recipe-ingredient'):
        ingredients.append(ingredient.get_text(strip=True))

    # Extract instructions and ensure the format
    instructions = []
    for instruction in soup.select('div.wprm-recipe-instruction-text'):
        instructions.append({
            "@type": "HowToStep",
            "text": instruction.get_text(strip=True)
        })

    prep_time = soup.find('div', class_='wprm-recipe-prep-time-container')
    cook_time = soup.find('div', class_='wprm-recipe-cook-time-container')
    servings = soup.find('div', class_='wprm-recipe-servings-container')

    image_url = soup.find('meta', property='og:image')
    if image_url:
        image_url = image_url['content']
    else:
        image_url = None

    local_image_path = download_image(image_url, recipe_id, title) if image_url else None

    schema_recipe = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "id": recipe_id,
        "name": title,
        "image": local_image_path,
        "author": "Korean Bapsang",
        "datePublished": datetime.now().strftime('%Y-%m-%d'),
        "recipeIngredient": ingredients,
        "recipeInstructions": instructions,  # Ensure instructions are in correct format
        "recipeYield": servings.get_text(strip=True) if servings else None,
        "prepTime": f"PT{prep_time.get_text(strip=True)}" if prep_time else None,
        "cookTime": f"PT{cook_time.get_text(strip=True)}" if cook_time else None,
        "description": soup.find('meta', attrs={"name": "description"})['content'] if soup.find('meta', attrs={"name": "description"}) else title
    }

    return schema_recipe

def save_to_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Recipe data saved to {file_name}")

if __name__ == "__main__":
    category_url = "https://www.koreanbapsang.com/category/appetizersnack"
    
    recipe_links = get_recipe_links(category_url)
    
    all_recipes = []
    recipe_id = 1  # Start ID from 1
    for link in recipe_links:
        print(f"Extracting recipe from {link}")
        recipe_data = extract_recipe_details(link, recipe_id)
        if recipe_data:
            all_recipes.append(recipe_data)
            recipe_id += 1  # Increment ID for next recipe
    
    save_to_json(all_recipes, 'recipes.json')
