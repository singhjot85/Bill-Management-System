<template>
  <v-container class="features-grid-section py-16">
    <v-row>
      <v-col
        v-for="(feature, index) in config.features"
        :key="index"
        cols="12"
        sm="6"
        lg="3"
      >
        <v-card class="feature-card pa-6 text-center" flat>
          <div class="icon-container mb-4">
            <v-icon size="40" color="primary">{{ feature.icon }}</v-icon>
          </div>
          <h3 class="feature-title mb-2 font-weight-bold">{{ feature.title }}</h3>
          <p class="feature-text mb-0">{{ feature.text }}</p>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { FeaturesGridConfig } from '@/config/tenantConfig';

defineProps<{
  config: FeaturesGridConfig;
}>();
</script>

<style scoped>
.features-grid-section {
  background-color: var(--background-color);
}

.feature-card {
  height: 100%;
  border-radius: var(--radius-lg);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: var(--surface-color);
  border: 1px solid rgba(var(--primary-color-rgb), 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg) !important;
}

.icon-container {
  width: 64px;
  height: 64px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(var(--primary-color-rgb), 0.1);
  border-radius: var(--radius-md);
}

.feature-title {
  font-size: var(--font-size-xl);
  color: var(--text-primary);
}

.feature-text {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  line-height: 1.5;
}
</style>
