<template>
  <v-container class="py-16">
    <h1 class="text-h4 font-weight-bold mb-6">User Dashboard</h1>
    <p>Welcome to your authenticated area.</p>
    <v-row class="mt-8">
      <v-col cols="12" md="4" v-for="i in 3" :key="i">
        <v-card class="pa-6" flat border>
          <h3 class="text-h6 mb-2">Stat {{ i }}</h3>
          <div class="text-h4 text-primary font-weight-black">{{ i * 123 }}</div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// Dashboard logic here
</script>
