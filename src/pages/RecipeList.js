// src/pages/RecipeList.js
import React, { useState, useEffect } from 'react';
import RecipeDetail from './RecipeDetail';

function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [loading, setLoading] = useState(true); // Loading state for data fetch

  useEffect(() => {
    // Fetch recipes data
    fetch('/data/recipes.json')
      .then((response) => response.json())
      .then((data) => {
        setRecipes(data);
        setLoading(false); // Set loading to false once data is fetched
      });
  }, []);

  const handleRecipeClick = (recipe) => {
    setSelectedRecipe(recipe);
  };

  return (
    <div>
      <h2>Recipes</h2>
      {loading ? ( // Display loading message only when fetching data initially
        <p>Loading...</p>
      ) : (
        <ul>
          {recipes.map((recipe) => (
            <li key={recipe.id}>
              <button onClick={() => handleRecipeClick(recipe)}>
                {recipe.name}
              </button>
              {/* Display RecipeDetail below the clicked recipe */}
              {selectedRecipe?.id === recipe.id && (
                <div className="recipe-detail">
                  <RecipeDetail recipe={selectedRecipe} />
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default RecipeList;

