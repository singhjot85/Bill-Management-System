<template>
  <v-container fluid class="pa-0 fill-height">
    <v-row no-gutters class="fill-height">
      <!-- Left Side -->
      <v-col
        cols="12"
        md="6"
        class="d-none d-md-flex align-center justify-center bg-primary-light"
      >
        <v-container class="text-center">
          <div v-for="item in config.left.order" :key="item">
            <v-img
              v-if="item === 'image'"
              :src="config.left.image"
              max-width="450"
              class="mx-auto mb-8"
              contain
            ></v-img>
            <h2
              v-if="item === 'title'"
              class="text-h3 font-weight-black text-primary mb-4"
            >
              {{ config.left.title }}
            </h2>
            <p
              v-if="item === 'text'"
              class="text-h6 text-muted mx-auto"
              style="max-width: 400px"
            >
              {{ config.left.text }}
            </p>
          </div>
        </v-container>
      </v-col>

      <!-- Right Side -->
      <v-col
        cols="12"
        md="6"
        class="d-flex align-center justify-center bg-light"
      >
        <v-card width="100%" max-width="450" flat class="bg-transparent pa-6">
          <!-- Header (Logo/Title) -->
          <div class="text-center mb-10">
            <div v-for="item in config.header.order" :key="item">
              <v-img
                v-if="item === 'logo'"
                :src="brandingStore.logoUrl"
                height="48"
                class="mb-4"
                contain
              ></v-img>
              <h1 v-if="item === 'title'" class="text-h5 font-weight-bold">
                {{ brandingStore.tenantName }}
              </h1>
            </div>
          </div>

          <!-- Switcher -->
          <v-tabs
            v-model="activeTab"
            grow
            color="primary"
            class="mb-8 border rounded-lg"
            bg-color="surface"
          >
            <v-tab value="login" class="text-none font-weight-bold"
              >Login</v-tab
            >
            <v-tab value="signup" class="text-none font-weight-bold"
              >Signup</v-tab
            >
          </v-tabs>

          <!-- Auth Forms -->
          <v-window v-model="activeTab">
            <v-window-item value="login">
              <v-form @submit.prevent="handleLogin">
                <v-text-field
                  v-model="loginEmail"
                  label="Email"
                  prepend-inner-icon="mdi-email-outline"
                  variant="outlined"
                  class="mb-2"
                  required
                />
                <v-text-field
                  v-model="loginPassword"
                  label="Password"
                  prepend-inner-icon="mdi-lock-outline"
                  type="password"
                  variant="outlined"
                  class="mb-4"
                  required
                />
                <v-btn
                  color="primary"
                  block
                  size="large"
                  class="font-weight-bold py-4 h-auto rounded-lg"
                  type="submit"
                  :loading="loading"
                  >Sign In</v-btn
                >
              </v-form>
            </v-window-item>

            <v-window-item value="signup">
              <v-form @submit.prevent="handleSignup">
                <v-text-field
                  v-model="signupName"
                  label="Full Name"
                  prepend-inner-icon="mdi-account-outline"
                  variant="outlined"
                  class="mb-2"
                  required
                />
                <v-text-field
                  v-model="signupEmail"
                  label="Email"
                  prepend-inner-icon="mdi-email-outline"
                  variant="outlined"
                  class="mb-2"
                  required
                />
                <v-text-field
                  v-model="signupPassword"
                  label="Password"
                  prepend-inner-icon="mdi-lock-outline"
                  type="password"
                  variant="outlined"
                  class="mb-4"
                  required
                />
                <v-btn
                  color="primary"
                  block
                  size="large"
                  class="font-weight-bold py-4 h-auto rounded-lg"
                  type="submit"
                  :loading="loading"
                  >Get Started</v-btn
                >
              </v-form>
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch } from "vue";
import { useBrandingStore } from "@/stores/brandingStore";
import { useRoute, useRouter } from 'vue-router';
import { defaultTenantConfig } from '@/config/tenantConfig';

const props = defineProps({
  config: { type: Object, default: () => defaultTenantConfig.auth }
});


const brandingStore = useBrandingStore();
const route = useRoute();
const router = useRouter();

const activeTab = ref(route.path.includes("signup") ? "signup" : "login");
const loading = ref(false);
const loginEmail = ref("");
const loginPassword = ref("");
const signupName = ref("");
const signupEmail = ref("");
const signupPassword = ref("");

watch(activeTab, (newVal) => router.replace(`/${newVal}`));

const handleLogin = () => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
    alert("Logged in!");
  }, 1000);
};

const handleSignup = () => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
    alert("Account created!");
  }, 1000);
};
</script>

<style scoped>
.bg-primary-light {
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.bg-light {
  background-color: var(--bg-light) !important;
}
</style>
