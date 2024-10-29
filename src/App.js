import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import RecipeList from './pages/RecipeList';
import RecipeDetail from './pages/RecipeDetail';

function App() {
  const [recipes, setRecipes] = useState([]);

  useEffect(() => {
    fetch('/data/recipes.json')
      .then((response) => response.json())
      .then((data) => setRecipes(data))
      .catch((error) => console.error('Error loading recipes:', error));
  }, []);
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<RecipeList recipes={recipes} />} />
        <Route path="/recipe/:id" element={<RecipeDetail recipes={recipes} />} />
      </Routes>
    </Router>
  );
}

export default App;