<template>
  <v-footer class="bg-grey-lighten-4 py-12 px-md-6 px-4 border-t">
    <v-container>
      <v-row>
        <v-col cols="12" md="4">
          <div class="d-flex align-center mb-4">
            <v-img :src="branding.logoUrl" width="30" height="30" class="mr-2"></v-img>
            <span class="text-h6 font-weight-bold">{{ branding.tenantName }}</span>
          </div>
          <p class="text-muted text-body-2">Modern bill management and donation platform.</p>
        </v-col>
        <v-col cols="12" md="4">
          <h4 class="font-weight-bold mb-4">Quick Links</h4>
          <v-list density="compact" class="bg-transparent pa-0">
            <v-list-item class="pa-0" to="/">Home</v-list-item>
            <v-list-item class="pa-0" to="/login">Login</v-list-item>
          </v-list>
        </v-col>
        <v-col cols="12" md="4">
          <h4 class="font-weight-bold mb-4">Contact</h4>
          <p class="text-muted text-body-2">{{ branding.contactInfo || 'contact@example.com' }}</p>
        </v-col>
      </v-row>
      <v-divider class="my-8"></v-divider>
      <div class="text-center text-muted text-caption">
        &copy; {{ new Date().getFullYear() }} {{ branding.tenantName }}. All rights reserved.
      </div>
    </v-container>
  </v-footer>
</template>

<script setup>
defineProps({
  branding: Object
});
</script>
