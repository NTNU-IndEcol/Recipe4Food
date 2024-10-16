export function filterRecipesByIngredient(recipes, ingredient) {
    return recipes.filter((recipe) =>
      recipe.recipeIngredient.includes(ingredient)
    );
  }
  
  export function filterRecipesByCategory(recipes, category) {
    return recipes.filter((recipe) => recipe.recipeCategory === category);
  }
  