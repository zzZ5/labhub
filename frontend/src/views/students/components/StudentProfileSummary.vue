<template>
  <section class="card profile-card">
    <div class="profile-heading">
      <div class="student-profile-avatar">
        <img v-if="student.avatar" :src="student.avatar" :alt="student.name" />
        <span v-else>{{ student.name.slice(0, 1) }}</span>
      </div>
      <div class="profile-copy">
        <h1>{{ student.name }}</h1>
        <p>{{ student.research_direction || student.research_topic || '研究方向待补充' }}</p>
      </div>
      <div class="profile-actions">
        <el-button v-if="student.can_edit" plain @click="$emit('edit', student)">编辑档案</el-button>
        <el-button v-if="student.can_delete" plain type="danger" @click="$emit('delete', student)">删除档案</el-button>
        <el-button v-if="student.can_edit" type="primary" @click="$emit('upload')">上传资料</el-button>
      </div>
    </div>
    <dl class="profile-list">
      <div><dt>身份</dt><dd>{{ student.degree_label }} {{ student.grade || '' }}</dd></div>
      <div><dt>导师</dt><dd>{{ advisorText }}</dd></div>
      <div><dt>研究题目</dt><dd>{{ student.research_topic || '-' }}</dd></div>
      <div><dt>登录账号</dt><dd>{{ student.user_email || student.user_username || '-' }}</dd></div>
    </dl>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { StudentProfile } from '../../../api/students'

const props = defineProps<{ student: StudentProfile }>()
defineEmits<{
  edit: [student: StudentProfile]
  delete: [student: StudentProfile]
  upload: []
}>()

const advisorText = computed(() => {
  if (props.student.advisor_names?.length) return props.student.advisor_names.join('、')
  return props.student.supervisor_name || '-'
})
</script>

<style scoped>
.profile-card {
  padding: 16px;
}

.profile-card:hover {
  transform: none;
}

.profile-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.student-profile-avatar {
  display: grid;
  flex: 0 0 58px;
  width: 58px;
  height: 58px;
  place-items: center;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 50%;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 700;
}

.student-profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.profile-copy {
  flex: 1 1 auto;
  min-width: 0;
}

.profile-copy h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(22px, 2.4vw, 28px);
  font-weight: 650;
  line-height: 1.2;
}

.profile-copy p {
  margin: 5px 0 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.profile-actions {
  display: flex;
  flex: 0 0 auto;
  align-items: flex-start;
  gap: 8px;
}

.profile-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 14px 0 0;
  border-top: 1px solid var(--color-line);
  padding-top: 12px;
}

.profile-list div {
  display: grid;
  gap: 4px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 9px 11px;
  background: var(--color-panel);
}

.profile-list dt,
.profile-list dd {
  margin: 0;
}

.profile-list dt {
  color: var(--color-muted);
  font-size: 13px;
}

.profile-list dd {
  color: var(--color-text);
  font-weight: 600;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

@media (max-width: 760px) {
  .profile-heading,
  .profile-actions {
    flex-wrap: wrap;
  }

  .profile-list {
    grid-template-columns: 1fr;
  }
}
</style>
