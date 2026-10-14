<script setup lang="ts">
import type { ThemeItem } from '@/api/types'
import PixelIcon from '@/components/ui/PixelIcon.vue'
defineProps<{ item: ThemeItem }>()
</script>
<template>
  <div class="achievement-detail">
    <PixelIcon :name="item.name" :locked="!item.unlocked" />
    <div>
      <p class="eyebrow">
        {{ item.unlocked ? 'ACHIEVEMENT UNLOCKED' : 'LOCKED OBJECTIVE' }}
      </p>
      <h3>{{ item.name }}</h3>
      <p>{{ item.description }}</p>
      <small>{{
        item.acquired_date
          ? `Acquired ${item.acquired_date}`
          : 'Keep playing. This one is waiting for you.'
      }}</small>
    </div>
    <strong>+{{ item.exp_value }} XP</strong>
  </div>
</template>
