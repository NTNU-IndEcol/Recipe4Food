// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import RecipeList from './pages/RecipeList';
import CategoryList from './pages/CategoryList';
import Home from './pages/Home';
import RecipeDetailPage from './pages/RecipeDetailPage';
import Search from './pages/Search';

function App() {
  return (
    <Router>
      <header>
        <div className="container">
          <h1 className="logo">
            <Link to="/">
              <img src="/images/recipe4food.jpg" alt="Recipe4Food Logo" />
            </Link>
          </h1>
          <nav>
            <ul>
              <li><Link to="/recipes">Recipes</Link></li>
              <li><Link to="/categories">Categories</Link></li>
              <li><Link to="/search">Search</Link></li>
            </ul>
          </nav>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/recipes" element={<RecipeList />} />
        <Route path="/categories" element={<CategoryList />} />
        {/* Add dynamic route for RecipeDetail */}
        <Route path="/recipes/:id" element={<RecipeDetailPage />} />
        <Route path="/search" element={<Search />} />
      </Routes>
    </Router>
  );
}

export default App;
