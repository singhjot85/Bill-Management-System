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
import HeroSection from '@/components/landing/HeroSection.vue';
import ProblemSolution from '@/components/landing/ProblemSolution.vue';
import FeaturesGrid from '@/components/landing/FeaturesGrid.vue';
import UseCases from '@/components/landing/UseCases.vue';
import DashboardPeek from '@/components/landing/DashboardPeek.vue';
import Testimonials from '@/components/landing/Testimonials.vue';
import PricingSection from '@/components/landing/PricingSection.vue';
import FinalCTA from '@/components/landing/FinalCTA.vue';
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
