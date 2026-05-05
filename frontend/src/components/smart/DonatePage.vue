<template>
  <div :style="pageStyle" class="donate-page-wrapper">
    <v-container class="py-16">
      <!-- Top HTML Content -->
      <div v-if="config.topHtml" v-html="config.topHtml"></div>

      <v-row align="center" justify="center">
        <!-- Left Image -->
        <v-col v-if="config.leftImage" cols="12" md="5" class="text-center d-none d-md-block">
          <v-img :src="config.leftImage" max-width="500" class="mx-auto" contain></v-img>
        </v-col>

        <!-- Main Form Component -->
        <v-col cols="12" :md="config.leftImage || config.rightImage ? 7 : 8" :lg="config.leftImage || config.rightImage ? 6 : 7">

          <DonateForm 
            :title="config.formTitle" 
            :subtitle="config.formSubtitle" 
          />
        </v-col>

        <!-- Right Image -->
        <v-col v-if="config.rightImage" cols="12" md="5" class="text-center d-none d-md-block">
          <v-img :src="config.rightImage" max-width="500" class="mx-auto" contain></v-img>
        </v-col>
      </v-row>

      <!-- Bottom HTML Content -->
      <div v-if="config.bottomHtml" v-html="config.bottomHtml"></div>
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { defaultTenantConfig } from '@/config/tenantConfig';
import DonateForm from '@/components/smart/DonateForm.vue';

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
