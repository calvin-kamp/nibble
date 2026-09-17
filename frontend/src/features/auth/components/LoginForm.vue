<script setup lang="ts">
import type { LoginCredentials } from '@interfaces/auth.types'

import { useForm } from 'vee-validate'
import { ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FormPasswordField, FormTextField } from '@components/form'
import { UiButton, UiCallout } from '@components/ui'
import { HttpError } from '@lib/http'
import { useAuthStore } from '@stores/auth.store'
import { authErrorMessages } from '../auth.data'
import { loginSchema } from '../auth.schemas'
import { focusFirstInvalidField, getNoticeText, getRedirectTarget } from '../auth.utils'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const formRef = useTemplateRef<HTMLFormElement>('form')

const errorMessage = ref<string | null>(null)
const noticeMessage = ref<string | null>(getNoticeText(route.query.notice))

const { handleSubmit, isSubmitting } = useForm({
  validationSchema: loginSchema,
  initialValues: {
    email: '',
    password: '',
  },
})

const onSubmit = handleSubmit(
  async (credentials: LoginCredentials) => {
    errorMessage.value = null
    noticeMessage.value = null

    try {
      await auth.login(credentials)
      await router.push(getRedirectTarget(route.query.redirect))
    } catch (error) {
      errorMessage.value =
        error instanceof HttpError && error.status === 401
          ? authErrorMessages.loginFailed
          : authErrorMessages.unreachable
    }
  },
  () => focusFirstInvalidField(formRef.value),
)
</script>

<template>
  <form
    ref="form"
    class="flex flex-col gap-6"
    :novalidate="true"
    @submit="onSubmit"
  >
    <UiCallout
      v-if="errorMessage"
      variant="warning"
      role="alert"
    >
      {{ errorMessage }}
    </UiCallout>

    <UiCallout
      v-else-if="noticeMessage"
      variant="info"
      role="status"
    >
      {{ noticeMessage }}
    </UiCallout>

    <FormTextField
      field-name="email"
      label="E-Mail-Adresse"
      type="email"
      autocomplete="username"
      required
    />

    <FormPasswordField
      field-name="password"
      label="Passwort"
      autocomplete="current-password"
      required
    />

    <UiButton
      type="submit"
      class="w-full"
      :loading="isSubmitting"
    >
      Anmelden
    </UiButton>
  </form>
</template>
