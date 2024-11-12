import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Search() {
  const [searchTerm, setSearchTerm] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [matchingRecipes, setMatchingRecipes] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch the recipes from the public folder
    fetch('/data/recipes.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load recipes");
        }
        return response.json();
      })
      .then((data) => setRecipes(data))
      .catch((error) => setError("Error loading recipes"));
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    
    // Find recipes that match the keyword in the name
    const matches = recipes.filter((recipe) =>
      recipe.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    setMatchingRecipes(matches);

    if (matches.length === 0) {
      alert('No recipes found!');
    }
  };

  return (
    <div>
      <div className="search-container">
        <h2>Search for a Recipe</h2>
        <form onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Enter dish name or keyword"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit">Search</button>
        </form>
      </div>

      {/* Display error message if there's an error */}
      {error && <div className="error-message">{error}</div>}

      {/* Display matching recipes with image and name */}
      {matchingRecipes.length > 0 && (
        <div className="recipe-list">
          {matchingRecipes.map((recipe) => (
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

export default Search;
