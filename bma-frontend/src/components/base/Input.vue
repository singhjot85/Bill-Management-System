<template>
    <div :class="wrapperClass">
        <label v-if="variant === 'above' && label" :for="id" :class="labelAboveClass">
            {{ label }}
        </label>

        <div :class="containerClass">
            <span v-if="variant === 'before' && label" :class="labelBeforeClass">
                {{ label }}
            </span>

            <input :id="id" :type="type" :value="modelValue" :placeholder="variant === 'inside' ? label : ''"
                :disabled="disabled" :class="inputClass" :style="inputStyle" @input="updateValue" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    modelValue?: string | number
    id?: string
    type?: string
    label?: string
    disabled?: boolean
    variant?: 'inside' | 'before' | 'above'
    width?: string
    height?: string
}

const props = withDefaults(defineProps<Props>(), {
    type: 'text',
    variant: 'inside',
    disabled: false,
    width: '250px',
    height: '40px',
})

const emit = defineEmits(['update:modelValue'])

/* ---------------- Layout ---------------- */

const wrapperClass = 'mb-4'

const containerClass = computed(() =>
    props.variant === 'before'
        ? 'flex items-center gap-2'
        : ''
)

/* ---------------- Input Styling ---------------- */

const inputClass = computed(() => [
    'px-4',
    'border border-border',
    'rounded-md',
    'bg-surface',
    'text-text',
    'outline-none',
    'transition',
    'focus:ring-2 focus:ring-primary',
    props.disabled && 'opacity-60 cursor-not-allowed',
])

const inputStyle = computed(() => ({
    width: props.width,
    height: props.height,
}))

/* ---------------- Labels ---------------- */

const labelAboveClass =
    'block mb-1 text-sm font-medium text-text'

const labelBeforeClass =
    'text-sm font-medium text-text whitespace-nowrap'

/* ---------------- Emit ---------------- */

function updateValue(e: Event) {
    emit('update:modelValue', (e.target as HTMLInputElement).value)
}
</script>
