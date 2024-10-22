import requests
from bs4 import BeautifulSoup
import json

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
    # Replace with any recipe page URL
    url = "https://www.koreanbapsang.com/dubu-salad-korean-tofu-salad/"
    
    recipe_data = extract_recipe_details(url)
    if recipe_data:
        save_to_json(recipe_data, 'recipe_data.json')