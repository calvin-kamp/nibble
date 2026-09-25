<script setup lang="ts">
import type { RecipeDetail, RecipeFormValues } from '../recipes.types'

import { CarrotIcon, ListOrderedIcon } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, useTemplateRef } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  FormCheckboxGroupField,
  FormFieldArray,
  FormImageField,
  FormNumberField,
  FormSection,
  FormSelectField,
  FormTextareaField,
  FormTextField,
} from '@components/form'
import { UiButton, UiCallout, UiCard, UiIcon, UiSeparator } from '@components/ui'
import { revealFirstInvalidField } from '@lib/scroll'
import { useRecipeStore } from '@stores/recipe.store'
import { recipeSchema } from '../recipe.schema'
import {
  AMOUNT_MAX,
  attributeOptions,
  dietOptions,
  equipmentOptions,
  intoleranceOptions,
  MACRO_MAX_GRAMS,
  mealTypeOptions,
  unitOptions,
} from '../recipes.data'
import { calculateKcal, isMacroValue, toRecipePayload } from '../recipes.utils'

interface Props {
  /** Edit mode when set, otherwise the form creates a new recipe */
  recipe?: RecipeDetail
}

const props = defineProps<Props>()

const recipeStore = useRecipeStore()
const router = useRouter()

const formElement = useTemplateRef<HTMLFormElement>('formElement')

const saveFailed = ref<boolean>(false)

/** Set after the first successful save, so a retry after a failed image upload updates instead of creating a duplicate */
const savedRecipe = ref<RecipeDetail | null>(props.recipe ?? null)

const cancelTarget = computed(() =>
  props.recipe ? `/rezepte/${props.recipe.slug}` : { name: 'recipe-list' },
)

/** NaN keeps the type a number and renders as an empty field */
function newIngredient() {
  return { name: '', amount: Number.NaN, unit: 'g' }
}

function newCookingStep() {
  return { text: '' }
}

const { handleSubmit, isSubmitting, values } = useForm({
  validationSchema: recipeSchema,
  initialValues: {
    image: props.recipe?.image ?? null,
    name: props.recipe?.name ?? '',
    description: props.recipe?.description ?? '',
    durationMinutes: props.recipe?.durationMinutes ?? 0,
    mealTypes: props.recipe?.mealTypes ?? [],
    equipment: props.recipe?.equipment ?? [],
    diets: props.recipe?.diets ?? [],
    intolerances: props.recipe?.intolerances ?? [],
    attributes: props.recipe?.attributes ?? [],
    proteinPerServing: props.recipe?.proteinPerServing ?? 0,
    carbsPerServing: props.recipe?.carbsPerServing ?? 0,
    fatPerServing: props.recipe?.fatPerServing ?? 0,
    servings: props.recipe?.servings ?? 1,
    ingredients: props.recipe?.ingredients ?? [newIngredient()],
    cookingSteps: props.recipe?.cookingSteps.map(({ text }) => ({ text })) ?? [newCookingStep()],
  },
})

const kcalPerServing = computed<number | null>(() => {
  const { proteinPerServing, carbsPerServing, fatPerServing } = values

  if (
    !isMacroValue(proteinPerServing) ||
    !isMacroValue(carbsPerServing) ||
    !isMacroValue(fatPerServing)
  ) {
    return null
  }

  return calculateKcal(proteinPerServing, carbsPerServing, fatPerServing)
})

const onSubmit = handleSubmit(
  async (formValues) => {
    saveFailed.value = false

    try {
      const values = formValues as RecipeFormValues

      const recipe = await recipeStore.saveRecipe(
        savedRecipe.value?.id ?? null,
        toRecipePayload(values),
      )

      savedRecipe.value = recipe

      await recipeStore.saveRecipeImage(recipe, values.image)
      await router.push(`/rezepte/${recipe.slug}`)
    } catch {
      saveFailed.value = true
    }
  },
  () => revealFirstInvalidField(formElement.value),
)
</script>

<template>
  <UiCard as-child>
    <form
      ref="formElement"
      :novalidate="true"
      class="flex flex-col gap-10"
      @submit="onSubmit"
    >
      <FormSection label="Grundangaben">
        <FormImageField
          field-name="image"
          label="Bild"
          description="JPG, PNG oder WebP, höchstens 5 MB."
        />

        <FormTextField
          field-name="name"
          label="Name"
          description="Höchstens 80 Zeichen."
          autocomplete="off"
          required
        />

        <FormTextareaField
          field-name="description"
          label="Beschreibung"
          description="Steht auf der Detailseite unter dem Namen."
        />
      </FormSection>

      <UiSeparator />

      <FormSection label="Angaben">
        <FormNumberField
          field-name="durationMinutes"
          label="Dauer"
          description="Zubereitung und Garzeit zusammen."
          :min="1"
          :max="600"
          required
        >
          <template #trailing> Minuten </template>
        </FormNumberField>

        <FormCheckboxGroupField
          field-name="mealTypes"
          label="Mahlzeit"
          :options="mealTypeOptions"
          required
        />

        <FormCheckboxGroupField
          field-name="equipment"
          label="Ausstattung"
          description="Was zum Zubereiten gebraucht wird."
          :options="equipmentOptions"
        />
      </FormSection>

      <UiSeparator />

      <FormSection
        label="Merkmale"
        description="Erscheinen auf der Rezeptkarte und in den Filtern der Übersicht."
      >
        <FormCheckboxGroupField
          field-name="diets"
          label="Ernährungsform"
          :options="dietOptions"
        />

        <FormCheckboxGroupField
          field-name="intolerances"
          label="Unverträglichkeiten"
          :options="intoleranceOptions"
        />

        <FormCheckboxGroupField
          field-name="attributes"
          label="Eigenschaften"
          :options="attributeOptions"
        />
      </FormSection>

      <UiSeparator />

      <FormSection
        label="Nährwerte pro Portion"
        description="Die Kalorien werden aus den drei Werten berechnet."
      >
        <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
          <FormNumberField
            field-name="proteinPerServing"
            label="Eiweiß"
            :min="0"
            :max="MACRO_MAX_GRAMS"
            :fraction-digits="1"
            required
          >
            <template #trailing> g </template>
          </FormNumberField>

          <FormNumberField
            field-name="carbsPerServing"
            label="Kohlenhydrate"
            :min="0"
            :max="MACRO_MAX_GRAMS"
            :fraction-digits="1"
            required
          >
            <template #trailing> g </template>
          </FormNumberField>

          <FormNumberField
            field-name="fatPerServing"
            label="Fett"
            :min="0"
            :max="MACRO_MAX_GRAMS"
            :fraction-digits="1"
            required
          >
            <template #trailing> g </template>
          </FormNumberField>
        </div>

        <div class="flex flex-col gap-2 pt-4 border-t">
          <p class="font-medium">Kalorien</p>

          <p class="text-muted-foreground text-sm">
            Eiweiß und Kohlenhydrate je 4 kcal, Fett 9 kcal pro Gramm.
          </p>

          <p class="text-3xl leading-none font-semibold tracking-tight tabular-nums">
            {{ kcalPerServing || 0 }} kcal
          </p>
        </div>
      </FormSection>

      <UiSeparator />

      <FormSection label="Zutaten">
        <FormNumberField
          field-name="servings"
          label="Portionen"
          description="Die Mengen gelten für diese Anzahl Portionen."
          :min="1"
          :max="12"
          stepper
          required
        />

        <FormFieldArray
          field-name="ingredients"
          entry-label="Zutat"
          empty-title="Noch keine Zutaten"
          empty-text="Füge die erste Zutat hinzu."
          add-more-label="Zutat hinzufügen"
          :new-entry="newIngredient"
        >
          <template #media>
            <UiIcon
              :icon="CarrotIcon"
              :size="24"
            />
          </template>

          <template #default="{ path }">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-[minmax(0,1fr)_8rem_9rem]">
              <FormTextField
                :field-name="`${path}.name`"
                label="Name"
                autocomplete="off"
                required
              />

              <FormNumberField
                :field-name="`${path}.amount`"
                label="Menge"
                :min="0"
                :max="AMOUNT_MAX"
                :fraction-digits="1"
                required
              />

              <FormSelectField
                :field-name="`${path}.unit`"
                label="Einheit"
                :options="unitOptions"
                required
              />
            </div>
          </template>
        </FormFieldArray>
      </FormSection>

      <UiSeparator />

      <FormSection
        label="Zubereitung"
        description="Ein Arbeitsschritt pro Eintrag."
      >
        <FormFieldArray
          field-name="cookingSteps"
          entry-label="Schritt"
          empty-title="Noch keine Schritte"
          empty-text="Beschreibe, wie das Rezept zubereitet wird."
          add-more-label="Schritt hinzufügen"
          :new-entry="newCookingStep"
          reorderable
        >
          <template #media>
            <UiIcon
              :icon="ListOrderedIcon"
              :size="24"
            />
          </template>

          <template #default="{ path }">
            <FormTextareaField
              :field-name="`${path}.text`"
              label="Beschreibung"
              required
            />
          </template>
        </FormFieldArray>
      </FormSection>

      <div class="flex flex-col gap-4 pt-6 border-t">
        <UiCallout
          v-if="saveFailed"
          variant="warning"
          title="Das Rezept wurde nicht gespeichert"
          role="alert"
        >
          Die Verbindung wurde unterbrochen. Deine Eingaben sind noch da, versuche es erneut.
        </UiCallout>

        <div class="flex flex-col gap-4 md:flex-row-reverse md:justify-between">
          <UiButton
            type="submit"
            :loading="isSubmitting"
          >
            {{ props.recipe ? 'Änderungen speichern' : 'Rezept speichern' }}
          </UiButton>

          <UiButton
            variant="ghost"
            as-child
          >
            <RouterLink :to="cancelTarget">Abbrechen</RouterLink>
          </UiButton>
        </div>
      </div>
    </form>
  </UiCard>
</template>
