<template>
  <v-card class="modern-card elevation-4" flat>
    <div class="primary-accent-bar"></div>
    <div class="pa-10">
      <div class="text-center mb-10">
        <h2 class="text-h3 font-weight-black mb-3">{{ title }}</h2>
        <p class="text-h6 text-muted font-weight-medium">{{ subtitle }}</p>
      </div>

      <v-form v-if="paymentStatus !== 'success'" @submit.prevent="proceedToPayment">
        <!-- Basic Info -->
        <v-text-field
          v-model="formData.name"
          label="Full Name"
          variant="outlined"
          prepend-inner-icon="mdi-account-outline"
          class="mb-4"
          bg-color="surface"
          required
        ></v-text-field>

      <!-- Email with Verification -->
      <v-row no-gutters align="center"  class="mb-2">
        <v-col :cols="emailVerified ? 12 : 9">
          <v-text-field
            v-model="formData.email"
            label="Email Address"
            variant="outlined"
            prepend-inner-icon="mdi-email-outline"
            :readonly="emailVerified"
            :success="emailVerified"
            hide-details
          >
            <template v-if="emailVerified" v-slot:append-inner>
              <v-icon color="success">mdi-check-circle</v-icon>
            </template>
          </v-text-field>
        </v-col>
        <v-col v-if="!emailVerified" cols="3" class="pl-2">
          <v-btn
            color="primary"
            variant="tonal"
            block
            height="56"
            @click="sendOtp('email')"
            :loading="emailLoading"
          >
            Verify
          </v-btn>
        </v-col>
      </v-row>

      <!-- Hidden Email OTP Field -->
      <v-expand-transition>
        <v-row no-gutters v-if="showEmailOtp && !emailVerified" class="mb-4">
          <v-col cols="9">
            <v-text-field
              v-model="formData.emailOtp"
              label="Enter Email OTP"
              variant="outlined"
              density="compact"
              hide-details
            ></v-text-field>
          </v-col>
          <v-col cols="3" class="pl-2">
            <v-btn
              color="success"
              block
              height="40"
              @click="verifyOtp('email')"
              :loading="emailLoading"
            >
              Confirm
            </v-btn>
          </v-col>
        </v-row>
      </v-expand-transition>

      <!-- Phone with Verification -->
      <v-row no-gutters align="center" class="mb-2">
        <v-col :cols="phoneVerified ? 12 : 9">
          <v-text-field
            v-model="formData.phone"
            label="Phone Number"
            variant="outlined"
            prepend-inner-icon="mdi-phone-outline"
            :readonly="phoneVerified"
            :success="phoneVerified"
            hide-details
          >
            <template v-if="phoneVerified" v-slot:append-inner>
              <v-icon color="success">mdi-check-circle</v-icon>
            </template>
          </v-text-field>
        </v-col>
        <v-col v-if="!phoneVerified" cols="3" class="pl-2">
          <v-btn
            color="primary"
            variant="tonal"
            block
            height="56"
            @click="sendOtp('phone')"
            :loading="phoneLoading"
          >
            Verify
          </v-btn>
        </v-col>
      </v-row>

      <!-- Hidden Phone OTP Field -->
      <v-expand-transition>
        <v-row no-gutters v-if="showPhoneOtp && !phoneVerified" class="mb-4">
          <v-col cols="9">
            <v-text-field
              v-model="formData.phoneOtp"
              label="Enter Phone OTP"
              variant="outlined"
              density="compact"
              hide-details
            ></v-text-field>
          </v-col>
          <v-col cols="3" class="pl-2">
            <v-btn
              color="success"
              block
              height="40"
              @click="verifyOtp('phone')"
              :loading="phoneLoading"
            >
              Confirm
            </v-btn>
          </v-col>
        </v-row>
      </v-expand-transition>

      <v-textarea
        v-model="formData.address"
        label="Address"
        variant="outlined"
        prepend-inner-icon="mdi-map-marker-outline"
        rows="2"
        class="mb-6"
      ></v-textarea>

      <!-- Payment Button -->
      <v-btn
        v-if="paymentStatus !== 'success'"
        color="primary"
        block
        size="large"
        class="font-weight-bold py-4 h-auto rounded-lg"
        @click="proceedToPayment"
        :loading="paymentLoading"
        :disabled="!isFormValid"
      >
        {{ paymentStatus === 'failure' ? 'Retry Payment' : 'Proceed to Payment' }}
      </v-btn>
    </v-form>

    <!-- Success State -->
    <v-fade-transition>
      <div v-if="paymentStatus === 'success'" class="text-center">
        <v-icon color="success" size="64" class="mb-4">mdi-check-decagram</v-icon>
        <h3 class="text-h5 font-weight-bold mb-2">Payment Successful!</h3>
        <p class="text-muted mb-6">Thank you for your generous contribution.</p>
        
        <v-alert
          type="info"
          variant="tonal"
          class="mb-6 text-left"
          border="start"
        >
          <strong>Payment ID:</strong> {{ paymentId }}
        </v-alert>

        <v-btn
          color="success"
          block
          size="large"
          prepend-icon="mdi-file-document-outline"
          class="font-weight-bold py-4 h-auto rounded-lg"
          @click="generateInvoice"
          :loading="invoiceLoading"
        >
          Generate Invoice
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

// Loading states
const emailLoading = ref(false);
const phoneLoading = ref(false);
const paymentLoading = ref(false);
const invoiceLoading = ref(false);

// Visibility/Verification states
const showEmailOtp = ref(false);
const emailVerified = ref(false);
const showPhoneOtp = ref(false);
const phoneVerified = ref(false);

// Payment states
const paymentStatus = ref('pending'); // pending, success, failure
const paymentId = ref('');

const isFormValid = computed(() => {
  return formData.name && emailVerified.value && phoneVerified.value && formData.address;
});

const sendOtp = (type) => {
  if (type === 'email') {
    emailLoading.value = true;
    setTimeout(() => {
      emailLoading.value = false;
      showEmailOtp.value = true;
      alert(`OTP sent to ${formData.email}`);
    }, 1000);
  } else {
    phoneLoading.value = true;
    setTimeout(() => {
      phoneLoading.value = false;
      showPhoneOtp.value = true;
      alert(`OTP sent to ${formData.phone}`);
    }, 1000);
  }
};

const verifyOtp = (type) => {
  if (type === 'email') {
    emailLoading.value = true;
    setTimeout(() => {
      emailLoading.value = false;
      emailVerified.value = true;
    }, 1000);
  } else {
    phoneLoading.value = true;
    setTimeout(() => {
      phoneLoading.value = false;
      phoneVerified.value = true;
    }, 1000);
  }
};

const proceedToPayment = () => {
  paymentLoading.value = true;
  
  // Simulated Razorpay integration
  setTimeout(() => {
    const success = Math.random() > 0.2; // 80% success rate for mock
    
    if (success) {
      paymentStatus.value = 'success';
      paymentId.value = 'pay_' + Math.random().toString(36).substr(2, 9).toUpperCase();
      console.log('Payment data sent to backend:', { ...formData, paymentId: paymentId.value });
    } else {
      paymentStatus.value = 'failure';
      alert('Payment failed. Please try again.');
    }
    paymentLoading.value = false;
  }, 2000);
};

const generateInvoice = () => {
  invoiceLoading.value = true;
  setTimeout(() => {
    invoiceLoading.value = false;
    alert('Invoice request sent to backend. You will receive it shortly.');
  }, 1500);
};
</script>

<style scoped>
.modern-card {
  border-radius: 24px !important;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.primary-accent-bar {
  height: 8px;
  background: linear-gradient(90deg, var(--v-theme-primary), var(--v-theme-primary-darken-1));
}
.v-text-field :deep(.v-field--outline) {
  border-radius: 12px;
}
</style>
