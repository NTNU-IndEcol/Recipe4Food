import requests
from bs4 import BeautifulSoup
import json

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
    details = {}
    prep_time = soup.find('div', class_='wprm-recipe-prep-time-container')
    cook_time = soup.find('div', class_='wprm-recipe-cook-time-container')
    servings = soup.find('div', class_='wprm-recipe-servings-container')

    if prep_time:
        details['prep_time'] = prep_time.get_text(strip=True)
    if cook_time:
        details['cook_time'] = cook_time.get_text(strip=True)
    if servings:
        details['servings'] = servings.get_text(strip=True)

    # Structure the extracted data
    recipe_data = {
        'title': title,
        'ingredients': ingredients,
        'instructions': instructions,
        'details': details
    }

    return recipe_data

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
    save_to_json(all_recipes, 'all_appetizer_snack_recipes.json')
