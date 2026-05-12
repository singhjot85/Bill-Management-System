<template>
  <v-container class="faq-section py-16">
    <h2 class="section-headline text-center font-weight-black mb-12">Frequently Asked Questions</h2>
    <v-row justify="center">
      <v-col cols="12" md="10">
        <v-expansion-panels variant="inset" class="custom-panels">
          <v-expansion-panel
            v-for="(item, index) in config.items"
            :key="index"
            :title="item.question"
            :text="item.answer"
            elevation="0"
          >
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { FAQConfig } from '@/config/tenantConfig';

defineProps<{
  config: FAQConfig;
}>();
</script>

<style scoped>
.section-headline {
  font-size: var(--font-size-h3);
}

.custom-panels :deep(.v-expansion-panel) {
  background-color: transparent !important;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  border-radius: 0 !important;
}

.custom-panels :deep(.v-expansion-panel-title) {
  font-size: var(--font-size-lg);
  font-weight: 700;
  padding: var(--spacing-lg) 0;
  color: var(--text-primary);
}

.custom-panels :deep(.v-expansion-panel-text) {
  color: var(--text-secondary);
  font-size: var(--font-size-base);
  line-height: 1.6;
  padding-bottom: var(--spacing-lg);
}

.custom-panels :deep(.v-expansion-panel--active) {
  margin-top: 0 !important;
}
</style>
