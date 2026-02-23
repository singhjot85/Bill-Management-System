<template>
    <div :class="wrapperClass" :style="wrapperStyle">
        <div :class="spinnerClass" :style="spinnerStyle"></div>

        <span v-if="label" class="mt-2 text-sm text-text">
            {{ label }}
        </span>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    size?: string
    color?: string
    thickness?: string
    speed?: string
    label?: string

    /* NEW */
    padding?: string
    margin?: string
    bordered?: boolean
    borderColor?: string
    borderRadius?: string
    background?: string
}

const props = withDefaults(defineProps<Props>(), {
    size: '40px',
    color: '#3b82f6',
    thickness: '4px',
    speed: '0.8s',

    /* Defaults */
    padding: '12px',
    margin: '5px',
    bordered: false,
    borderColor: '#e5e7eb',
    borderRadius: '8px',
    background: 'transparent',
})

/* Wrapper */

const wrapperClass =
    'flex flex-col items-center justify-center'

const wrapperStyle = computed(() => ({
    width: props.size,
    padding: props.padding,
    margin: props.margin,
    background: props.background,
    border: props.bordered ? `1px solid ${props.borderColor}` : 'none',
    borderRadius: props.borderRadius,
}))

/* Spinner */

const spinnerClass =
    'rounded-full animate-spin'

const spinnerStyle = computed(() => ({
    width: props.size,
    height: props.size,
    border: `${props.thickness} solid rgba(0,0,0,0.1)`,
    borderTop: `${props.thickness} solid ${props.color}`,
    animationDuration: props.speed,
}))
</script>
