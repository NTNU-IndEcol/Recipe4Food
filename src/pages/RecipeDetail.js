import React from 'react';
import { useParams } from 'react-router-dom';
import '../css/styles.css'; // Adjust the path if necessary


function RecipeDetails({ recipes }) {
  const { id } = useParams();
  const recipe = recipes.find((r) => r.id === parseInt(id));

  if (!recipe) return <p>Recipe not found</p>;

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
        {recipe.recipeInstructions.map((step, index) => (
          <li key={index}>{step.text || step}</li>
        ))}
      </ol>
    </div>
  );
}

export default RecipeDetails;