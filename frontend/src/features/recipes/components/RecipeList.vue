<script setup lang="ts">
import type { Recipe } from '../recipes.types.ts'
import RecipeCard from './RecipeCard.vue'

const recipes: Recipe[] = []
</script>

<template>
  <ul
    aria-label="Rezepte Liste"
    class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4"
  >
    <li
      v-for="recipe in recipes"
      :key="recipe.id"
    >
      <RecipeCard :recipe="recipe" />
    </li>
  </ul>
</template>
