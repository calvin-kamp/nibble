<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const recipeId = Number(route.params.id)
</script>

<template>Recipe Detail {{ recipeId }}</template>
