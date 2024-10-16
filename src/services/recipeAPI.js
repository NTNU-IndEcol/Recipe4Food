export async function fetchRecipes() {
    const response = await fetch('/data/recipes.json');
    const data = await response.json();
    return data;
  }
  
  export async function fetchRecipeById(id) {
    const recipes = await fetchRecipes();
    return recipes.find((recipe) => recipe.id === id);
  }
  