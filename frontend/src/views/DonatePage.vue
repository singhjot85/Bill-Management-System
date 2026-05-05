<template>
  <v-container class="py-16 text-center">
    <h1 class="text-h2 font-weight-black mb-6">Support Our Cause</h1>
    <p class="text-h6 text-muted mb-10">Choose an amount and your preferred payment method.</p>
    
    <v-card class="modern-card mx-auto pa-8" max-width="500">
      <v-form>
        <v-text-field label="Amount ($)" variant="outlined" class="mb-4" type="number"></v-text-field>
        <v-select label="Payment Method" :items="['Credit Card', 'PayPal', 'Wire Transfer']" variant="outlined" class="mb-6"></v-select>
        <v-btn color="primary" block size="large" class="font-weight-bold">Complete Donation</v-btn>
      </v-form>
    </v-card>
  </v-container>
</template>
