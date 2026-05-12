<template>
  <div class="customer-login-form">
    <div class="mb-8">
      <h3 class="text-h5 font-weight-bold mb-1">Check your donation impact</h3>
      <p class="text-body-2 text-muted">View receipts, track your recurring gifts, see where your money went.</p>
    </div>

    <v-form @submit.prevent="handleSubmit" v-model="isValid">
      <v-text-field
        v-model="email"
        label="Email (Registered Customer)"
        placeholder="you@gmail.com"
        prepend-inner-icon="mdi-email-outline"
        variant="outlined"
        :rules="[v => !!v || 'Email is required']"
        class="mb-2"
      />

      <v-text-field
        v-model="receiptNo"
        label="Donation Receipt No."
        placeholder="INV-DON-XXXXX"
        prepend-inner-icon="mdi-receipt-text-outline"
        variant="outlined"
        class="mb-4"
      />

      <div class="text-center my-6 position-relative">
        <v-divider />
        <span class="bg-white px-4 text-caption text-muted position-absolute" style="top: 50%; left: 50%; transform: translate(-50%, -50%)">
          OR
        </span>
      </div>

      <v-text-field
        v-model="otp"
        label="One-Time OTP"
        placeholder="OTP sent to your email"
        prepend-inner-icon="mdi-shield-key-outline"
        variant="outlined"
        class="mb-6"
      />

      <v-btn
        color="accent"
        block
        size="large"
        height="54"
        class="font-weight-bold text-none rounded-lg text-white"
        type="submit"
        :disabled="!isValid"
        elevation="0"
      >
        View My Impact <v-icon end>mdi-arrow-right</v-icon>
      </v-btn>

      <div class="mt-8 text-center">
        <a href="#" class="text-caption font-weight-bold text-primary text-decoration-none">
          Don't have a receipt number? Resend Donation Receipt
        </a>
      </div>
    </v-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const isValid = ref(false);
const email = ref('');
const receiptNo = ref('');
const otp = ref('');

const handleSubmit = () => {
  if (isValid.value) {
    alert("Customer impact tracking coming soon!");
  }
};
</script>
