import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

function CategoryList() {
  const [categories, setCategories] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [expandedCategory, setExpandedCategory] = useState(null);

  // Function to clean and normalize category names
  const cleanCategoryName = (category) => {
    if (!category) return null;
    return category
      .trim()
      .replace(/[^a-zA-Z\s]/g, '')
      .toLowerCase()
      .replace(/\s+/g, ' ');
  };

  useEffect(() => {
    // Fetch recipes.json file
    fetch('/data/recipes.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data) => {
        // Save all recipes
        setRecipes(data);

        // Extract and clean unique categories
        const uniqueCategories = [
          ...new Set(
            data
              .flatMap((recipe) =>
                Array.isArray(recipe.category)
                  ? recipe.category.map(cleanCategoryName)
                  : cleanCategoryName(recipe.category)
              )
              .filter((category) => category)
          ),
        ];
        setCategories(uniqueCategories);
      })
      .catch((error) => {
        console.error('Error fetching recipes:', error);
      });
  }, []);

  const toggleCategory = (category) => {
    setExpandedCategory((prevCategory) => (prevCategory === category ? null : category));
  };

  return (
    <div className="category-list">
      <h2>Categories</h2>
      <ul>
        {categories.map((category) => (
          <li key={category}>
            <div
              onClick={() => toggleCategory(category)}
              style={{ cursor: 'pointer', fontWeight: 'bold' }}
            >
              {category}
            </div>

            {expandedCategory === category && (
              <div className="category-dishes">
                <div className="dish-list">
                  {recipes
                    .filter((recipe) =>
                      Array.isArray(recipe.category)
                        ? recipe.category.some((cat) => cleanCategoryName(cat) === category)
                        : cleanCategoryName(recipe.category) === category
                    )
                    .map((recipe) => (
                      <div className="dish-item" key={recipe.id}>
                        <img src={recipe.image} alt={recipe.name || 'Recipe Image'} />
                        <Link to={`/recipes/${recipe.id}`}>{recipe.name}</Link>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CategoryList;
