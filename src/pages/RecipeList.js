import React from 'react';
import { Link } from 'react-router-dom';

function RecipeList({ recipes }) {
  return (
    <div>
      <h1>Recipe List</h1>
      <ul>
        {recipes.map((recipe) => (
          <li key={recipe.id}>
            <Link to={`/recipe/${recipe.id}`}>
              <h2>{recipe.name}</h2>
              <img src={recipe.image} alt={recipe.name} width="100" />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}


export default RecipeList;