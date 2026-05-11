<template>
  <v-container fluid class="recurring-section py-16">
    <v-row justify="center">
      <v-col cols="12" md="10">
        <v-card class="recurring-card pa-12 rounded-xl elevation-4" color="surface">
          <v-row align="center">
            <v-col cols="12" md="7">
              <h2 class="headline font-weight-black mb-4 color-primary">{{ config.headline }}</h2>
              <p class="body-text mb-8">{{ config.body }}</p>
              
              <div class="benefits-grid">
                <div v-for="(benefit, index) in config.benefits" :key="index" class="benefit-item d-flex align-center mb-4">
                  <v-icon color="primary" class="mr-3" size="24">{{ benefit.icon }}</v-icon>
                  <span class="font-weight-medium">{{ benefit.text }}</span>
                </div>
              </div>
            </v-col>
            <v-col cols="12" md="5" class="text-center">
              <v-sheet class="pa-8 rounded-xl bg-primary-light text-center border">
                <v-icon color="primary" size="64" class="mb-4">mdi-calendar-sync</v-icon>
                <div class="text-h6 font-weight-bold mb-6">Sustainable Impact</div>
                <v-btn
                  color="primary"
                  size="x-large"
                  block
                  class="rounded-lg font-weight-black"
                  height="64"
                >
                  {{ config.cta }}
                </v-btn>
              </v-sheet>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
interface RecurringConfig {
  headline: string;
  body: string;
  benefits: { icon: string; text: string }[];
  cta: string;
}

defineProps<{
  config: RecurringConfig;
}>();
</script>

<style scoped>
.recurring-section {
  background-color: var(--background-color);
}

.recurring-card {
  border: 1px solid rgba(var(--primary-color-rgb), 0.1);
}

.headline {
  font-size: var(--font-size-h3);
  line-height: 1.2;
}

.body-text {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
}

.bg-primary-light {
  background-color: rgba(var(--primary-color-rgb), 0.05) !important;
}

.benefit-item {
  font-size: var(--font-size-base);
  color: var(--text-primary);
}
</style>
