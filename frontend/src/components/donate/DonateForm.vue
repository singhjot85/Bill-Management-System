<template>
  <v-card class="premium-form-card" flat>
    <div class="gradient-accent"></div>
    <div class="pa-10">
      <!-- Header Section -->
      <div class="text-center mb-10">
        <h2 class="text-h3 font-weight-black color-primary mb-2">{{ title }}</h2>
        <div class="subtitle-wrapper mx-auto">
          <p class="text-subtitle-1 text-muted font-weight-medium">{{ subtitle }}</p>
        </div>
      </div>

      <v-form v-if="paymentStatus !== 'success'" @submit.prevent="proceedToPayment">
        <!-- Section 1: Personal Identity -->
        <div class="form-section-label mb-4">Per  sonal Information</div>
        <v-text-field
          v-model="formData.name"
          label="Full Name"
          variant="filled"
          flat
          bg-color="grey-lighten-4"
          prepend-inner-icon="mdi-account-circle-outline"
          class="mb-6 rounded-lg custom-input"
          hide-details="auto"
          required
        ></v-text-field>

        <!-- Email Group -->
        <div class="verification-group mb-6">
          <v-row no-gutters align="center">
            <v-col>
              <v-text-field
                v-model="formData.email"
                label="Email Address"
                variant="filled"
                flat
                bg-color="grey-lighten-4"
                prepend-inner-icon="mdi-email-open-outline"
                :readonly="emailVerified"
                class="rounded-lg custom-input"
                hide-details="auto"
              >
                <template v-slot:append-inner>
                  <v-fade-transition>
                    <v-icon v-if="emailVerified" color="success">mdi-check-decagram</v-icon>
                  </v-fade-transition>
                </template>
              </v-text-field>
            </v-col>
            <v-col v-if="!emailVerified" cols="auto" class="pl-3">
              <v-btn
                color="primary"
                height="56"
                min-width="100"
                class="rounded-lg font-weight-bold"
                elevation="0"
                @click="sendOtp('email')"
                :loading="emailLoading"
              >
                Verify
              </v-btn>
            </v-col>
          </v-row>
          <v-expand-transition>
            <div v-if="showEmailOtp && !emailVerified" class="otp-box mt-3 pa-3 rounded-lg border">
              <div class="d-flex align-center">
                <v-text-field
                  v-model="formData.emailOtp"
                  placeholder="Enter 6-digit OTP"
                  density="compact"
                  variant="plain"
                  hide-details
                  class="otp-input"
                ></v-text-field>
                <v-btn color="success" size="small" @click="verifyOtp('email')" :loading="emailLoading" class="ml-2 font-weight-bold">Confirm</v-btn>
              </div>
            </div>
          </v-expand-transition>
        </div>

        <!-- Phone Group -->
        <div class="verification-group mb-6">
          <v-row no-gutters align="center">
            <v-col>
              <v-text-field
                v-model="formData.phone"
                label="Phone Number"
                variant="filled"
                flat
                bg-color="grey-lighten-4"
                prepend-inner-icon="mdi-phone-outline"
                :readonly="phoneVerified"
                class="rounded-lg custom-input"
                hide-details="auto"
              >
                <template v-slot:append-inner>
                  <v-fade-transition>
                    <v-icon v-if="phoneVerified" color="success">mdi-check-decagram</v-icon>
                  </v-fade-transition>
                </template>
              </v-text-field>
            </v-col>
            <v-col v-if="!phoneVerified" cols="auto" class="pl-3">
              <v-btn
                color="primary"
                height="56"
                min-width="100"
                class="rounded-lg font-weight-bold"
                elevation="0"
                @click="sendOtp('phone')"
                :loading="phoneLoading"
              >
                Verify
              </v-btn>
            </v-col>
          </v-row>
          <v-expand-transition>
            <div v-if="showPhoneOtp && !phoneVerified" class="otp-box mt-3 pa-3 rounded-lg border">
              <div class="d-flex align-center">
                <v-text-field
                  v-model="formData.phoneOtp"
                  placeholder="Enter mobile OTP"
                  density="compact"
                  variant="plain"
                  hide-details
                  class="otp-input"
                ></v-text-field>
                <v-btn color="success" size="small" @click="verifyOtp('phone')" :loading="phoneLoading" class="ml-2 font-weight-bold">Confirm</v-btn>
              </div>
            </div>
          </v-expand-transition>
        </div>

        <!-- Section 2: Contribution Details -->
        <div class="form-section-label mb-4 mt-8">Contribution Details</div>
        <v-textarea
          v-model="formData.address"
          label="Billing Address"
          variant="filled"
          flat
          bg-color="grey-lighten-4"
          prepend-inner-icon="mdi-map-marker-radius-outline"
          rows="2"
          class="mb-10 rounded-lg custom-input"
          hide-details="auto"
        ></v-textarea>

        <!-- Final Action -->
        <v-btn
          v-if="paymentStatus !== 'success'"
          color="primary"
          block
          height="72"
          class="pay-btn text-h6 font-weight-black rounded-xl"
          @click="proceedToPayment"
          :loading="paymentLoading"
          :disabled="!isFormValid"
        >
          <v-icon start class="mr-2">mdi-shield-check-outline</v-icon>
          {{ paymentStatus === 'failure' ? 'Retry Payment' : 'Secure Checkout' }}
        </v-btn>
      </v-form>

      <!-- Celebratory Success State -->
      <v-fade-transition>
        <div v-if="paymentStatus === 'success'" class="text-center py-10">
          <div class="success-icon-wrapper mb-6">
            <v-icon color="white" size="48">mdi-check-bold</v-icon>
          </div>
          <h3 class="text-h4 font-weight-black mb-2">Contribution Received!</h3>
          <p class="text-subtitle-1 text-muted mb-10">Your impact is now being processed. Thank you for your support!</p>
          
          <div class="payment-id-card pa-4 rounded-lg mb-10">
            <div class="text-overline mb-1">Platform Receipt ID</div>
            <div class="text-h6 font-weight-black text-primary">{{ paymentId }}</div>
          </div>

          <v-btn
            color="success"
            block
            height="64"
            prepend-icon="mdi-file-certificate"
            class="text-h6 font-weight-bold rounded-xl shadow-success"
            @click="generateInvoice"
            :loading="invoiceLoading"
          >
            Download Invoice
          </v-btn>
        </div>
      </v-fade-transition>
    </div>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

const props = defineProps({
  title: String,
  subtitle: String
});

const formData = reactive({
  name: '',
  email: '',
  emailOtp: '',
  phone: '',
  phoneOtp: '',
  address: ''
});

const emailLoading = ref(false);
const phoneLoading = ref(false);
const paymentLoading = ref(false);
const invoiceLoading = ref(false);
const showEmailOtp = ref(false);
const emailVerified = ref(false);
const showPhoneOtp = ref(false);
const phoneVerified = ref(false);
const paymentStatus = ref('pending');
const paymentId = ref('');

const isFormValid = computed(() => {
  return formData.name && emailVerified.value && phoneVerified.value && formData.address;
});

const sendOtp = (type) => {
  if (type === 'email') {
    emailLoading.value = true;
    setTimeout(() => { emailLoading.value = false; showEmailOtp.value = true; }, 800);
  } else {
    phoneLoading.value = true;
    setTimeout(() => { phoneLoading.value = false; showPhoneOtp.value = true; }, 800);
  }
};

const verifyOtp = (type) => {
  if (type === 'email') {
    emailLoading.value = true;
    setTimeout(() => { emailLoading.value = false; emailVerified.value = true; }, 800);
  } else {
    phoneLoading.value = true;
    setTimeout(() => { phoneLoading.value = false; phoneVerified.value = true; }, 800);
  }
};

const proceedToPayment = () => {
  paymentLoading.value = true;
  setTimeout(() => {
    const success = Math.random() > 0.1;
    if (success) {
      paymentStatus.value = 'success';
      paymentId.value = 'BMA-' + Math.random().toString(36).substr(2, 6).toUpperCase();
    } else {
      paymentStatus.value = 'failure';
    }
    paymentLoading.value = false;
  }, 1800);
};

const generateInvoice = () => {
  invoiceLoading.value = true;
  setTimeout(() => { invoiceLoading.value = false; alert('Invoice generated!'); }, 1000);
};
</script>

<style scoped>
.premium-form-card {
  background: var(--surface-light);
  border-radius: 32px !important;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(0, 0, 0, 0.03) !important;
  overflow: hidden;
}

.gradient-accent {
  height: 10px;
  background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
}

.form-section-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 800;
  color: var(--v-theme-primary);
  opacity: 0.8;
}

.custom-input :deep(.v-field) {
  border-radius: 12px !important;
  transition: all 0.2s ease;
}

.custom-input :deep(.v-field--focused) {
  background-color: white !important;
  box-shadow: 0 0 0 2px var(--v-theme-primary) !important;
}

.otp-box {
  background-color: #f8fafc;
  border: 1px dashed #cbd5e1 !important;
}

.pay-btn {
  background: linear-gradient(135deg, var(--v-theme-primary) 0%, #4338ca 100%) !important;
  box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4) !important;
  transition: transform 0.2s ease;
}

.pay-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.success-icon-wrapper {
  width: 80px;
  height: 80px;
  background: #22c55e;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.4);
}

.payment-id-card {
  background: #f0f9ff;
  border: 1px solid #bae6fd !important;
}

.subtitle-wrapper {
  max-width: 450px;
}

.color-primary {
  color: #1e293b;
}
</style>
