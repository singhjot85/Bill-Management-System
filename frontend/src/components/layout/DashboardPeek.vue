<template>
  <v-container class="dashboard-peek-section py-16 text-center">
    <h2 class="section-headline font-weight-bold mb-12">Dashboard Sneak Peek</h2>
    <v-card class="dashboard-mockup pa-4 mx-auto elevation-12 rounded-xl" max-width="1000">
      <v-row>
        <!-- Sidebar Mock -->
        <v-col cols="3" class="sidebar-mock d-none d-md-flex flex-column pa-4 border-right">
          <div v-for="n in 5" :key="n" class="sidebar-item mb-4"></div>
        </v-col>
        <!-- Main Content Mock -->
        <v-col cols="12" md="9" class="pa-6 text-left">
          <v-row>
            <v-col v-for="(widget, index) in config.widgets" :key="index" cols="12" sm="4">
              <v-card class="widget-card pa-4" variant="outlined">
                <div class="widget-title mb-1 font-weight-bold">{{ widget.title }}</div>
                <div class="widget-content">{{ widget.content }}</div>
              </v-card>
            </v-col>
          </v-row>
          <v-sheet class="mt-6 chart-placeholder rounded-lg" height="200" color="rgba(var(--primary-color-rgb), 0.05)"></v-sheet>
        </v-col>
      </v-row>
    </v-card>
    <p class="peek-caption mt-8 font-weight-medium">{{ config.caption }}</p>
  </v-container>
</template>

<script setup lang="ts">
import type { DashboardPeekConfig } from '@/config/tenantConfig';

defineProps<{
  config: DashboardPeekConfig;
}>();
</script>

<style scoped>
.section-headline {
  font-size: var(--font-size-h3);
  color: var(--text-primary);
}

.dashboard-mockup {
  background-color: var(--surface-color);
  border: 1px solid rgba(var(--primary-color-rgb), 0.1);
  overflow: hidden;
}

.sidebar-mock {
  background-color: rgba(var(--primary-color-rgb), 0.02);
}

.sidebar-item {
  height: var(--spacing-md);
  background-color: rgba(var(--primary-color-rgb), 0.1);
  border-radius: var(--radius-sm);
  width: 100%;
}

.widget-card {
  border-color: rgba(var(--primary-color-rgb), 0.1) !important;
  border-radius: var(--radius-md);
}

.widget-title {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  text-transform: uppercase;
}

.widget-content {
  font-size: var(--font-size-base);
  color: var(--primary-color);
}

.chart-placeholder {
  border: 1px dashed rgba(var(--primary-color-rgb), 0.3);
}

.peek-caption {
  font-size: var(--font-size-xl);
  color: var(--text-primary);
}
</style>
