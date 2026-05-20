<template>
  <div class="home-view">
    <HeroSection :config="config.hero" />
    <ProblemSolution :config="config.problemSolution" />
    <FeaturesGrid :config="config.featuresGrid" />
    <UseCases :config="config.useCases" />
    <DashboardPeek :config="config.dashboardPeek" />
    <Testimonials :config="config.testimonials" />
    <PricingSection :config="config.pricing" />
    <FinalCTA :config="config.finalCTA" />
  </div>
</template>

<script setup lang="ts">
import HeroSection from '@/components/layout/HeroSection.vue';
import ProblemSolution from '@/components/layout/ProblemSolution.vue';
import FeaturesGrid from '@/components/layout/FeaturesGrid.vue';
import UseCases from '@/components/layout/UseCases.vue';
import DashboardPeek from '@/components/layout/DashboardPeek.vue';
import Testimonials from '@/components/layout/Testimonials.vue';
import PricingSection from '@/components/layout/PricingSection.vue';
import FinalCTA from '@/components/layout/FinalCTA.vue';
import type { HomePageConfig } from '@/config/tenantConfig';

defineProps<{
  config: HomePageConfig;
}>();
</script>

<style scoped>
.home-view {
  background-color: var(--background-color);
  color: var(--text-primary);
}
</style>
