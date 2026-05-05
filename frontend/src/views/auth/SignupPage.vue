<template>
  <v-container class="fill-height bg-light" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="modern-card pa-8" elevation="4">
          <div class="text-center mb-8">
            <v-img :src="brandingStore.logoUrl" height="64" class="mb-4"></v-img>
            <h1 class="text-h4 font-weight-black">Create Account</h1>
            <p class="text-muted mt-2">Join {{ brandingStore.tenantName }} today</p>
          </div>

          <v-form @submit.prevent="handleSignup">
            <v-text-field
              v-model="name"
              label="Full Name"
              prepend-inner-icon="mdi-account-outline"
              variant="outlined"
              class="mb-2"
              required
            ></v-text-field>

            <v-text-field
              v-model="email"
              label="Email Address"
              prepend-inner-icon="mdi-email-outline"
              variant="outlined"
              class="mb-2"
              required
            ></v-text-field>

            <v-text-field
              v-model="password"
              label="Password"
              prepend-inner-icon="mdi-lock-outline"
              type="password"
              variant="outlined"
              class="mb-4"
              required
            ></v-text-field>

            <v-btn
              color="primary"
              size="large"
              block
              class="font-weight-bold py-4 h-auto"
              type="submit"
              :loading="loading"
            >
              Get Started
            </v-btn>
          </v-form>

          <div class="text-center mt-6">
            <p class="text-body-2 text-muted">
              Already have an account? 
              <router-link to="/login" class="text-primary font-weight-bold text-decoration-none">Sign in</router-link>
            </p>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useBrandingStore } from '@/stores/brandingStore';

const brandingStore = useBrandingStore();
const name = ref('');
const email = ref('');
const password = ref('');
const loading = ref(false);

const handleSignup = () => {
  loading.value = true;
  // Mock signup delay
  setTimeout(() => {
    loading.value = false;
    alert('Account created successfully!');
  }, 1000);
};
</script>
