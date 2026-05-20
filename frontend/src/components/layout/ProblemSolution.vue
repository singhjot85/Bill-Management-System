<template>
  <v-container class="problem-solution-section py-16">
    <v-row justify="center" class="text-center mb-12">
      <v-col cols="12" md="10">
        <h2 class="section-headline font-weight-bold">{{ config.headline }}</h2>
      </v-col>
    </v-row>
    <v-row>
      <!-- Problem Column -->
      <v-col cols="12" md="6">
        <v-card class="pa-8 problem-card" flat>
          <h3 class="column-title mb-6">{{ config.problem.title }}</h3>
          <ul class="item-list">
            <li v-for="(item, index) in config.problem.items" :key="index" class="mb-4">
              <v-icon color="error" class="mr-2">mdi-close-circle-outline</v-icon>
              <span>{{ item }}</span>
            </li>
          </ul>
        </v-card>
      </v-col>
      <!-- Solution Column -->
      <v-col cols="12" md="6">
        <v-card class="pa-8 solution-card" flat>
          <h3 class="column-title mb-6">{{ config.solution.title }}</h3>
          <div v-for="(item, index) in config.solution.items" :key="index" class="mb-6">
            <div class="d-flex align-center mb-1">
              <v-icon color="success" class="mr-2">mdi-check-circle</v-icon>
              <span class="solution-item-title font-weight-bold">{{ item.title }}</span>
            </div>
            <p class="solution-item-text ml-8 mb-0">{{ item.text }}</p>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { ProblemSolutionConfig } from '@/config/tenantConfig';

defineProps<{
  config: ProblemSolutionConfig;
}>();
</script>

<style scoped>
.problem-solution-section {
  background-color: var(--background-color);
}

.section-headline {
  font-size: var(--font-size-h3);
  color: var(--text-primary);
}

.problem-card {
  background-color: rgba(var(--error-color-rgb, 255, 82, 82), 0.05) !important;
  border-radius: var(--radius-lg);
  height: 100%;
}

.solution-card {
  background-color: rgba(var(--success-color-rgb, 76, 175, 80), 0.05) !important;
  border-radius: var(--radius-lg);
  height: 100%;
}

.column-title {
  font-size: var(--font-size-xxl);
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.item-list {
  list-style: none;
  padding: 0;
}

.item-list li {
  display: flex;
  align-items: flex-start;
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
}

.solution-item-title {
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

.solution-item-text {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
}
</style>
