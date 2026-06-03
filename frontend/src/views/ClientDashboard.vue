<template>
    <p>Hello Mr. {{ authStore?.user?.first_name }} {{ authStore?.user?.last_name }}</p>
</template>
<script setup lang="ts">

import { useAuthStore } from "@/stores/authStore";

const authStore = useAuthStore();
console.log(authStore)
</script>
