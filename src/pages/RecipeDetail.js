import React from 'react';
import recipes from '../data/recipes.json';
import { useParams } from 'react-router-dom';

function RecipeDetail() {
  const { id } = useParams();
  const recipe = recipes.find((recipe) => recipe.id === parseInt(id));

  return (
    <div>
      <h1>{recipe.name}</h1>
      <img src={recipe.image} alt={recipe.name} />
      <p>{recipe.description}</p>
      <h2>Ingredients</h2>
      <ul>
        {recipe.recipeIngredient.map((ingredient, index) => (
          <li key={index}>{ingredient}</li>
        ))}
      </ul>
      <h2>Instructions</h2>
      <ol>
        {recipe.recipeInstructions.map((instruction, index) => (
          <li key={index}>{instruction.text}</li>
        ))}
      </ol>
    </div>
  );
}

export default RecipeDetail;
