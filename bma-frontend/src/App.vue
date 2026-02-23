<template>
  <Button rounded="full" padding="lg" @click="toggleTheme">Toggle Theme</Button>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import Button from './components/base/Button.vue'

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')

  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark')
  }
})

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark')
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
}
</script>
