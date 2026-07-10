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

      <!-- Right Panel: Auth Forms — bg-surface replaces bg-white -->
      <v-col
        cols="12"
        md="6"
        lg="5"
        class="d-flex align-center justify-center bg-surface"
      >
        <v-card width="100%" height="100%" flat class="pa-6 pa-sm-10 bg-surface">
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
          <v-window v-model="activeTab" class="auth-window">
            <v-window-item value="login">
              <LoginForm @forgot-password="showForgotPassword = true" /> <!-- pragma: allowlist-secret -->
            </v-window-item>

            <v-window-item value="register">
              <RegisterForm />
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>

    </v-row>

    <!-- Forgot Password Modal — with entrance transition -->
    <v-dialog v-model="showForgotPassword" max-width="400">
      <Transition name="modal-enter">
        <v-card v-if="showForgotPassword" class="pa-6 rounded-lg bg-surface">
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
            <v-btn color="primary" @click="handleResetPassword" class="px-6 cta-btn">Send Reset Link</v-btn>
          </v-card-actions>
        </v-card>
      </Transition>
    </v-dialog>

    <!-- Reset password snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000" location="bottom">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute, useRouter } from 'vue-router';
import { useBrandingStore } from "@/stores/brandingStore";

import BrandSidebar from "@/components/view/auth/BrandSidebar.vue";
import LoginForm from "@/components/view/auth/LoginForm.vue";
import RegisterForm from "@/components/view/auth/RegisterForm.vue";

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
const snackbar = ref({ show: false, message: '', color: 'success' });

// Sync route with tab
watch(activeTab, (newTab) => {
  const path = newTab === 'register' ? '/signup' : '/login';
  router.replace(path);
});

const handleResetPassword = async () => {
  // ponytail: real API call wired in future — show success toast for now
  snackbar.value = { show: true, message: `Reset link sent to ${forgotEmail.value}`, color: 'success' };
  showForgotPassword.value = false;
  forgotEmail.value = '';
};
</script>

<style scoped>
/* Tab bar border — token-driven, dark-mode safe */
.auth-tabs :deep(.v-selection-control-group) {
  border-bottom: 1px solid rgba(var(--text-primary-rgb), 0.08);
}

.auth-tabs :deep(.v-tab) {
  border-bottom: 2px solid transparent;
}

/* v-window tab transition — custom cubic-bezier */
.auth-window :deep(.v-window__container) {
  transition: transform 230ms cubic-bezier(0.23, 1, 0.32, 1);
}

/* Forgot-password modal entrance animation */
.modal-enter-active {
  transition: opacity 200ms ease-out, transform 260ms cubic-bezier(0.23, 1, 0.32, 1);
}
.modal-enter-from { opacity: 0; transform: translateY(12px) scale(0.97); }
.modal-enter-to   { opacity: 1; transform: translateY(0) scale(1); }
.modal-leave-active { transition: opacity 150ms ease-in; }
.modal-leave-from { opacity: 1; }
.modal-leave-to   { opacity: 0; }

/* CTA button press micro-animation */
.cta-btn:active { transform: scale(0.97); transition: transform 120ms ease-out; }

.text-muted { color: var(--text-secondary); }
.lh-1 { line-height: 1; }
</style>
