<template>
  <div :style="pageStyle" class="donate-page-wrapper">
    <v-container fluid class="pa-0">
      <!-- <v-container class="py-16"> -->
        <!-- Top HTML Content -->
        <div v-if="config.topHtml" v-html="config.topHtml"></div>

        <v-row align="stretch" justify="center" no-gutters class="mx-auto" style="max-width: 1600px">
          <!-- Left Image -->
          <v-col 
            v-if="config.leftImage" 
            cols="12" 
            :md="config.rightImage ? 3 : 4" 
            class="d-none d-md-flex px-0"
          >
            <v-img 
              :src="config.leftImage" 
              class="rounded-xl shadow-lg" 
              cover 
              height="100%"
            ></v-img>
          </v-col>

          <!-- Main Form Component -->
          <v-col 
            cols="12" 
            :md="config.leftImage && config.rightImage ? 6 : (config.leftImage || config.rightImage ? 8 : 8)"
            :lg="config.leftImage && config.rightImage ? 5 : (config.leftImage || config.rightImage ? 7 : 6)"
            class="px-md-10 px-4 py-4"
          >
            <DonateForm 
              :title="config.formTitle" 
              :subtitle="config.formSubtitle" 
            />
          </v-col>

          <!-- Right Image -->
          <v-col 
            v-if="config.rightImage" 
            cols="12" 
            :md="config.leftImage ? 3 : 4" 
            class="d-none d-md-flex px-0"
          >
            <v-img 
              :src="config.rightImage" 
              class="rounded-xl shadow-lg" 
              cover 
              height="100%"
            ></v-img>
          </v-col>
        </v-row>

        <!-- Bottom HTML Content -->
        <div v-if="config.bottomHtml" v-html="config.bottomHtml" class="mt-8"></div>
      <!-- </v-container> -->
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { defaultTenantConfig } from '@/config/tenantConfig';
import DonateForm from '@/components/donate/DonateForm.vue';

const props = defineProps({
  config: {
    type: Object,
    default: () => defaultTenantConfig.donate
  }
});

const pageStyle = computed(() => {
  if (props.config.backgroundImage) {
    return {
      backgroundImage: `url(${props.config.backgroundImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      minHeight: '100%'
    };
  }
  return {};
});
</script>

<style scoped>
.donate-page-wrapper {
  transition: all 0.3s ease;
}
</style>
