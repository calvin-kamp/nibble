<script setup lang="ts">
import { Trash2Icon } from '@lucide/vue'
import { DialogClose } from 'reka-ui'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { UiButton, UiCallout, UiDialog, UiIcon, UiLink } from '@components/ui'
import { useRecipeStore } from '@stores/recipe.store'
import RecipeForm from '../components/RecipeForm.vue'
import { useRecipeDetail } from '../recipe-detail'

const route = useRoute()
const router = useRouter()
const recipeStore = useRecipeStore()

const recipeId = computed<number>(() => Number(route.params.id))

const { recipe, status, load } = useRecipeDetail(recipeId)

const isNotFound = computed<boolean>(
  () => status.value === 'not-found' || (status.value === 'loaded' && !recipe.value?.isOwner),
)

const isDeleting = ref<boolean>(false)
const deleteFailed = ref<boolean>(false)

watch(isNotFound, (notFound) => {
  if (notFound) document.title = 'Rezept nicht gefunden – Nibble'
})

async function onDelete(): Promise<void> {
  if (!recipe.value) return

  isDeleting.value = true
  deleteFailed.value = false

  try {
    await recipeStore.deleteRecipe(recipe.value.id)
    await router.push({ name: 'recipe-list' })
  } catch {
    deleteFailed.value = true
  } finally {
    isDeleting.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6 w-full max-w-2xl mx-auto md:gap-8">
    <div class="flex flex-col items-start gap-2">
      <UiLink
        route-name="recipe-list"
        variant="standalone"
      >
        Zu den Rezepten
      </UiLink>

      <h1>{{ isNotFound ? 'Rezept nicht gefunden' : 'Rezept bearbeiten' }}</h1>
    </div>

    <p
      v-if="status === 'loading'"
      role="status"
      class="text-muted-foreground"
    >
      Rezept wird geladen …
    </p>

    <div
      v-else-if="status === 'error'"
      class="flex flex-col items-start gap-4"
    >
      <UiCallout
        variant="warning"
        title="Rezept konnte nicht geladen werden"
        role="alert"
      >
        Die Verbindung wurde unterbrochen.
      </UiCallout>

      <UiButton @click="load">Erneut versuchen</UiButton>
    </div>

    <p
      v-else-if="isNotFound"
      class="max-w-prose text-muted-foreground"
    >
      Das Rezept wurde gelöscht oder der Link ist nicht mehr gültig.
    </p>

    <template v-else-if="recipe !== null">
      <RecipeForm :recipe="recipe" />

      <div class="pt-6 border-t">
        <UiDialog
          title="Rezept wirklich löschen?"
          :description="`„${recipe.name}“ wird dauerhaft entfernt.`"
        >
          <template #trigger>
            <UiButton variant="destructive">
              <UiIcon :icon="Trash2Icon" />
              Rezept löschen
            </UiButton>
          </template>

          <template #content>
            <UiCallout
              v-if="deleteFailed"
              variant="warning"
              title="Das Rezept wurde nicht gelöscht"
              role="alert"
            >
              Die Verbindung wurde unterbrochen. Versuche es erneut.
            </UiCallout>

            <div class="flex flex-col-reverse gap-2 md:flex-row md:justify-end">
              <DialogClose as-child>
                <UiButton variant="ghost">Abbrechen</UiButton>
              </DialogClose>

              <UiButton
                variant="destructive"
                :loading="isDeleting"
                @click="onDelete"
              >
                Löschen
              </UiButton>
            </div>
          </template>
        </UiDialog>
      </div>
    </template>
  </div>
</template>
