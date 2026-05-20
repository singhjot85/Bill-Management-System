<template>
  <div class="register-form">
    <div class="mb-8">
      <h3 class="text-h5 font-weight-bold mb-1">Create your account</h3>
      <p class="text-body-2 text-muted">Start your 14-day free trial. No credit card required.</p>
    </div>

    <v-form @submit.prevent="handleSubmit" v-model="isValid">
      <v-text-field
        v-model="fullName"
        label="Full Name"
        placeholder="Rajesh Sharma"
        prepend-inner-icon="mdi-account-outline"
        variant="outlined"
        :rules="[v => !!v || 'Full name is required', v => v.length >= 3 || 'Min 3 characters']"
        class="mb-2"
      />

      <v-text-field
        v-model="email"
        label="Email"
        placeholder="rajesh@company.com"
        prepend-inner-icon="mdi-email-outline"
        variant="outlined"
        :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'E-mail must be valid']"
        class="mb-2"
      />

      <v-text-field
        v-model="phone"
        label="Phone (Optional)"
        placeholder="+91 98765 43210"
        prepend-inner-icon="mdi-phone-outline"
        variant="outlined"
        class="mb-2"
      />

      <v-text-field
        v-model="password"
        label="Password"
        placeholder="Create a strong password"
        prepend-inner-icon="mdi-lock-outline"
        type="password"
        variant="outlined"
        :rules="[v => !!v || 'Password is required', v => v.length >= 8 || 'Min 8 characters']"
        class="mb-2"
      />

      <v-checkbox
        v-model="agree"
        color="primary"
        hide-details
        class="mb-6"
        :rules="[v => !!v || 'Required']"
      >
        <template v-slot:label>
          <div class="text-caption">
            I agree to the <a href="#" class="text-primary font-weight-bold text-decoration-none">Terms of Service</a> and <a href="#" class="text-primary font-weight-bold text-decoration-none">Privacy Policy</a>
          </div>
        </template>
      </v-checkbox>

      <v-btn
        color="primary"
        block
        size="large"
        height="54"
        class="font-weight-bold text-none rounded-lg"
        type="submit"
        :disabled="!isValid"
        elevation="0"
      >
        Start Free Trial <v-icon end>mdi-arrow-right</v-icon>
      </v-btn>

      <p class="mt-6 text-center text-caption text-muted">
        No credit card required. Cancel anytime. You will get 500 invoice credits on signup.
      </p>
    </v-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const isValid = ref(false);
const fullName = ref('');
const email = ref('');
const phone = ref('');
const password = ref('');
const agree = ref(false);

const handleSubmit = () => {
  if (isValid.value) {
    alert("Signup functionality coming soon!");
  }
};
</script>
