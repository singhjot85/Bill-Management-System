<template>
  <div class="donate-view">
    <DonateHero :config="config.hero" @action="handleHeroAction" />
    <ProblemImpact :config="config.problem" />
    <DonationTiers :config="config.tiers" @select-tier="handleTierSelect" />
    <RecurringDonation :config="config.recurringBlock" />
    <TransparencySteps :config="config.transparency" />

    <v-container id="donation-form-section" class="py-16">
      <v-row justify="center">
        <v-col cols="12" md="8" lg="6">
          <DonateForm
            ref="donateFormRef"
            :title="config.formTitle"
            :subtitle="config.formSubtitle"
            :initialAmount="selectedAmount"
          />
        </v-col>
      </v-row>
    </v-container>

    <Testimonials :config="config.socialProof" />
    <RealTimeCounter :config="config.counter" @donate-click="handleTierSelect({ amount: $event })" />
    <FAQSection :config="config.faq" />

    <!-- Final CTA -->
    <v-container fluid class="py-16 bg-primary-dark">
      <v-row justify="center" class="text-center">
        <v-col cols="12" md="8">
          <h2 class="text-h2 font-weight-black text-white mb-4">{{ config.finalCTA.headline }}</h2>
          <p class="text-h5 text-white opacity-80 mb-10">{{ config.finalCTA.subheadline }}</p>
          <div class="d-flex flex-wrap justify-center gap-4">
            <v-btn color="white" size="x-large" class="rounded-lg font-weight-black" style="color: var(--primary-color) !important;" @click="scrollToForm">
              {{ config.finalCTA.primaryCTA }}
            </v-btn>
            <v-btn variant="outlined" color="white" size="x-large" class="rounded-lg font-weight-black">
              {{ config.finalCTA.secondaryCTA }}
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import DonateHero from '@/components/layout/DonateHero.vue';
import ProblemImpact from '@/components/layout/ProblemImpact.vue';
import DonationTiers from '@/components/layout/DonationTiers.vue';
import RecurringDonation from '@/components/layout/RecurringDonation.vue';
import TransparencySteps from '@/components/layout/TransparencySteps.vue';
import RealTimeCounter from '@/components/layout/RealTimeCounter.vue';
import FAQSection from '@/components/layout/FAQSection.vue';
import DonateForm from '@/components/view/donate/DonateForm.vue';
import Testimonials from '@/components/layout/Testimonials.vue';
import type { DonatePageConfig } from '@/config/tenantConfig';

const props = defineProps<{
  config: DonatePageConfig;
}>();

const selectedAmount = ref<number | null>(null);

const scrollToForm = () => {
  const el = document.getElementById('donation-form-section');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
};

const handleHeroAction = (action: string) => {
  if (action === 'scrollToForm') {
    scrollToForm();
  }
};

const handleTierSelect = (tier: { amount: number }) => {
  selectedAmount.value = tier.amount;
  scrollToForm();
};
</script>

<style scoped>
.donate-view {
  background-color: var(--background-color);
}

.bg-primary-dark {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%) !important;
}

.opacity-80 { opacity: 0.8; }
.gap-4 { gap: var(--spacing-md); }
</style>
