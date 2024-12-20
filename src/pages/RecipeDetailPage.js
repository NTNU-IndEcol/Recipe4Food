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
          throw new Error('Failed to fetch recipe');
        }
        return response.json();
      })
      .then((data) => {
        // Find the recipe that matches the ID (assuming 'id' is unique)
        const foundRecipe = Array.isArray(data) ? data.find((r) => r.id === parseInt(id)) : null;
        if (foundRecipe) {
          setRecipe(foundRecipe);
        } else {
          setError('Recipe not found');
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
            <h2>{recipe.name || 'Unnamed Recipe'}</h2>
            {recipe.image ? (
              <img src={recipe.image} alt={recipe.name || 'Recipe Image'} />
            ) : (
              <p>No image available</p>
            )}
            <p><strong>Author:</strong> {recipe.author || 'Unknown'}</p>
            
            {/* Handling category display */}
            <p><strong>Category:</strong> 
              {Array.isArray(recipe.category)
                ? recipe.category.join(', ')  // Display as a comma-separated list
                : recipe.category || 'Uncategorized'}
            </p>
            
            <p><strong>Published:</strong> {recipe.datePublished || 'N/A'}</p>
            <p>{recipe.description || 'No description provided'}</p>

            <h3>Ingredients:</h3>
            {recipe.recipeIngredient && recipe.recipeIngredient.length > 0 ? (
              <ul>
                {recipe.recipeIngredient.map((ingredient, index) => (
                  <li key={index}>
                    {typeof ingredient === 'object' 
                      ? `${ingredient.amount || ''} ${ingredient.unit || ''} ${ingredient.name || ''}` 
                      : ingredient}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No ingredients listed</p>
            )}

            <h3>Instructions:</h3>
            {recipe.recipeInstructions && recipe.recipeInstructions.length > 0 ? (
              <ol>
                {recipe.recipeInstructions.map((step, index) => (
                  <li key={index}>
                    {typeof step === 'string' ? step : step.text || 'Instruction missing'}
                  </li>
                ))}
              </ol>
            ) : (
              <p>No instructions provided</p>
            )}

            <h3>Prep Time:</h3>
            <p>{recipe.prepTime || 'N/A'}</p>

            <h3>Cook Time:</h3>
            <p>{recipe.cookTime || 'N/A'}</p>

            <h3>Yield:</h3>
            <p>{recipe.recipeYield || 'N/A'}</p>
          </div>
        )
      )}
    </div>
  );
}

export default RecipeDetailPage;
