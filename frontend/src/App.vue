<template>
  <v-app>
    <!-- Modern Loading Overlay -->
    <LoadingOverlay :active="isLoading" />

    <!-- Main Content -->
    <router-view v-if="!isLoading" />
  </v-app>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useBrandingStore } from '@/stores/brandingStore';
import { useTheme } from 'vuetify';
import LoadingOverlay from '@/components/dumb/LoadingOverlay.vue';

const brandingStore = useBrandingStore();
const vuetifyTheme = useTheme();
const isLoading = ref(true);

const applyTheme = (themeName) => {
  // Try using the recommended approach if available, otherwise fallback to standard reactive assignment
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
    // Turn on the overlay and wait for branding
    await brandingStore.fetchBranding();
  } finally {
    // Small delay for smooth transition
    setTimeout(() => {
      isLoading.value = false;
    }, 500);
  }
});
</script>