// schemaUtils.js
export function getRecipeSchema(recipe) {
    return {
      "@context": "https://schema.org/",
      "@type": "Recipe",
      name: recipe.name,
      image: recipe.image,
      description: recipe.description,
      recipeCategory: recipe.recipeCategory,
      recipeCuisine: recipe.recipeCuisine,
      recipeIngredient: recipe.recipeIngredient,
      recipeInstructions: recipe.recipeInstructions.map((step, index) => ({
        "@type": "HowToStep",
        position: index + 1,
        text: step.text
      }))
    };
  }
  
  