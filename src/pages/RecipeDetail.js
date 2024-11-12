import React from 'react';

function RecipeDetail({ recipe }) {
  if (!recipe) return <div>Loading...</div>;

  return (
    <div className="recipe-detail">
      <h2>{recipe.name}</h2>
      <div className="recipe-image">
        <img src={recipe.image} alt={recipe.name} />
      </div>
      <section className="ingredients">
        <h3>Ingredients</h3>
        <ul>
          {recipe.recipeIngredient.map((ingredient, index) => (
            <li key={index}>{ingredient}</li>
          ))}
        </ul>
      </section>
      <section className="instructions">
        <h3>Instructions</h3>
        <ol>
          {recipe.recipeInstructions.map((instruction, index) => (
            <li key={index}>
              {typeof instruction === 'string' ? instruction : instruction.text}
            </li>
          ))}
        </ol>
      </section>
      <div className="recipe-meta">
        <p>Prep Time: {recipe.prepTime || 'N/A'}</p>
        <p>Cook Time: {recipe.cookTime || 'N/A'}</p>
        <p>Servings: {recipe.recipeYield || 'N/A'}</p>
        <p>Calories: {recipe.nutrition ? recipe.nutrition.calories : 'N/A'}</p>
      </div>
    </div>
  );
}

export default RecipeDetail;

