<template>
    <span :class="badgeClass" :style="badgeStyle">
        <slot />
    </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    variant?: 'default' | 'success' | 'warning' | 'danger'
    rounded?: boolean

    padding?: string
    margin?: string
    bordered?: boolean
    borderColor?: string
    radius?: 'sm' | 'md' | 'lg' | 'full'
}

const props = withDefaults(defineProps<Props>(), {
    variant: 'default',
    rounded: true,
    padding: '6px 12px',
    margin: '0px',
    bordered: false,
    borderColor: '#e5e7eb',
    radius: 'full',
})

const variantMap = {
    default: 'bg-primary text-white',
    success: 'bg-green-500 text-white',
    warning: 'bg-warning text-white',
    danger: 'bg-danger text-white',
}

const radiusMap = {
    sm: '4px',
    md: '8px',
    lg: '12px',
    full: '9999px',
}

const badgeClass = computed(() => [
    'inline-block',
    'text-xs font-medium',
    variantMap[props.variant],
])

const badgeStyle = computed(() => ({
    padding: props.padding,
    margin: props.margin,
    border: props.bordered ? `1px solid ${props.borderColor}` : 'none',
    borderRadius: props.rounded
        ? '9999px'
        : radiusMap[props.radius],
}))
</script>
