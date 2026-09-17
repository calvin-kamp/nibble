<script setup lang="ts">
import type { RegisterCredentials } from '@interfaces/auth.types'

import { useForm } from 'vee-validate'
import { ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { FormCheckboxField, FormPasswordField, FormTextField } from '@components/form'
import { UiButton, UiCallout, UiLink } from '@components/ui'
import { HttpError } from '@lib/http'
import { useAuthStore } from '@stores/auth.store'
import { authErrorMessages } from '../auth.data'
import { registerSchema } from '../auth.schemas'
import { focusFirstInvalidField } from '../auth.utils'

type RegisterField = keyof RegisterCredentials

const REGISTER_FIELDS: RegisterField[] = ['email', 'password', 'passwordConfirm', 'tosAccepted']

const auth = useAuthStore()
const router = useRouter()

const formRef = useTemplateRef<HTMLFormElement>('form')

const errorMessage = ref<string | null>(null)

const { handleSubmit, isSubmitting, setErrors } = useForm({
  validationSchema: registerSchema,
  initialValues: {
    email: '',
    password: '',
    passwordConfirm: '',
    tosAccepted: false,
  },
})

function getFieldErrors(data: unknown): Partial<Record<RegisterField, string>> {
  if (typeof data !== 'object' || data === null) return {}

  const errors: Partial<Record<RegisterField, string>> = {}

  for (const field of REGISTER_FIELDS) {
    const messages = (data as Record<string, unknown>)[field]

    if (Array.isArray(messages) && typeof messages[0] === 'string') {
      errors[field] = field === 'email' ? authErrorMessages.emailTaken : messages[0]
    }
  }

  return errors
}

const onSubmit = handleSubmit(
  async (credentials: RegisterCredentials) => {
    errorMessage.value = null

    try {
      await auth.register(credentials)
      await router.push({ name: 'dashboard' })
    } catch (error) {
      const fieldErrors =
        error instanceof HttpError && error.status === 400 ? getFieldErrors(error.data) : {}

      if (Object.keys(fieldErrors).length === 0) {
        errorMessage.value = authErrorMessages.unreachable

        return
      }

      setErrors(fieldErrors)
      await focusFirstInvalidField(formRef.value)
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

    <FormTextField
      field-name="email"
      label="E-Mail-Adresse"
      type="email"
      autocomplete="email"
      required
    />

    <FormPasswordField
      field-name="password"
      label="Passwort"
      description="Mindestens 8 Zeichen."
      autocomplete="new-password"
      required
    />

    <FormPasswordField
      field-name="passwordConfirm"
      label="Passwort wiederholen"
      autocomplete="new-password"
      required
    />

    <FormCheckboxField
      field-name="tosAccepted"
      label="Ich akzeptiere die AGB"
      required
    >
      <template #label>
        Ich akzeptiere die

        <UiLink
          route-name="legal-tos"
          new-tab
          >AGB</UiLink
        >
      </template>
    </FormCheckboxField>

    <UiButton
      type="submit"
      class="w-full"
      :loading="isSubmitting"
    >
      Konto erstellen
    </UiButton>
  </form>
</template>
