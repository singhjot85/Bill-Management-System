<template>
    <button :disabled="isDisabled" :class="buttonClasses" @click="handleClick">
        <span v-if="loading" class="animate-pulse">
            Loading...
        </span>

        <slot v-else />
    </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    variant?: 'simple' | 'warning' | 'danger' | 'disabled'
    size?: 'sm' | 'md' | 'lg'
    loading?: boolean
    disabled?: boolean

    /* New configurable props */
    rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full'
    padding?: 'none' | 'sm' | 'md' | 'lg'
    margin?: 'none' | 'sm' | 'md' | 'lg'
    bordered?: boolean
    block?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    variant: 'simple',
    size: 'md',
    loading: false,
    disabled: false,

    rounded: 'md',
    padding: 'md',
    margin: 'sm',
    bordered: false,
    block: false,
})

/* -------------------------- Disabled -------------------------- */

const isDisabled = computed(() => {
    return props.disabled || props.variant === 'disabled' || props.loading
})

/* -------------------------- Base -------------------------- */

const baseClasses =
    'inline-flex items-center justify-center font-medium transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'

/* -------------------------- Size -------------------------- */

const sizeClasses = computed(() => {
    switch (props.size) {
        case 'sm':
            return 'text-sm'
        case 'lg':
            return 'text-lg'
        default:
            return 'text-base'
    }
})

/* -------------------------- Padding -------------------------- */

const paddingClasses = computed(() => {
    switch (props.padding) {
        case 'none':
            return ''
        case 'sm':
            return 'px-3 py-1'
        case 'lg':
            return 'px-6 py-3'
        default:
            return 'px-4 py-2'
    }
})

/* -------------------------- Margin -------------------------- */

const marginClasses = computed(() => {
    switch (props.margin) {
        case 'sm':
            return 'm-2'
        case 'md':
            return 'm-4'
        case 'lg':
            return 'm-6'
        default:
            return ''
    }
})

/* -------------------------- Radius -------------------------- */

const radiusClasses = computed(() => {
    switch (props.rounded) {
        case 'none':
            return 'rounded-none'
        case 'sm':
            return 'rounded-sm'
        case 'lg':
            return 'rounded-lg'
        case 'full':
            return 'rounded-full'
        default:
            return 'rounded-md'
    }
})

/* -------------------------- Border -------------------------- */

const borderClasses = computed(() => {
    return props.bordered ? 'border border-border' : ''
})

/* -------------------------- Width -------------------------- */

const widthClasses = computed(() => {
    return props.block ? 'w-full' : ''
})

/* -------------------------- Variants -------------------------- */

const variantClasses = computed(() => {
    if (isDisabled.value) {
        return 'bg-gray-300 text-gray-500 cursor-not-allowed dark:bg-gray-700 dark:text-gray-400'
    }

    switch (props.variant) {
        case 'warning':
            return 'bg-warning text-white hover:opacity-90'
        case 'danger':
            return 'bg-danger text-white hover:opacity-90'
        default:
            return 'bg-primary text-white hover:bg-primaryHover'
    }
})

/* -------------------------- Final Class Builder -------------------------- */

const buttonClasses = computed(() => {
    return [
        baseClasses,
        sizeClasses.value,
        paddingClasses.value,
        marginClasses.value,
        radiusClasses.value,
        borderClasses.value,
        widthClasses.value,
        variantClasses.value,
    ].join(' ')
})

function handleClick(event: Event) {
    if (isDisabled.value) {
        event.preventDefault()
    }
}
</script>
