<template>
  <v-container fluid class="hero-section py-16">
    <v-row justify="center" align="center" class="text-center">
      <v-col cols="12" md="10" lg="8">
        <h1 class="hero-headline font-weight-black mb-6">
          {{ config.headline }}
        </h1>
        <p class="hero-subheadline mb-10">
          {{ config.subheadline }}
        </p>
        <v-btn
          color="primary"
          size="x-large"
          class="hero-cta font-weight-bold elevation-4"
          :to="config.primaryCTA.to"
        >
          {{ config.primaryCTA.text }}
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { HeroSectionConfig } from '@/config/tenantConfig';

defineProps<{
  config: HeroSectionConfig;
}>();
</script>

<style scoped>
.hero-section {
  padding-top: var(--spacing-xxl);
  padding-bottom: var(--spacing-xxl);
  background: radial-gradient(circle at 50% -20%, var(--primary-color) 0%, transparent 70%);
  opacity: 0.9; /* Subtle overlay effect */
}

.hero-headline {
  font-size: var(--font-size-h2);
  line-height: 1.1;
  color: var(--text-primary);
}

.hero-subheadline {
  font-size: var(--font-size-xxl);
  line-height: 1.6;
  color: var(--text-secondary);
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.hero-cta {
  height: 72px;
  padding: 0 var(--spacing-xl);
  font-size: var(--font-size-lg);
  border-radius: var(--radius-lg);
  text-transform: none;
}

@media (max-width: 960px) {
  .hero-headline {
    font-size: var(--font-size-h3);
  }
  .hero-subheadline {
    font-size: var(--font-size-xl);
  }
}
</style>
