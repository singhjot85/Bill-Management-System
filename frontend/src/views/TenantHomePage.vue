<template>
  <v-app>
    <Navbar 
      :branding="brandingStore" 
      :config="navbarConfig"
      fixed
      @action="handleAction"
      @navigate="handleNavigate"
    />

    <v-main class="bg-light">
      <v-container class="py-16">
        <!-- Hero / Top Section -->
        <v-row justify="center" align="center" class="text-center mb-16">
          <v-col cols="12" md="8">
            <h1 class="text-h2 font-weight-black mb-6">
              Empowering Your <span class="text-primary">Financial Impact</span>
            </h1>
            <p class="text-h6 text-muted mb-10">
              Seamlessly manage your bills and support causes you care about, all in one modern platform.
            </p>
          </v-col>
        </v-row>

        <!-- PR Content Stub 1 -->
        <PRStub />

        <!-- Big Bulk Donate Button -->
        <v-row justify="center" class="my-16">
          <v-col cols="auto">
            <v-btn class="big-donate-btn" height="72" elevation="8" to="/donate">
              Donate Now
            </v-btn>
          </v-col>
        </v-row>

        <!-- PR Content Stub 2 -->
        <PRStub />

      </v-container>
    </v-main>

    <Footer :branding="brandingStore" />
  </v-app>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import PRStub from '@/components/PRStub.vue';
import { useBrandingStore } from '@/stores/brandingStore';
import { useRouter } from 'vue-router';
import { defaultNavbarConfig } from '@/config/navbarConfig';

const brandingStore = useBrandingStore();
const router = useRouter();
const navbarConfig = ref(defaultNavbarConfig);

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
  background-color: var(--bg-light) !important;
}
</style>
