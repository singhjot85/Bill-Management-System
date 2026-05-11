<template>
  <v-container fluid class="donate-hero py-16">
    <v-row justify="center" align="center">
      <v-col cols="12" md="10" lg="8" class="text-center">
        <v-img :src="config.image" class="rounded-xl mb-10 elevation-8 mx-auto" max-height="400" cover></v-img>
        <h1 class="hero-headline font-weight-black mb-6">{{ config.headline }}</h1>
        <p class="hero-subheadline mb-10 mx-auto">{{ config.subheadline }}</p>
        
        <div class="d-flex flex-wrap justify-center gap-4 mb-10">
          <v-btn
            color="primary"
            size="x-large"
            class="hero-cta font-weight-bold"
            height="64"
            @click="$emit('action', config.primaryCTA.action)"
          >
            {{ config.primaryCTA.text }}
          </v-btn>
          <v-btn
            variant="outlined"
            size="x-large"
            class="hero-cta-secondary font-weight-bold"
            height="64"
            :href="config.secondaryCTA.url"
          >
            <v-icon start>mdi-play-circle-outline</v-icon>
            {{ config.secondaryCTA.text }}
          </v-btn>
        </div>

        <div class="trust-badges d-flex flex-wrap justify-center gap-6">
          <div v-for="(badge, index) in config.trustBadges" :key="index" class="trust-badge d-flex align-center">
            <v-icon color="success" class="mr-2">{{ badge.icon || 'mdi-check-decagram' }}</v-icon>
            <span class="font-weight-medium">{{ badge.text }}</span>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type { DonateHeroConfig } from '@/config/tenantConfig';

defineProps<{
  config: DonateHeroConfig;
}>();

defineEmits(['action']);
</script>

<style scoped>
.donate-hero {
  background: radial-gradient(circle at 50% 0%, rgba(var(--primary-color-rgb), 0.05) 0%, transparent 70%);
}

.hero-headline {
  font-size: var(--font-size-h2);
  line-height: 1.2;
  color: var(--text-primary);
}

.hero-subheadline {
  font-size: var(--font-size-xl);
  line-height: 1.6;
  color: var(--text-secondary);
  max-width: 800px;
}

.hero-cta {
  border-radius: var(--radius-lg);
  text-transform: none;
  font-size: var(--font-size-lg);
  padding: 0 var(--spacing-xl);
}

.hero-cta-secondary {
  border-radius: var(--radius-lg);
  text-transform: none;
  font-size: var(--font-size-lg);
  color: var(--text-primary);
  border-color: rgba(0,0,0,0.1);
}

.gap-4 { gap: var(--spacing-md); }
.gap-6 { gap: var(--spacing-lg); }

.trust-badge {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
}

@media (max-width: 960px) {
  .hero-headline {
    font-size: var(--font-size-h3);
  }
}
</style>
