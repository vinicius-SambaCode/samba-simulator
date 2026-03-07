<!-- components/dashboard/StatCard.vue -->
<template>
  <div class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm flex items-start gap-4">
    <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" :class="iconBg">
      <Icon :name="icon" class="w-5 h-5" :class="iconColor" />
    </div>
    <div>
      <p class="text-2xl font-bold text-gray-900">{{ value }}</p>
      <p class="text-sm text-gray-500 mt-0.5">{{ label }}</p>
      <p
        v-if="change"
        class="text-xs mt-1 font-medium"
        :class="changePositive === true ? 'text-emerald-600' : changePositive === false ? 'text-red-500' : 'text-gray-400'"
      >
        {{ changePositive === true ? '↑' : changePositive === false ? '↓' : '' }} {{ change }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string
  change?: string
  changePositive?: boolean | null
  icon: string
  iconBg: string
  iconColor: string
}>()
</script>