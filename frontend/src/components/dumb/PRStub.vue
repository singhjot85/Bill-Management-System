<template>
  <v-card :class="['modern-card pa-6 text-center my-12', stubConfig.class]" flat>
    <v-icon v-if="stubConfig.icon" size="48" color="primary" class="mb-4">{{ stubConfig.icon }}</v-icon>
    <v-img v-else-if="stubConfig.image" :src="stubConfig.image" height="200" contain class="mb-4"></v-img>
    <h3 class="text-h5 font-weight-bold mb-2">{{ stubConfig.title || 'PR Content Placeholder' }}</h3>
    <p class="text-muted">{{ stubConfig.description || 'This component will display promotional content stubs.' }}</p>
  </v-card>
</template>

<script setup>
defineProps({
  stubConfig: {
    type: Object,
    default: () => ({})
  }
});
</script>
