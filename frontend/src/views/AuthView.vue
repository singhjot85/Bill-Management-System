<template>
  <v-container fluid class="pa-0 fill-height bg-surface">
    <v-row no-gutters class="fill-height">
      <!-- Left Panel: Brand Sidebar -->
      <v-col
        cols="12"
        md="6"
        lg="7"
        class="d-none d-md-block"
      >
        <BrandSidebar />
      </v-col>

      <!-- Right Panel: Auth Forms -->
      <v-col
        cols="12"
        md="6"
        lg="5"
        class="d-flex align-center justify-center bg-white"
      >
        <v-card width="100%" flat class="pa-6 pa-sm-10">
          <!-- Mobile Logo (shown only on small screens) -->
          <div class="d-md-none text-center mb-8">
            <v-icon size="48" color="primary">mdi-heart-pulse</v-icon>
            <h1 class="text-h5 font-weight-black">{{ brandingStore.tenantName }}</h1>
          </div>

          <!-- Tab Navigation -->
          <v-tabs
            v-model="activeTab"
            color="primary"
            grow
            class="mb-10 auth-tabs"
            bg-color="transparent"
          >
            <v-tab value="login" class="text-none font-weight-bold">
              <v-icon start>mdi-login</v-icon> Sign In
            </v-tab>
            <v-tab value="register" class="text-none font-weight-bold">
              <v-icon start>mdi-account-plus</v-icon> Sign Up
            </v-tab>
          </v-tabs>

          <!-- Auth Windows -->
          <v-window v-model="activeTab">
            <v-window-item value="login">
              <LoginForm @forgot-password="showForgotPassword = true" />
            </v-window-item>

            <v-window-item value="register">
              <RegisterForm />
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>

    </v-row>

    <!-- Forgot Password Modal -->
    <v-dialog v-model="showForgotPassword" max-width="400">
      <v-card class="pa-6 rounded-lg">
        <v-card-title class="px-0 pt-0 text-h5 font-weight-bold">
          Reset your password
        </v-card-title>
        <v-card-text class="px-0 text-body-2 text-muted mb-4">
          We will send a password reset link to your registered email.
        </v-card-text>
        <v-text-field
          v-model="forgotEmail"
          label="Email"
          placeholder="registered@email.com"
          variant="outlined"
          hide-details
          class="mb-6"
        />
        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="text" color="muted" @click="showForgotPassword = false">Cancel</v-btn>
          <v-btn color="primary" @click="handleResetPassword" class="px-6">Send Reset Link</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from 'vue-router';
import { useBrandingStore } from "@/stores/brandingStore";

import BrandSidebar from "@/components/auth/BrandSidebar.vue";
import LoginForm from "@/components/auth/LoginForm.vue";
import RegisterForm from "@/components/auth/RegisterForm.vue";
import DonorLoginForm from "@/components/auth/DonorLoginForm.vue";

const brandingStore = useBrandingStore();
const route = useRoute();
const router = useRouter();

// Determine active tab based on route
const getInitialTab = () => {
  if (route.path.includes("signup")) return "register";
  return "login";
};

const activeTab = ref(getInitialTab());
const showForgotPassword = ref(false);
const forgotEmail = ref('');

// Sync route with tab
watch(activeTab, (newTab) => {
  const path = newTab === 'register' ? '/signup' : '/login';
  router.replace(path);
});

const handleResetPassword = () => {
  alert(`Reset link sent to ${forgotEmail.value}`);
  showForgotPassword.value = false;
};
</script>

<style scoped>
.auth-tabs :deep(.v-selection-control-group) {
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.auth-tabs :deep(.v-tab) {
  border-bottom: 2px solid transparent;
}

.text-muted {
  /* color: #666; */
  color: var(--text-secondary)
}

.lh-1 { line-height: 1; }
</style>
