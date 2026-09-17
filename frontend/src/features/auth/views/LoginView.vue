<script setup lang="ts">
import { UiLink } from '@components/ui'
import AuthCard from '../components/AuthCard.vue'
import LoginForm from '../components/LoginForm.vue'
</script>

<template>
  <AuthCard
    title="Anmelden"
    description="Melde dich mit deiner E-Mail-Adresse an."
  >
    <LoginForm />

    <template #footer>
      Noch kein Konto?
      <UiLink route-name="auth-register">Konto erstellen</UiLink>
    </template>
  </AuthCard>
</template>
