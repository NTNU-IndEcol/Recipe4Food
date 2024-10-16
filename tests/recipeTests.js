import { filterRecipesByIngredient, filterRecipesByCategory } from '../src/utils/filterUtils';
import recipes from '../src/data/recipes.json';

test('filters recipes by ingredient', () => {
  const filtered = filterRecipesByIngredient(recipes, 'garlic');
  expect(filtered.length).toBeGreaterThan(0);
});

test('filters recipes by category', () => {
  const filtered = filterRecipesByCategory(recipes, 'Dinner');
  expect(filtered.length).toBeGreaterThan(0);
});
