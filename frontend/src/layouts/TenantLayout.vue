<template>
  <v-app>
    <Navbar 
      :branding="brandingStore" 
      :config="tenantConfig.navbar"
      fixed
      @action="handleAction"
      @navigate="handleNavigate"
    />

    <v-main class="bg-light main-content-wrapper">
      <router-view v-slot="{ Component }">
        <component :is="Component" :config="viewConfig" />
      </router-view>
    </v-main>

    <Footer :branding="brandingStore" />
  </v-app>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import Navbar from '@/components/common/Navbar.vue';
import Footer from '@/components/common/Footer.vue';
import { useBrandingStore } from '@/stores/brandingStore';
import { useRouter, useRoute } from 'vue-router';
import { defaultTenantConfig } from '@/config/tenantConfig';

const brandingStore = useBrandingStore();
const router = useRouter();
const route = useRoute();

const tenantConfig = ref(defaultTenantConfig);

const viewConfig = computed(() => {
  if (route.path === '/' || route.name === 'PublicHome') {
    return tenantConfig.value.home;
  }
  if (route.path.includes('login') || route.path.includes('signup')) {
    return tenantConfig.value.auth;
  }
  if (route.path.includes('donate')) {
    return tenantConfig.value.donate;
  }
  return {};
});

const handleAction = (action, item) => {
  if (action === 'toggleTheme') {
    brandingStore.toggleTheme();
  }
};

const handleNavigate = (path, item) => {
  router.push(path);
};

onMounted(async () => {
  await brandingStore.fetchBranding();
});
</script>

<style scoped>
.bg-light {
  background-color: var(--background-color) !important;
}
.main-content-wrapper {
  margin-top: 24px;
  margin-bottom: 24px;
  min-height: calc(100vh - 128px);
}
</style>
