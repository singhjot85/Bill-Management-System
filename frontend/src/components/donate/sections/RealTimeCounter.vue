<template>
  <v-container fluid class="counter-section py-16 text-center" color="surface">
    <v-row justify="center">
      <v-col v-for="(item, index) in config.items" :key="index" cols="6" md="3">
        <div class="counter-item">
          <div class="counter-value font-weight-black mb-2">{{ item.value }}</div>
          <div class="counter-label text-caption text-uppercase font-weight-bold">{{ item.label }}</div>
        </div>
      </v-col>
    </v-row>
    <v-row justify="center" class="mt-12">
      <v-col cols="auto">
        <v-btn
          color="primary"
          size="x-large"
          class="rounded-xl font-weight-black px-12"
          height="64"
          @click="$emit('donate-click', config.cta.amount)"
        >
          {{ config.cta.text }} – ₹{{ config.cta.amount }}
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { RealTimeCounterConfig } from '@/config/tenantConfig';

defineProps<{
  config: RealTimeCounterConfig;
}>();

defineEmits(['donate-click']);
</script>

<style scoped>
.counter-section {
  background-color: var(--surface-color);
  border-top: 1px solid rgba(0,0,0,0.05);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.counter-value {
  font-size: var(--font-size-h2);
  color: var(--primary-color);
  line-height: 1;
}

.counter-label {
  color: var(--text-secondary);
  letter-spacing: 1px;
}

@media (max-width: 600px) {
  .counter-value {
    font-size: var(--font-size-h3);
  }
}
</style>
