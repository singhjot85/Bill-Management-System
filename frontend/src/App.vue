<template>
  <v-app>
    <!-- Modern Loading Overlay -->
    <LoadingOverlay :active="uiStore.isLoading" />

    <!-- Main Content -->
    <router-view />
  </v-app>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { useBrandingStore } from '@/stores/brandingStore';
import { useUIStore } from '@/stores/uiStore';
import { useTheme } from 'vuetify';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const brandingStore = useBrandingStore();
const uiStore = useUIStore();
const vuetifyTheme = useTheme();

const applyTheme = (themeName) => {
  if (typeof vuetifyTheme.global.name.value !== 'undefined') {
    vuetifyTheme.global.name.value = themeName;
  }
  document.documentElement.setAttribute('data-theme', themeName);
};

// Sync store theme with Vuetify and DOM
watch(() => brandingStore.theme, (newTheme) => {
  applyTheme(newTheme);
}, { immediate: true });

onMounted(async () => {
  try {
    uiStore.startLoading();
    await brandingStore.fetchBranding();
  } finally {
    uiStore.stopLoading();
  }
});
</script>
