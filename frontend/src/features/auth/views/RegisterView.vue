<script setup lang="ts">
import { UiLink } from '@components/ui'
import AuthCard from '../components/AuthCard.vue'
import RegisterForm from '../components/RegisterForm.vue'
</script>

<template>
  <AuthCard
    title="Konto erstellen"
    description="Mit einem Konto erfasst du Kalorien und Gewicht und speicherst Rezepte."
  >
    <RegisterForm />

    <template #footer>
      Schon ein Konto?
      <UiLink route-name="auth-login">Anmelden</UiLink>
    </template>
  </AuthCard>
</template>
