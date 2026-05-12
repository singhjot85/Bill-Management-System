<template>
  <v-container class="transparency-section py-16">
    <v-row justify="center" class="text-center mb-12">
      <v-col cols="12" md="10">
        <h2 class="section-headline font-weight-black mb-4">{{ config.headline }}</h2>
        <p class="section-subheadline mx-auto font-weight-medium">{{ config.subheadline }}</p>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-for="(step, index) in config.steps" :key="index" cols="12" sm="6" md="3">
        <div class="step-card text-center pa-6 h-100 d-flex flex-column">
          <div class="step-number mb-4 mx-auto font-weight-black">{{ index + 1 }}</div>
          <h3 class="step-title font-weight-bold mb-3">{{ step.title }}</h3>
          <p class="step-description mb-0">{{ step.description }}</p>
          <v-icon v-if="index < config.steps.length - 1" class="step-arrow d-none d-md-block" size="32" color="primary">mdi-chevron-right</v-icon>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { TransparencyConfig } from '@/config/tenantConfig';

defineProps<{
  config: TransparencyConfig;
}>();
</script>

<style scoped>
.section-headline {
  font-size: var(--font-size-h3);
}

.section-subheadline {
  font-size: var(--font-size-lg);
  color: var(--primary-color);
  max-width: 600px;
}

.step-card {
  position: relative;
}

.step-number {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
}

.step-title {
  font-size: var(--font-size-base);
  text-transform: uppercase;
  color: var(--text-primary);
}

.step-description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

.step-arrow {
  position: absolute;
  top: 30px;
  right: -16px;
  opacity: 0.3;
}
</style>
