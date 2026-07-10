<template>
  <v-container class="testimonials-section py-16">
    <v-row>
      <v-col v-for="(item, index) in config.items" :key="index" cols="12" md="6">
        <v-card class="testimonial-card pa-8 elevation-2" flat>
          <v-icon color="primary" size="48" class="mb-4">mdi-format-quote-open</v-icon>
          <p class="testimonial-quote mb-6 font-italic">
            {{ item.quote }}
          </p>
          <div class="d-flex align-center">
            <v-avatar color="primary" size="48" class="mr-4">
              <!-- ponytail: replace letter avatar with a clean, modern default icon avatar -->
              <v-icon color="white" size="24">mdi-account-circle-outline</v-icon>
            </v-avatar>
            <div>
              <div class="author-name font-weight-bold">{{ item.author }}</div>
              <div class="author-role">{{ item.role }}</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { TestimonialsConfig } from '@/config/tenantConfig';

defineProps<{
  config: TestimonialsConfig;
}>();
</script>

<style scoped>
.testimonial-card {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  height: 100%;
  background-color: var(--surface-color);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(var(--primary-color-rgb), 0.15);
  transition: transform 250ms var(--ease-out), box-shadow 250ms var(--ease-out);
}

.testimonial-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md) !important;
}

.testimonial-quote {
  font-size: var(--font-size-lg);
  color: var(--text-primary);
  line-height: 1.6;
}

.author-name {
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.author-role {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
</style>
