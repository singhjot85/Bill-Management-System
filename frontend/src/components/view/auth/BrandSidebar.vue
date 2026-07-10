<template>
  <div class="brand-sidebar fill-height d-flex align-center justify-center pa-12 text-white">
    <div class="brand-content w-100" style="max-width: 500px">
      <!-- Logo Area -->
      <div class="brand-logo mb-12 d-flex align-center">
        <v-icon size="40" class="mr-3">mdi-heart-pulse</v-icon>
        <div>
          <h1 class="text-h4 font-weight-black lh-1">{{ brandingStore.tenantName }}</h1>
          <span class="text-caption text-uppercase tracking-widest">Bill • Donation • Inventory</span>
        </div>
      </div>

      <!-- Main Headline -->
      <h2 class="text-h3 font-weight-black mb-4 leading-tight">
        Manage Money.<br />
        Save Lives.<br />
        Grow Business.
      </h2>
      <p class="text-h6 font-weight-medium mb-12 opacity-80">
        One app for invoices, donations, bills &amp; inventory.
      </p>

      <!-- Trust Badges (config-driven) -->
      <div class="trust-badges d-flex flex-column gap-4">
        <div v-for="badge in badges" :key="badge.text" class="d-flex align-center">
          <v-avatar color="white" size="32" class="mr-4">
            <v-icon color="primary" size="18">{{ badge.icon ?? 'mdi-check' }}</v-icon>
          </v-avatar>
          <span class="text-subtitle-1 font-weight-bold">{{ badge.text }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBrandingStore } from "@/stores/brandingStore";
import type { BadgeItem } from '@/config/types/authTypes';
import { defaultBrandSidebarConfig } from '@/config/defaults/authDefaults';

const brandingStore = useBrandingStore();

// ponytail: prop with default — caller overrides, else falls back to config defaults
const props = withDefaults(defineProps<{ badges?: BadgeItem[] }>(), {
  badges: () => defaultBrandSidebarConfig.badges
});
</script>

<style scoped>
.brand-sidebar {
  background: linear-gradient(
    135deg,
    rgba(var(--primary-color-rgb), 0.95) 0%,
    rgba(var(--secondary-color-rgb), 0.90) 100%
  );
  position: relative;
  overflow: hidden;
}

.brand-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 30%, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.lh-1 { line-height: 1; }
.opacity-80 { opacity: 0.8; }
.gap-4 { gap: 16px; }
.tracking-widest { letter-spacing: 0.1em; }
</style>
