import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

function CategoryList() {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    // Fetch recipes.json file
    fetch('/data/recipes.json')
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then(data => {
        // Extract unique categories from recipes
        const uniqueCategories = [...new Set(data.map(recipe => recipe.category))];
        setCategories(uniqueCategories);
      })
      .catch(error => {
        console.error("Error fetching recipes:", error);
      });
  }, []);

  return (
    <div className="category-list">
      <h2>Categories</h2>
      <ul>
        {categories.map((category) => (
          <li key={category}>
            <Link to={`/recipes?category=${category}`}>{category}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CategoryList;
