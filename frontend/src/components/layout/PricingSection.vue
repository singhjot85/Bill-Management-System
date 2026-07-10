<template>
  <v-container class="pricing-section py-16">
    <v-row justify="center" class="text-center mb-12">
      <v-col cols="12">
        <h2 class="section-headline font-weight-bold">
          {{ config.headline || 'Simple Tiering' }}
        </h2>
      </v-col>
    </v-row>
    <v-row align="stretch">
      <v-col
        v-for="(tier, index) in config.tiers"
        :key="index"
        cols="12"
        :md="config.tiers && config.tiers.length === 3 ? (tier.popular ? 5 : (index === 0 ? 3 : 4)) : 4"
      >
        <v-card
          :class="['pricing-card pa-8 text-center d-flex flex-column', { 'popular-tier': tier.popular }]"
          flat
        >
          <div v-if="tier.popular" class="popular-badge mb-4">Most Popular</div>
          <h3 class="tier-name mb-4">{{ tier.name }}</h3>
          <div class="tier-price mb-6 font-weight-black">{{ tier.price }}</div>
          <v-divider class="mb-6"></v-divider>
          <ul class="tier-features mb-8 text-left flex-grow-1">
            <li v-for="(feature, fIndex) in tier.features" :key="fIndex" class="mb-2">
              <v-icon color="success" size="20" class="mr-2">mdi-check</v-icon>
              <span>{{ feature }}</span>
            </li>
          </ul>
          <v-btn
            :color="tier.popular ? 'primary' : 'secondary'"
            size="large"
            block
            class="rounded-lg font-weight-bold"
            variant="flat"
          >
            Get Started
          </v-btn>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { PricingConfig } from '@/config/tenantConfig';

defineProps<{
  config: PricingConfig;
}>();
</script>

<style scoped>
.section-headline {
  font-size: var(--font-size-h3);
  color: var(--text-primary);
}

.pricing-card {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  height: 100%;
  border-radius: var(--radius-lg);
  background-color: var(--surface-color);
  border: 1px solid rgba(var(--primary-color-rgb), 0.15); /* ponytail: theme-aware border */
  transition: transform 250ms var(--ease-out), box-shadow 250ms var(--ease-out), border-color 250ms var(--ease-out);
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg) !important;
}

.popular-tier {
  border: 2px solid var(--primary-color) !important;
  position: relative;
  transform: scale(1.03);
  box-shadow: var(--shadow-md) !important;
  z-index: 1;
}

.popular-tier:hover {
  transform: scale(1.03) translateY(-5px);
  box-shadow: var(--shadow-lg) !important;
}

.popular-badge {
  background-color: var(--primary-color);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: bold;
  text-transform: uppercase;
  display: inline-block;
}

.tier-name {
  font-size: var(--font-size-xl);
  color: var(--text-primary);
}

.tier-price {
  font-size: var(--font-size-h3);
  color: var(--primary-color);
}

.tier-features {
  list-style: none;
  padding: 0;
}

.tier-features li {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
}
</style>
