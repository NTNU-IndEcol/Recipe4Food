import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_recipe_links(category_url):
    recipe_links = []
    page = 1

    while True:
        # Construct the URL for each page
        url = f"{category_url}/page/{page}/"
        print(f"Scraping page: {url}")
        
        # Fetch the category page content
        response = requests.get(url)
        if response.status_code != 200:
            print(f"No more pages found or failed to retrieve the URL: {url}")
            break
        
        # Parse the category page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links to individual recipes
        found_links = soup.select('h2.entry-title a')
        if not found_links:
            print(f"No more recipes found on page {page}")
            break
        
        # Add links to the list
        for a_tag in found_links:
            recipe_links.append(a_tag['href'])
        
        page += 1  # Move to the next page
    
    return recipe_links

def extract_recipe_details(url):
    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return None
    
    # Parse the webpage content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract title
    title = soup.find('h1', class_='entry-title').get_text(strip=True)

    # Extract ingredients
    ingredients = []
    for ingredient in soup.select('li.wprm-recipe-ingredient'):
        ingredients.append(ingredient.get_text(strip=True))

    # Extract instructions
    instructions = []
    for instruction in soup.select('div.wprm-recipe-instruction-text'):
        instructions.append(instruction.get_text(strip=True))

    # Extract other relevant details
    prep_time = soup.find('div', class_='wprm-recipe-prep-time-container')
    cook_time = soup.find('div', class_='wprm-recipe-cook-time-container')
    servings = soup.find('div', class_='wprm-recipe-servings-container')

    # Schema.org JSON-LD Recipe structure
    schema_recipe = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": title,
        "author": "Korean Bapsang",  # Assuming a fixed author
        "datePublished": datetime.now().strftime('%Y-%m-%d'),  # Current date as default
        "recipeIngredient": ingredients,
        "recipeInstructions": " ".join(instructions),  # Combine instructions into a string
        "recipeYield": servings.get_text(strip=True) if servings else None,
        "prepTime": f"PT{prep_time.get_text(strip=True)}" if prep_time else None,
        "cookTime": f"PT{cook_time.get_text(strip=True)}" if cook_time else None,
        "image": soup.find('img')['src'] if soup.find('img') else None,  # First image as recipe image
        "description": soup.find('meta', attrs={"name": "description"})['content'] if soup.find('meta', attrs={"name": "description"}) else title
    }

    return schema_recipe

def save_to_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Recipe data saved to {file_name}")

if __name__ == "__main__":
    # Base URL of the "Appetizer/Snack" category page
    category_url = "https://www.koreanbapsang.com/category/appetizersnack"
    
    # Get all recipe links from all pages of the category
    recipe_links = get_recipe_links(category_url)
    
    all_recipes = []
    for link in recipe_links:
        print(f"Extracting recipe from {link}")
        recipe_data = extract_recipe_details(link)
        if recipe_data:
            all_recipes.append(recipe_data)
    
    # Save all the recipes in a single JSON file
    save_to_json(all_recipes, 'schema_org_recipes.json')
