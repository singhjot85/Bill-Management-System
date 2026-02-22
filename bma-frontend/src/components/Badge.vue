<template>
    <span :class="badgeClass">
        <slot />
    </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    variant?: 'default' | 'success' | 'warning' | 'danger'
    rounded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    variant: 'default',
    rounded: true,
})

const variantMap = {
    default: 'bg-primary text-white',
    success: 'bg-green-500 text-white',
    warning: 'bg-warning text-white',
    danger: 'bg-danger text-white',
}

const badgeClass = computed(() => [
    'inline-block',
    'px-3 py-1',
    'text-xs font-medium',
    variantMap[props.variant],
    props.rounded ? 'rounded-full' : 'rounded-md',
])
</script>
