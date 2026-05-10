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
              <span class="text-white">{{ item.author.charAt(0) }}</span>
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
  height: 100%;
  background-color: var(--surface-color);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(var(--primary-color-rgb), 0.05);
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
