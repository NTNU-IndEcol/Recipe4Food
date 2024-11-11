// scripts.js
document.addEventListener("DOMContentLoaded", function () {
  fetch("/data/recipes.json")
    .then((response) => response.json())
    .then((recipes) => {
      const recipeContainer = document.getElementById("recipe-container");
      recipes.forEach((recipe) => {
        const recipeDiv = document.createElement("div");
        recipeDiv.classList.add("recipe-details");

        recipeDiv.innerHTML = `
          <h3 class="recipe-title">${recipe.name}</h3>
          <div class="recipe-image">
            <img src="${recipe.image}" alt="${recipe.name}" class="recipe-image">
          </div>
          <div class="recipe-content">
            <section class="ingredients">
              <h4>Ingredients</h4>
              <ul>${recipe.recipeIngredient.map(ingredient => `<li>${ingredient}</li>`).join('')}</ul>
            </section>
            <section class="instructions">
              <h4>Instructions</h4>
              <ol>${recipe.recipeInstructions.map(step => `<li>${step.text || step}</li>`).join('')}</ol>
            </section>
            <div class="recipe-meta">
              <p>Prep Time: ${recipe.prepTime || 'N/A'} | Cook Time: ${recipe.cookTime || 'N/A'}</p>
              <p>Servings: ${recipe.servings || 'N/A'}</p>
              <p>Calories: ${recipe.nutrition?.calories || 'N/A'}</p>
            </div>
          </div>
        `;

        recipeContainer.appendChild(recipeDiv);
      });
    })
    .catch((error) => console.error("Error fetching recipes:", error));
});