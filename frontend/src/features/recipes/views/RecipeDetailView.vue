<script setup lang="ts">
import { BookmarkIcon, CheckIcon, PencilIcon, UtensilsIcon } from '@lucide/vue'
import { computed, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { UiBadge, UiButton, UiCallout, UiIcon } from '@components/ui'
import RecipeIngredients from '../components/RecipeIngredients.vue'
import RecipeMeta from '../components/RecipeMeta.vue'
import RecipeNutrition from '../components/RecipeNutrition.vue'
import RecipeSteps from '../components/RecipeSteps.vue'
import { useRecipeDetail } from '../recipe-detail'

const route = useRoute()

const recipeId = computed<number>(() => Number(route.params.id))

const { recipe, status, load } = useRecipeDetail(recipeId)

const hasBadges = computed<boolean>(
  () =>
    recipe.value !== null &&
    (recipe.value.diets.length > 0 ||
      recipe.value.intolerances.length > 0 ||
      recipe.value.attributes.length > 0),
)

watch(
  [recipe, status],
  ([currentRecipe, currentStatus]) => {
    if (currentStatus === 'loading') return

    document.title = `${currentRecipe?.name ?? 'Rezept nicht gefunden'} - Nibble`
  },
  { immediate: true },
)
</script>

<template>
  <div class="flex flex-col gap-6 md:gap-8">
    <p
      v-if="status === 'loading'"
      role="status"
      class="text-muted-foreground"
    >
      Rezept wird geladen …
    </p>

    <section
      v-else-if="status === 'error'"
      class="flex flex-col items-start gap-4"
    >
      <h1>Rezept</h1>

      <UiCallout
        variant="warning"
        title="Rezept konnte nicht geladen werden"
        role="alert"
      >
        Die Verbindung wurde unterbrochen.
      </UiCallout>

      <UiButton @click="load">Erneut versuchen</UiButton>
    </section>

    <template v-else-if="recipe !== null">
      <section class="flex flex-col gap-6 md:gap-8">
        <img
          v-if="recipe.image"
          :src="recipe.image"
          alt=""
          class="w-full h-40 rounded-xl object-cover md:h-60 lg:h-90"
        />

        <div
          v-else
          class="flex items-center justify-center w-full h-40 rounded-xl bg-muted text-muted-foreground md:h-60 lg:h-90"
        >
          <UiIcon
            :icon="UtensilsIcon"
            :size="36"
          />
        </div>

        <div class="flex flex-col gap-3 md:gap-4">
          <div class="flex justify-between">
            <h1 class="text-balance">
              {{ recipe.name }}
            </h1>

            <div class="flex shrink-0 items-start gap-2">
              <UiButton
                v-if="recipe.isOwner"
                variant="ghost"
                as-child
              >
                <RouterLink :to="{ name: 'recipe-edit', params: { id: recipe.id } }">
                  <UiIcon :icon="PencilIcon" />
                  Bearbeiten
                </RouterLink>
              </UiButton>

              <UiButton
                variant="ghost"
                size="icon-lg"
              >
                <UiIcon
                  :icon="BookmarkIcon"
                  :size="24"
                />
              </UiButton>
            </div>
          </div>

          <p class="max-w-prose text-muted-foreground">
            {{ recipe.description }}
          </p>
        </div>

        <RecipeMeta
          :duration-minutes="recipe.durationMinutes"
          :meal-types="recipe.mealTypes"
          :equipment="recipe.equipment"
        />

        <ul
          v-if="hasBadges"
          aria-label="Merkmale"
          class="flex flex-wrap gap-2"
        >
          <li
            v-for="diet in recipe.diets"
            :key="diet"
          >
            <UiBadge>{{ diet }}</UiBadge>
          </li>

          <li
            v-for="intolerance in recipe.intolerances"
            :key="intolerance"
          >
            <UiBadge variant="secondary">
              <UiIcon
                :icon="CheckIcon"
                :size="16"
              />

              {{ intolerance }}
            </UiBadge>
          </li>

          <li
            v-for="attribute in recipe.attributes"
            :key="attribute"
          >
            <UiBadge variant="outline">{{ attribute }}</UiBadge>
          </li>
        </ul>
      </section>

      <RecipeNutrition
        :kcal-per-serving="recipe.kcalPerServing"
        :protein-per-serving="recipe.proteinPerServing"
        :carbs-per-serving="recipe.carbsPerServing"
        :fat-per-serving="recipe.fatPerServing"
      />

      <div class="flex flex-col gap-8 md:flex-row md:gap-12 lg:gap-20">
        <div class="md:w-80 md:shrink-0">
          <RecipeIngredients
            :ingredients="recipe.ingredients"
            :base-servings="recipe.servings"
          />
        </div>

        <RecipeSteps :cooking-steps="recipe.cookingSteps" />
      </div>
    </template>

    <section
      v-else
      class="flex flex-col items-start gap-4"
    >
      <h1>Rezept nicht gefunden</h1>

      <p class="text-muted-foreground">Die Adresse ist veraltet oder das Rezept wurde entfernt.</p>
    </section>
  </div>
</template>
