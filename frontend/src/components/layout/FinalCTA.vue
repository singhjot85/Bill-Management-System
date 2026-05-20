<template>
  <v-container fluid class="final-cta-section py-16">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <v-card class="cta-card pa-12 text-center rounded-xl elevation-8" color="primary">
          <h2 class="cta-headline font-weight-black mb-4 text-white">
            {{ config.headline }}
          </h2>
          <p class="cta-subheadline mb-10 text-white opacity-90">
            {{ config.subheadline }}
          </p>
          <v-btn
            color="white"
            size="x-large"
            class="cta-button font-weight-bold mb-4 px-12"
            height="64"
            variant="flat"
            style="color: var(--primary-color) !important;"
          >
            {{ config.buttonText }}
          </v-btn>
          <p class="cta-fineprint text-white opacity-70 mb-0">
            {{ config.finePrint }}
          </p>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { FinalCTAConfig } from '@/config/tenantConfig';

defineProps<{
  config: FinalCTAConfig;
}>();
</script>

<style scoped>
.cta-card {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
}

.cta-headline {
  font-size: var(--font-size-h2);
  line-height: 1.2;
}

.cta-subheadline {
  font-size: var(--font-size-xl);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-button {
  border-radius: var(--radius-lg);
  font-size: var(--font-size-lg);
  text-transform: none;
}

.cta-fineprint {
  font-size: var(--font-size-sm);
}

.opacity-90 {
  opacity: 0.9;
}

.opacity-70 {
  opacity: 0.7;
}

@media (max-width: 600px) {
  .cta-headline {
    font-size: var(--font-size-h3);
  }
}
</style>
