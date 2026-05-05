<template>
  <v-overlay
    :model-value="active"
    class="align-center justify-center"
    persistent
    scrim="surface"
  >
    <div class="text-center">
      <v-progress-circular
        indeterminate
        color="primary"
        size="64"
        width="6"
        class="mb-4"
      ></v-progress-circular>
      <div class="text-h6 font-weight-bold text-primary animate-pulse">
        Loading Experience...
      </div>
    </div>
  </v-overlay>
</template>

<script setup>
defineProps({
  active: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .5; }
}
</style>
