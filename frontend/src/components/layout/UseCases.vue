<template>
  <v-container class="use-cases-section py-16">
    <v-row v-for="(item, index) in config.items" :key="index" class="mb-16 align-center" :class="{ 'flex-row-reverse': index % 2 !== 0 }">
      <v-col cols="12" md="6">
        <div class="use-case-content pa-8">
          <h3 class="use-case-title font-weight-bold mb-4">{{ item.title }}</h3>
          <blockquote class="use-case-quote font-italic mb-6">
            "{{ item.quote }}"
          </blockquote>
          <p class="use-case-description">
            {{ item.description }}
          </p>
        </div>
      </v-col>
      <v-col cols="12" md="6">
        <v-sheet class="use-case-visual d-flex align-center justify-center rounded-xl elevation-2" height="300" color="surface">
          <v-icon size="120" color="primary" opacity="0.2">mdi-chart-areaspline</v-icon>
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { UseCasesConfig } from '@/config/tenantConfig';

defineProps<{
  config: UseCasesConfig;
}>();
</script>

<style scoped>
.use-case-title {
  font-size: var(--font-size-h3);
  color: var(--text-primary);
}

.use-case-quote {
  font-size: var(--font-size-xl);
  color: var(--primary-color);
  border-left: 4px solid var(--primary-color);
  padding-left: var(--spacing-md);
}

.use-case-description {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
  line-height: 1.7;
}

.use-case-visual {
  background: linear-gradient(135deg, rgba(var(--primary-color-rgb), 0.05) 0%, rgba(var(--primary-color-rgb), 0.1) 100%);
  border: 1px solid rgba(var(--primary-color-rgb), 0.1);
}
</style>
