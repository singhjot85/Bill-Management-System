<template>
  <v-container class="donation-tiers-section py-16">
    <div class="text-center mb-12">
      <h2 class="section-headline font-weight-bold mb-4">{{ config.headline }}</h2>
      <v-chip v-if="config.inventoryStatus" color="primary" variant="tonal" class="font-weight-bold">
        <v-icon start size="18">mdi-package-variant-closed</v-icon>
        {{ config.inventoryStatus }}
      </v-chip>
    </div>

    <v-row justify="center">
      <v-col v-for="(tier, index) in config.tiers" :key="index" cols="12" md="6" lg="4">
        <v-card
          :class="['tier-card pa-6 text-center h-100 d-flex flex-column', { 'highlighted-tier': index === 0 }]"
          flat
        >
          <!-- ponytail: highlight badge for the first/popular donation tier -->
          <div v-if="index === 0" class="highlight-badge mb-4">Most Popular</div>
          <div class="tier-name font-weight-bold mb-2">{{ tier.name }}</div>
          <div class="tier-amount font-weight-black color-primary mb-4">₹{{ tier.amount }}</div>
          <v-divider class="mb-4"></v-divider>
          <div class="tier-impact mb-4 flex-grow-1">{{ tier.impact }}</div>
          <div class="tier-best-for text-caption text-muted mb-4">{{ tier.bestFor }}</div>
          <v-btn
            color="primary"
            variant="flat"
            block
            class="rounded-lg font-weight-bold mt-auto"
            @click="$emit('select-tier', tier)"
          >
            Select
          </v-btn>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { DonationTiersConfig } from '@/config/tenantConfig';

defineProps<{
  config: DonationTiersConfig;
}>();

defineEmits(['select-tier']);
</script>

<style scoped>
.section-headline {
  font-size: var(--font-size-h3);
}

.tier-card {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  border: 1px solid rgba(var(--primary-color-rgb), 0.15); /* ponytail: theme-aware border */
  border-radius: var(--radius-lg);
  transition: transform 250ms var(--ease-out), box-shadow 250ms var(--ease-out), border-color 250ms var(--ease-out);
  background-color: var(--surface-color);
  position: relative;
}

.tier-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md) !important;
  border-color: var(--primary-color);
}

/* ponytail: make first/popular tier stand out visually */
.highlighted-tier {
  border: 2px solid var(--primary-color) !important;
  transform: scale(1.02);
  box-shadow: var(--shadow-sm) !important;
}

.highlighted-tier:hover {
  transform: scale(1.02) translateY(-5px);
  box-shadow: var(--shadow-md) !important;
}

.highlight-badge {
  background-color: var(--primary-color);
  color: white;
  padding: 4px 12px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: bold;
  text-transform: uppercase;
  align-self: center;
}

.tier-name {
  font-size: var(--font-size-base);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.tier-amount {
  font-size: var(--font-size-xxl);
  color: var(--primary-color);
}

.tier-impact {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  line-height: 1.4;
}
</style>
