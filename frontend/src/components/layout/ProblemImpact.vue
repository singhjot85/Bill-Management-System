<template>
  <v-container class="problem-impact-section py-16">
    <v-row justify="center" class="mb-12">
      <v-col cols="12" md="10" class="text-center">
        <h2 class="section-headline font-weight-bold mb-6">{{ config.headline }}</h2>
        <p class="section-subheadline mx-auto">{{ config.problemStatement }}</p>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="6">
        <v-card class="pa-8 problem-points-card h-100" flat>
          <div v-for="(point, index) in config.points" :key="index" class="d-flex align-start mb-6">
            <v-icon color="error" class="mr-4 mt-1" size="28">{{ point.icon }}</v-icon>
            <div class="point-text font-weight-medium">{{ point.text }}</div>
          </div>
          <v-divider class="my-6"></v-divider>
          <div class="result-text font-weight-bold color-error">
            <v-icon start color="error">mdi-alert-circle-outline</v-icon>
            {{ config.result }}
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="pa-8 solution-quote-card h-100 d-flex flex-column justify-center text-center" flat color="surface">
          <v-icon color="primary" size="64" class="mb-6 opacity-20">mdi-format-quote-open</v-icon>
          <blockquote class="solution-quote mb-6 font-italic">
            {{ config.solutionQuote }}
          </blockquote>
          <p class="font-weight-medium color-primary mb-0">Your donation makes this possible.</p>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { DonateProblemConfig } from '@/config/tenantConfig';

defineProps<{
  config: DonateProblemConfig;
}>();
</script>

<style scoped>
.section-headline {
  font-size: var(--font-size-h3);
  color: var(--text-primary);
}

.section-subheadline {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
  max-width: 700px;
}

.problem-points-card {
  background-color: rgba(var(--error-color-rgb), 0.03) !important;
  border-radius: var(--radius-xl);
  border: 1px solid rgba(var(--error-color-rgb), 0.1);
}

.solution-quote-card {
  background: linear-gradient(135deg, rgba(var(--primary-color-rgb), 0.05) 0%, rgba(var(--primary-color-rgb), 0.1) 100%) !important;
  border-radius: var(--radius-xl);
  border: 1px solid rgba(var(--primary-color-rgb), 0.1);
}

.point-text {
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

.result-text {
  font-size: var(--font-size-lg);
  color: var(--error-color);
}

.solution-quote {
  font-size: var(--font-size-xxl);
  color: var(--primary-color);
  line-height: 1.4;
}

.opacity-20 { opacity: 0.2; }
</style>
