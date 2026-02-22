<template>
    <div :class="cardClass" :style="cardStyle">

        <div v-if="$slots.header" :class="headerClass">
            <slot name="header" />
        </div>

        <div :class="bodyClass">
            <slot />
        </div>

        <div v-if="$slots.footer" :class="footerClass">
            <slot name="footer" />
        </div>

    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    padding?: 'sm' | 'md' | 'lg'
    margin?: 'none' | 'sm' | 'md' | 'lg'
    shadow?: boolean
    bordered?: boolean
    rounded?: 'sm' | 'md' | 'lg'
    width?: string
    height?: string
}

const props = withDefaults(defineProps<Props>(), {
    padding: 'md',
    margin: 'md',
    shadow: true,
    bordered: true,
    rounded: 'md',
    width: '300px',
    height: 'auto',
})

/* ---------------- Maps ---------------- */

const paddingMap = {
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-8',
}

const marginMap = {
    none: '',
    sm: 'm-2',
    md: 'm-4',
    lg: 'm-6',
}

const radiusMap = {
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
}

/* ---------------- Card ---------------- */

const cardClass = computed(() => [
    'bg-surface',
    marginMap[props.margin],
    props.bordered && 'border border-border',
    props.shadow && 'shadow-sm',
    radiusMap[props.rounded],
])

const cardStyle = computed(() => ({
    width: props.width,
    height: props.height,
}))

/* ---------------- Sections ---------------- */

const headerClass = computed(() => [
    'border-b border-border',
    'font-semibold text-text',
    paddingMap[props.padding],
])

const bodyClass = computed(() => [
    'text-text',
    paddingMap[props.padding],
])

const footerClass = computed(() => [
    'border-t border-border',
    paddingMap[props.padding],
])
</script>
