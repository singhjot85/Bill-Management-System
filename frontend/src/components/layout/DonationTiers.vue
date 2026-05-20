<template>
  <v-container class="donation-tiers-section py-16">
    <div class="text-center mb-12">
      <h2 class="section-headline font-weight-bold mb-4">{{ config.headline }}</h2>
      <v-chip v-if="config.inventoryStatus" color="primary" variant="tonal" class="font-weight-bold">
        <v-icon start size="18">mdi-package-variant-closed</v-icon>
        {{ config.inventoryStatus }}
      </v-chip>
    </div>

    <v-row>
      <v-col v-for="(tier, index) in config.tiers" :key="index" cols="12" md="4" lg="2.4">
        <v-card class="tier-card pa-6 text-center h-100 d-flex flex-column" flat>
          <div class="tier-name font-weight-bold mb-2">{{ tier.name }}</div>
          <div class="tier-amount font-weight-black color-primary mb-4">₹{{ tier.amount }}</div>
          <v-divider class="mb-4"></v-divider>
          <div class="tier-impact mb-4 flex-grow-1">{{ tier.impact }}</div>
          <div class="tier-best-for text-caption text-muted mb-4">{{ tier.bestFor }}</div>
          <v-btn
            color="primary"
            variant="flat"
            block
            class="rounded-lg font-weight-bold"
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
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
  background-color: var(--surface-color);
}

.tier-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md) !important;
  border-color: var(--primary-color);
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
