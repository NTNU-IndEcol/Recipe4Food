import React from 'react';
import { Link } from 'react-router-dom';
import recipes from '../data/recipes.json';

function RecipeList({ categories }) {
  return (
    <div>
      {categories.map((category) => (
        <div key={category.id}>
          <h3>{category.name}</h3>
          <ul>
            {recipes
              .filter((recipe) => recipe.category === category.name)
              .map((recipe) => (
                <li key={recipe.id}>
                  <Link to={`/recipe/${recipe.id}`}>{recipe.name}</Link>
                </li>
              ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default RecipeList;
