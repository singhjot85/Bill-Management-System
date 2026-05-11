<template>
  <div class="login-form">
    <div class="mb-8">
      <h3 class="text-h5 font-weight-bold mb-1">Welcome back</h3>
      <p class="text-body-2 text-muted">Sign in to manage your invoices, donations & inventory</p>
    </div>

    <v-form @submit.prevent="handleSubmit" v-model="isValid">
      <v-text-field
        v-model="username"
        label="Username"
        placeholder="your-username"
        prepend-inner-icon="mdi-account-outline"
        variant="outlined"
        :rules="[v => !!v || 'Username is required']"
        class="mb-2"
      />
      
      <v-text-field
        v-model="password"
        label="Password"
        placeholder="••••••••"
        prepend-inner-icon="mdi-lock-outline"
        :type="showPassword ? 'text' : 'password'"
        :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
        @click:append-inner="showPassword = !showPassword"
        variant="outlined"
        :rules="[v => !!v || 'Password is required']"
        class="mb-1"
      />

      <div class="d-flex align-center justify-space-between mb-6">
        <v-checkbox
          v-model="rememberMe"
          label="Keep me signed in"
          hide-details
          density="comfortable"
          color="primary"
        />
        <a href="#" class="text-body-2 font-weight-bold text-primary text-decoration-none" @click.prevent="$emit('forgot-password')">
          Forgot password?
        </a>
      </div>

      <v-btn
        color="primary"
        block
        size="large"
        height="54"
        class="font-weight-bold text-none rounded-lg"
        type="submit"
        :loading="authStore.loading"
        :disabled="!isValid"
        elevation="0"
      >
        Sign In
      </v-btn>

      <div class="text-center my-8 position-relative">
        <v-divider />
        <span class="bg-white px-4 text-caption text-muted position-absolute" style="top: 50%; left: 50%; transform: translate(-50%, -50%)">
          Or continue with
        </span>
      </div>

      <v-row dense>
        <v-col cols="6">
          <v-btn block variant="outlined" class="text-none rounded-lg" height="48">
            <v-icon start>mdi-google</v-icon> Google
          </v-btn>
        </v-col>
        <v-col cols="6">
          <v-btn block variant="outlined" class="text-none rounded-lg" height="48">
            <v-icon start>mdi-microsoft</v-icon> Microsoft
          </v-btn>
        </v-col>
      </v-row>

      <div class="mt-8 text-center">
        <p class="text-caption text-muted">
          Demo: demo@fintech.com / demo123
        </p>
      </div>
    </v-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const isValid = ref(false);
const username = ref('');
const password = ref('');
const showPassword = ref(false);
const rememberMe = ref(false);

const handleSubmit = async () => {
  if (!isValid.value) return;
  
  try {
    await authStore.login({
      username: username.value,
      password: password.value
    });
    router.push({ name: 'Dashboard' });
  } catch (error) {
    // Error handled by store/interceptor
  }
};
</script>
