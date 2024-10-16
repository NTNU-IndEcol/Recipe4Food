import requests
from bs4 import BeautifulSoup
import json

def scrape_recipes(base_url):
    recipes = []
    page = 1
    while True:
        print(f"Fetching page {page}...")
        
        response = requests.get(f"{base_url}/page/{page}/")
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        recipe_links = soup.select('.entry-title a')  # Check the selector here

        if not recipe_links:
            print("No more recipes found.")
            break

        print(f"Found {len(recipe_links)} recipes on page {page}.")
        
        for link in recipe_links:
            recipe_url = link['href']
            print(f"Scraping recipe: {recipe_url}")
            recipe = scrape_recipe(recipe_url)
            if recipe:
                recipes.append(recipe)
            else:
                print(f"Failed to scrape recipe from {recipe_url}")

        page += 1

    return recipes

def scrape_recipe(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve recipe page: {url}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        title = soup.find('h1').text.strip()  # Modify selector if needed
        ingredients = [li.text.strip() for li in soup.select('.wprm-recipe-ingredient')]  # Check selector
        instructions = [li.text.strip() for li in soup.select('.wprm-recipe-instruction')]  # Check selector

        if title and ingredients and instructions:
            return {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'url': url
            }
        else:
            print(f"Failed to extract data from {url}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_recipes_to_json(recipes, filename='recipes.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    base_url = 'https://www.koreanbapsang.com/all-recipes/'
    recipes = scrape_recipes(base_url)
    save_recipes_to_json(recipes)
    print(f"Scraped {len(recipes)} recipes.")
