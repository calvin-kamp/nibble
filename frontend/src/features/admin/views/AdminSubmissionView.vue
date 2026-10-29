<script setup lang="ts">
import type { SubmissionDetail } from '@features/admin/admin.types'
import type { RecipeFact } from '@features/recipes/recipes.types'

import { CheckIcon, XIcon } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import RecipeMedia from '@features/recipes/components/RecipeMedia.vue'
import NutritionCard from '@features/tracking/components/NutritionCard.vue'
import {
	BaseActions,
	BaseAlertDialog,
	BaseBreadcrumb,
	BaseButton,
	BaseCard,
	BaseDialog,
	BaseIcon,
} from '@shared/ui'

import { usePageTitle } from '@shared/composables/page-title'
import { useToast } from '@shared/composables/toast'

import { approveSubmission, fetchSubmission, rejectSubmission } from '@features/admin/admin.api'
import {
	MAX_REJECTION_REASON_LENGTH,
	STATUS_QUERY,
	SUBMISSION_KIND_LABELS,
	SUBMISSION_STATUS_LABELS,
} from '@features/admin/admin.constants'
import { rejectSchema } from '@features/admin/admin.schema'
import { changedFields, formatTimestamp } from '@features/admin/admin.utils'
import { formatAmount, recipeFacts, recipeParams } from '@features/recipes/recipes.utils'
import { ApiError } from '@shared/api/client'
import { focusFirstError, TextareaField } from '@shared/forms'

interface Props {
	id: string
}

const props = defineProps<Props>()

const router = useRouter()
const toast = useToast()

// undefined: still loading, null: does not exist or could not be loaded
const submission = ref<SubmissionDetail | null | undefined>(undefined)

usePageTitle(() => submission.value?.title)

async function load(id: string): Promise<void> {
	submission.value = undefined

	try {
		submission.value = await fetchSubmission(id)
	} catch {
		submission.value = null
	}
}

watch(() => props.id, load, { immediate: true })

const content = computed(() => submission.value?.content)

const facts = computed<RecipeFact[]>(() => (content.value ? recipeFacts(content.value) : []))

// Revisions only: what differs from the version everyone currently sees
const changes = computed<string>(() => {
	const current = submission.value?.current

	if (!content.value || !current) return ''

	return changedFields(content.value, current)
		.map((change) => change.label)
		.join(', ')
})

const meta = computed<string>(() => {
	if (!submission.value) return ''

	const { author, kind, submittedAt } = submission.value
	const by = author ? `von ${author}` : 'Konto inzwischen gelöscht'

	return `${SUBMISSION_KIND_LABELS[kind]} ${by}, eingereicht am ${formatTimestamp(submittedAt)}`
})

const isPending = computed<boolean>(() => submission.value?.status === 'pending')

const backLocation = computed(() => ({
	label: 'Verwaltung',
	routeName: 'admin',
	query: submission.value ? { status: STATUS_QUERY[submission.value.status] } : undefined,
}))

const isDeciding = ref<boolean>(false)

/** Someone else may have decided in the meantime; then the page shows their decision */
async function decide(action: () => Promise<SubmissionDetail>, message: string): Promise<void> {
	isDeciding.value = true

	try {
		await action()
		toast.show(message)
		await router.push({ name: 'admin' })
	} catch (error) {
		if (error instanceof ApiError && error.code === 'submission_not_pending') {
			toast.show('Diese Einreichung wurde inzwischen schon bearbeitet.', 'info')
			await load(props.id)
		} else {
			toast.show('Das hat nicht geklappt. Versuch es bitte noch einmal.', 'danger')
		}
	} finally {
		isDeciding.value = false
	}
}

const approveOpen = ref<boolean>(false)

function onApprove(): void {
	void decide(() => approveSubmission(props.id), 'Freigegeben. Der Autor bekommt eine E-Mail.')
}

const rejectOpen = ref<boolean>(false)

const { handleSubmit, resetForm } = useForm({ validationSchema: rejectSchema })

const onReject = handleSubmit(
	async ({ reason }) => {
		rejectOpen.value = false
		await decide(
			() => rejectSubmission(props.id, reason),
			'Abgelehnt. Der Autor bekommt die Begründung per E-Mail.',
		)
	},
	({ evt }) => focusFirstError(evt),
)

watch(rejectOpen, (open) => {
	if (open) resetForm()
})
</script>

<template>
	<main
		v-if="submission && content"
		class="content-wrapper flex flex-col gap-6 pt-4 pb-10"
	>
		<div class="flex flex-col gap-4">
			<BaseBreadcrumb
				:items="[backLocation]"
				:current="submission.title"
			/>

			<RecipeMedia
				class="aspect-4/3 rounded-xl bg-lime md:aspect-21/9"
				:image-url="submission.imageUrl"
			/>
		</div>

		<div class="flex flex-col gap-5">
			<div class="flex flex-col gap-2">
				<h1 class="wrap-break-word">
					{{ content.title }}
				</h1>

				<p class="text-muted">
					{{ meta }}
				</p>
			</div>

			<p
				v-if="submission.current"
				class="notice notice--info"
			>
				Änderung an einem freigegebenen Rezept.
				{{ changes ? `Geändert: ${changes}.` : 'Nur das Foto ist neu.' }}

				<RouterLink
					class="link link--inline"
					:to="{
						name: 'recipe-detail',
						params: recipeParams({
							id: submission.recipeId,
							title: submission.current.title,
						}),
					}"
				>
					Aktuelle Fassung ansehen
				</RouterLink>
			</p>

			<p
				v-if="!isPending"
				class="notice"
				:class="submission.status === 'rejected' ? 'notice--danger' : 'notice--info'"
			>
				{{ SUBMISSION_STATUS_LABELS[submission.status] }}
				{{ submission.reviewedBy ? `von ${submission.reviewedBy}` : '' }}
				{{ submission.reviewedAt ? `am ${formatTimestamp(submission.reviewedAt)}` : '' }}.
				{{ submission.rejectionReason ? `Begründung: ${submission.rejectionReason}` : '' }}
			</p>

			<p
				v-if="content.description"
				class="max-w-3xl text-lg text-ink-soft"
			>
				{{ content.description }}
			</p>

			<dl class="flex flex-col gap-4 py-5 border-y border-divider md:flex-row md:gap-6">
				<div
					v-for="fact in facts"
					:key="fact.label"
					class="flex flex-col gap-0.5 min-w-0 md:flex-1"
				>
					<dt class="text-sm text-muted">
						{{ fact.label }}
					</dt>

					<dd class="font-bold">
						{{ fact.value }}
					</dd>
				</div>
			</dl>
		</div>

		<NutritionCard
			title="Nährwerte pro Portion"
			:nutrition="{
				kcal: content.kcalPerServing,
				protein: content.protein,
				carbs: content.carbs,
				fat: content.fat,
			}"
		/>

		<div class="grid grid-cols-12 gap-10 xl:items-start xl:gap-6">
			<BaseCard
				as="section"
				class="col-span-12 xl:col-span-5"
				aria-labelledby="submission-ingredients-title"
			>
				<div class="flex flex-col gap-4">
					<div class="flex flex-col gap-1">
						<h2
							id="submission-ingredients-title"
							class="text-2xl"
						>
							Zutaten
						</h2>

						<p class="text-muted">
							Für {{ content.servings }}
							{{ content.servings === 1 ? 'Portion' : 'Portionen' }}
						</p>
					</div>

					<ul class="data-list">
						<li
							v-for="(ingredient, index) in content.ingredients"
							:key="index"
							class="data-list__row"
						>
							<span class="data-list__label">{{ ingredient.name }}</span>

							<span class="data-list__value">
								{{
									formatAmount(
										ingredient.amount,
										ingredient.unit,
										content.servings,
										content.servings,
									)
								}}
							</span>
						</li>
					</ul>
				</div>
			</BaseCard>

			<section
				class="flex flex-col gap-5 col-span-12 xl:col-span-7 xl:pt-5"
				aria-labelledby="submission-steps-title"
			>
				<h2
					id="submission-steps-title"
					class="text-2xl"
				>
					Zubereitung
				</h2>

				<ol class="flex flex-col gap-4 pl-6 list-decimal marker:font-bold marker:text-leaf">
					<li
						v-for="(step, index) in content.steps"
						:key="index"
						class="pl-2 leading-relaxed"
					>
						{{ step }}
					</li>
				</ol>
			</section>
		</div>

		<BaseActions
			v-if="isPending"
			class="sticky bottom-20 z-10 p-4 rounded-lg bg-surface shadow-lg xl:bottom-6"
		>
			<BaseButton
				:disabled="isDeciding"
				aria-haspopup="dialog"
				@click="approveOpen = true"
			>
				<BaseIcon :icon="CheckIcon" />
				Freigeben
			</BaseButton>

			<BaseButton
				variant="outline"
				:disabled="isDeciding"
				aria-haspopup="dialog"
				@click="rejectOpen = true"
			>
				<BaseIcon :icon="XIcon" />
				Ablehnen
			</BaseButton>
		</BaseActions>

		<BaseAlertDialog
			v-model:open="approveOpen"
			title="Rezept freigeben?"
			:description="
				submission.current
					? 'Die Änderung ersetzt die aktuelle Fassung, und der Autor bekommt eine E-Mail.'
					: 'Das Rezept wird für alle sichtbar, und der Autor bekommt eine E-Mail.'
			"
			confirm-label="Freigeben"
			@confirm="onApprove"
		/>

		<BaseDialog
			v-model:open="rejectOpen"
			title="Rezept ablehnen"
			description="Der Autor bekommt deine Begründung per E-Mail und sieht sie beim Rezept."
		>
			<form
				class="flex flex-col gap-5"
				novalidate
				@submit="onReject"
			>
				<TextareaField
					name="reason"
					label="Begründung"
					:hint="`Höchstens ${MAX_REJECTION_REASON_LENGTH} Zeichen.`"
				/>

				<BaseActions>
					<BaseButton
						type="submit"
						variant="danger"
					>
						Ablehnen
					</BaseButton>

					<BaseButton
						variant="ghost"
						@click="rejectOpen = false"
					>
						Abbrechen
					</BaseButton>
				</BaseActions>
			</form>
		</BaseDialog>
	</main>

	<main
		v-else-if="submission === null"
		class="content-wrapper flex flex-col gap-4 pt-6 pb-10"
	>
		<h1>Einreichung nicht gefunden</h1>

		<p class="text-lg text-muted">Vielleicht wurde das Rezept inzwischen gelöscht.</p>

		<BaseButton
			class="self-start"
			route-name="admin"
		>
			Zur Verwaltung
		</BaseButton>
	</main>

	<main
		v-else
		class="content-wrapper"
		aria-busy="true"
	/>
</template>
