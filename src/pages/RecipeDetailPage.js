import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function RecipeDetailPage() {
  const { id } = useParams(); // Get the recipe ID from the URL
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch recipe data from the JSON file
    fetch('/data/recipes.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch recipe");
        }
        return response.json();
      })
      .then((data) => {
        // Find the recipe that matches the ID (assuming 'id' is unique)
        const foundRecipe = Array.isArray(data) ? data.find((r) => r.id === parseInt(id)) : null;
        if (foundRecipe) {
          setRecipe(foundRecipe);
        } else {
          setError("Recipe not found");
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        recipe && (
          <div className="recipe-detail">
            <h2>{recipe.name}</h2>
            <img src={recipe.image} alt={recipe.name} />
            <p><strong>Author:</strong> {recipe.author}</p>
            <p><strong>Category:</strong> {recipe.category}</p>
            <p><strong>Published:</strong> {recipe.datePublished}</p>
            <p>{recipe.description}</p>
            
            <h3>Ingredients:</h3>
            <ul>
              {recipe.recipeIngredient.map((ingredient, index) => (
                <li key={index}>{ingredient}</li>
              ))}
            </ul>

            <h3>Instructions:</h3>
            <ol>
              {recipe.recipeInstructions.map((step, index) => (
                <li key={index}>{step.text}</li>
              ))}
            </ol>

            <h3>Prep Time:</h3>
            <p>{recipe.prepTime}</p>

            <h3>Cook Time:</h3>
            <p>{recipe.cookTime}</p>

            <h3>Yield:</h3>
            <p>{recipe.recipeYield}</p>
          </div>
        )
      )}
    </div>
  );
}

export default RecipeDetailPage;
