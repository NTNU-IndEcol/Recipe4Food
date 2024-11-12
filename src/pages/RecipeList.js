import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const query = useQuery();
  const category = query.get('category'); // Get the category from the URL

  useEffect(() => {
    // Fetch recipes data
    fetch('/data/recipes.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch recipes");
        }
        return response.json();
      })
      .then((data) => {
        setRecipes(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Filter recipes by the selected category, if any
  const filteredRecipes = category
    ? recipes.filter((recipe) => recipe.category === category)
    : recipes;

  return (
    <div>
      <h2>{category ? `Recipes in ${category}` : 'All Recipes'}</h2>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>Error: {error}</p>
      ) : (
        <div className="recipe-container">
          {filteredRecipes.map((recipe) => (
            <div key={recipe.id} className="recipe-item">
              <Link to={`/recipes/${recipe.id}`}>
                <img src={recipe.image} alt={recipe.name} />
                <h3>{recipe.name}</h3>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecipeList;
