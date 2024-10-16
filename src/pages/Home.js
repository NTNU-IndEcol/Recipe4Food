import React from 'react';
import RecipeList from './RecipeList';
import categories from '../data/categories.json';

function Home() {
  return (
    <div>
      <header>
        <h1>Welcome to Recipe4Food</h1>
        <p>Your ultimate hub for delicious recipes!</p>
      </header>
      <section>
        <h2>Browse by Categories</h2>
        <RecipeList categories={categories} />
      </section>
    </div>
  );
}

export default Home;
