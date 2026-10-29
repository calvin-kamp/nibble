<script setup lang="ts">
import OperatorAddress from '@features/legal/components/OperatorAddress.vue'
import PolicySection from '@features/legal/components/PolicySection.vue'
import { BaseLink } from '@shared/ui'

import { OPERATOR } from '@features/legal/legal.constants'

// Impressum per § 5 DDG. The details come from OPERATOR in legal.constants.ts.
const SECTIONS = {
	provider: { id: 'anbieter', title: 'Angaben gemäß § 5 DDG' },
	contact: { id: 'kontakt', title: 'Kontakt' },
	tax: { id: 'umsatzsteuer', title: 'Umsatzsteuer' },
	editorial: { id: 'verantwortlich', title: 'Verantwortlich für den Inhalt' },
	dispute: { id: 'streitbeilegung', title: 'Verbraucherstreitbeilegung' },
	content: { id: 'haftung', title: 'Haftung für Inhalte und Links' },
	sources: { id: 'datenquellen', title: 'Datenquellen' },
}
</script>

<template>
	<main class="content-wrapper pt-6 pb-10">
		<article class="legal">
			<div class="legal__header">
				<h1>Impressum</h1>
			</div>

			<PolicySection :section="SECTIONS.provider">
				<OperatorAddress />
			</PolicySection>

			<PolicySection :section="SECTIONS.contact">
				<dl class="grid grid-cols-12 gap-x-4 gap-y-1">
					<dt class="col-span-3 font-bold sm:col-span-2">E-Mail</dt>

					<dd class="col-span-9 sm:col-span-10">
						<BaseLink
							:href="`mailto:${OPERATOR.email}`"
							variant="inline"
						>
							{{ OPERATOR.email }}
						</BaseLink>
					</dd>

					<template v-if="OPERATOR.phone">
						<dt class="col-span-3 font-bold sm:col-span-2">Telefon</dt>

						<dd class="col-span-9 sm:col-span-10">
							<BaseLink
								:href="`tel:${OPERATOR.phone.replace(/[^\d+]/g, '')}`"
								variant="inline"
							>
								{{ OPERATOR.phone }}
							</BaseLink>
						</dd>
					</template>
				</dl>
			</PolicySection>

			<PolicySection
				v-if="OPERATOR.vatId"
				:section="SECTIONS.tax"
			>
				<p>
					Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz:
					{{ OPERATOR.vatId }}
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.editorial">
				<p>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV:</p>

				<OperatorAddress />
			</PolicySection>

			<PolicySection :section="SECTIONS.dispute">
				<p>
					Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor
					einer Verbraucherschlichtungsstelle teilzunehmen.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.content">
				<p>
					Wir erstellen die Inhalte von Nibble mit Sorgfalt. Die Werte aus Kalorienrechner
					und Tagebuch sind Schätzungen zur Orientierung und ersetzen keine ärztliche oder
					ernährungsfachliche Beratung.
				</p>

				<p>
					Rezepte reichen Nutzerinnen und Nutzer ein. Wir prüfen sie vor der
					Veröffentlichung, machen uns ihren Inhalt aber nicht zu eigen. Erfahren wir von
					einem Rechtsverstoß, entfernen wir den Inhalt umgehend. Schreib uns dazu an die
					oben genannte Adresse.
				</p>

				<p>
					Für die Inhalte verlinkter fremder Websites sind ausschließlich deren Betreiber
					verantwortlich. Zum Zeitpunkt der Verlinkung waren keine Rechtsverstöße
					erkennbar.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.sources">
				<p>
					Die Lebensmitteldaten stammen von
					<BaseLink
						href="https://world.openfoodfacts.org"
						variant="inline"
					>
						Open Food Facts
					</BaseLink>

					und stehen unter der

					<BaseLink
						href="https://opendatacommons.org/licenses/odbl/1-0/"
						variant="inline"
					>
						Open Database License
					</BaseLink>

					.
				</p>
			</PolicySection>
		</article>
	</main>
</template>
