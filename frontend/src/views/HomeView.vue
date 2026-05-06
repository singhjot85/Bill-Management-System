<template>
  <v-row 
    v-for="(row, rIdx) in config.rows" 
    :key="'row-' + rIdx"
    justify="center" 
    align="center" 
    :class="row.class"
  >
    <v-col 
      v-for="(col, cIdx) in row.cols" 
      :key="'col-' + cIdx"
      :cols="col.cols || 12"
      :md="col.md"
      :class="col.class"
    >
      <div v-html="col.html"></div>
    </v-col>
  </v-row>

  <PRStub 
    v-for="(stub, sIdx) in config.topPRStubs" 
    :key="'top-stub-' + sIdx"
    :stubConfig="stub" 
  />

  <!-- Big Bulk Donate Button -->
  <v-row justify="center" class="my-16">
    <v-col cols="auto">
      <v-btn 
        class="big-donate-btn" 
        height="72" 
        elevation="8" 
        to="/donate"
        color="primary"
      >
        Donate Now
      </v-btn>
    </v-col>
  </v-row>

  <PRStub 
    v-for="(stub, sIdx) in config.bottomPRStubs" 
    :key="'bottom-stub-' + sIdx"
    :stubConfig="stub" 
  />
</template>

<script setup>
import PRStub from '@/components/ui/PRStub.vue';
import { defaultTenantConfig } from '@/config/tenantConfig';

defineProps({
  config: {
    type: Object,
    default: () => defaultTenantConfig.home
  }
});
</script>

<style scoped>
.big-donate-btn {
  font-size: 1.5rem;
  font-weight: bold;
  padding: 0 3rem;
  border-radius: 12px;
}
</style>
