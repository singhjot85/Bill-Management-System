<template>
    <div v-if="show" :class="overlayClass" :style="overlayStyle">
        <Spinner v-if="useSpinner" :size="spinnerSize" :color="spinnerColor" :label="spinnerLabel" />
        <slot v-else />
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Spinner from './Spinner.vue'

interface Props {
    show?: boolean
    background?: string
    opacity?: number
    blur?: boolean
    zIndex?: number
    fullscreen?: boolean

    /* Spinner Options */
    useSpinner?: boolean
    spinnerSize?: string
    spinnerColor?: string
    spinnerLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
    show: false,
    background: '#000',
    opacity: 0.4,
    blur: false,
    zIndex: 50,
    fullscreen: true,

    useSpinner: true,
    spinnerSize: '40px',
    spinnerColor: '#ffffff',
})

const overlayClass = computed(() => [
    'flex items-center justify-center',
    'transition-all duration-200',
    props.fullscreen ? 'fixed inset-0' : 'absolute inset-0',
])

const overlayStyle = computed(() => ({
    backgroundColor: props.background,
    opacity: props.opacity,
    backdropFilter: props.blur ? 'blur(4px)' : 'none',
    zIndex: props.zIndex,
}))
</script>
