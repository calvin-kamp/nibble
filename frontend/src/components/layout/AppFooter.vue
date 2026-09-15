<script setup lang="ts">
import type { FooterLink } from '@interfaces/navigation.types'

import { UiLink } from '@components/ui'
import { footerNavigation } from '@data/footer-navigation.data'
import { useAuthStore } from '@stores/auth.store'

const auth = useAuthStore()

function visibleLinks(links: FooterLink[]): FooterLink[] {
  return links.filter(
    (link) =>
      !link.visibility ||
      link.visibility === 'always' ||
      link.visibility === (auth.isLoggedIn ? 'user' : 'guest'),
  )
}

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="pt-10 pb-8 mt-auto border-t md:pt-14 lg:pt-16">
    <div class="content-wrapper flex flex-col gap-8 md:gap-10">
      <div class="flex flex-col gap-6">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="111"
          height="44"
          version="1.2"
          viewBox="0 0 110.67 43.2"
        >
          <path
            d="M19.8 22.1V34h-3.3V22.2q0-2.8-1.1-4.2-1.1-1.3-3.2-1.3-2.7 0-4.2 1.6-1.5 1.7-1.5 4.6V34H3.3V14.3h3.2v3.1q1.2-1.8 2.7-2.7 1.6-.9 3.7-.9 3.4 0 5.1 2.1 1.8 2.1 1.8 6.2M26.2 34V14.3h3.2V34zm0-23.3V6.6h3.3v4.1zm24.1 13.5q0-3.6-1.5-5.6-1.4-2.1-4-2.1t-4 2.1q-1.5 2-1.5 5.6 0 3.5 1.5 5.6 1.4 2 4 2t4-2q1.5-2.1 1.5-5.6m-11-17.6v10.7q1-1.8 2.6-2.6 1.5-.9 3.7-.9 3.6 0 5.8 2.9 2.3 2.8 2.3 7.5 0 4.6-2.3 7.5-2.2 2.8-5.8 2.8-2.2 0-3.7-.8-1.6-.9-2.6-2.7v3h-3.2V6.6zm33.8 17.6q0-3.6-1.5-5.6-1.4-2.1-4-2.1t-4 2.1q-1.5 2-1.5 5.6 0 3.5 1.5 5.6 1.4 2 4 2t4-2q1.5-2.1 1.5-5.6m-11-17.6v10.7q1-1.8 2.6-2.6 1.5-.9 3.7-.9 3.6 0 5.8 2.9 2.3 2.8 2.3 7.5 0 4.6-2.3 7.5-2.2 2.8-5.8 2.8-2.2 0-3.7-.8-1.6-.9-2.6-2.7v3h-3.2V6.6zM81.8 34V6.6H85V34zm26.9-10.7v1.6H93.8q.2 3.4 2 5.1 1.8 1.8 5 1.8 1.9 0 3.6-.5 1.8-.4 3.5-1.4V33q-1.7.7-3.6 1.1-1.8.4-3.7.4-4.7 0-7.4-2.7-2.8-2.8-2.8-7.5 0-4.8 2.6-7.6 2.6-2.9 7.1-2.9 3.9 0 6.2 2.6 2.4 2.6 2.4 6.9m-14.8-.9h11.5q0-2.7-1.5-4.2-1.4-1.6-3.8-1.6-2.7 0-4.3 1.5-1.7 1.5-1.9 4.3"
            aria-label="nibble"
          />
        </svg>

        <div class="flex flex-col gap-4 max-w-prose text-muted-foreground">
          <p>Kalorien, Makros und Rezepte an einem Ort.</p>

          <p class="text-sm text-balance">
            Nibble ersetzt keine ärztliche oder ernährungstherapeutische Beratung. Alle berechneten
            Werte sind Schätzungen.
          </p>
        </div>
      </div>

      <div class="grid gap-8 md:grid-cols-2 lg:gap-12">
        <nav
          v-for="footerGroup in footerNavigation"
          :key="footerGroup.id"
          :aria-labelledby="footerGroup.id"
          class="flex flex-col gap-2"
        >
          <h2
            :id="footerGroup.id"
            class="text-base text-foreground font-semibold"
          >
            {{ footerGroup.title }}
          </h2>

          <ul>
            <li
              v-for="link in visibleLinks(footerGroup.links)"
              :key="link.label"
            >
              <UiLink
                :route-name="link.routeName"
                :hash="link.hash"
                variant="standalone"
              >
                {{ link.label }}
              </UiLink>
            </li>
          </ul>
        </nav>
      </div>

      <div
        class="flex flex-col gap-1 pt-4 border-t md:flex-row md:items-center md:justify-between md:pt-5"
      >
        <p class="text-muted-foreground">&copy; {{ currentYear }} Nibble</p>

        <UiLink
          href="#body"
          variant="standalone"
        >
          Nach oben
        </UiLink>
      </div>
    </div>
  </footer>
</template>
