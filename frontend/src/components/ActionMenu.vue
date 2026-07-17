<template>
  <el-dropdown trigger="click" @command="$emit('command', $event)">
    <el-button class="action-menu-trigger" :size="size" plain :aria-label="label">
      <span>{{ label }}</span><el-icon><MoreFilled /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="item in items"
          :key="item.command"
          :command="item.command"
          :disabled="item.disabled"
          :divided="item.divided"
          :class="{ 'is-danger': item.danger }"
        >{{ item.label }}</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { MoreFilled } from '@element-plus/icons-vue'

export type ActionMenuItem = {
  command: string
  label: string
  disabled?: boolean
  divided?: boolean
  danger?: boolean
}

withDefaults(defineProps<{ items: ActionMenuItem[]; label?: string; size?: 'small' | 'default' | 'large' }>(), {
  label: '更多',
  size: 'small',
})
defineEmits<{ command: [command: string] }>()
</script>

<style scoped>
.action-menu-trigger {
  gap: 5px;
  margin: 0;
}

:global(.el-dropdown-menu__item.is-danger) {
  color: var(--color-danger, #9f3a38);
}
</style>
