import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUIStore = defineStore('ui', () => {
  const isLoading = ref(false);

  function setLoading(value: boolean) {
    isLoading.value = value;
  }

  function startLoading() {
    isLoading.value = true;
  }

  function stopLoading() {
    // Small delay to prevent flickering on fast connections
    setTimeout(() => {
      isLoading.value = false;
    }, 300);
  }

  return {
    isLoading,
    setLoading,
    startLoading,
    stopLoading
  };
});
