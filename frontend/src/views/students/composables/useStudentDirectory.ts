import { computed, ref, watch, type Ref } from 'vue'

import type { StudentProfile } from '../../../api/students'

export function useStudentDirectory(students: Ref<StudentProfile[]>) {
  const selectedId = ref<number | null>(null)
  const studentKeyword = ref('')
  const degreeFilter = ref('')
  const studentPage = ref(1)
  const studentPageSize = ref(12)

  const filteredStudents = computed(() => {
    const keyword = studentKeyword.value.trim().toLowerCase()
    return students.value.filter((student) => {
      const matchesDegree = !degreeFilter.value || student.degree_type === degreeFilter.value
      const haystack = `${student.name} ${student.grade} ${student.research_direction} ${student.research_topic} ${student.user_email} ${student.user_username}`.toLowerCase()
      return matchesDegree && (!keyword || haystack.includes(keyword))
    })
  })
  const studentTotalPages = computed(() => Math.max(1, Math.ceil(filteredStudents.value.length / studentPageSize.value)))
  const pagedStudents = computed(() => filteredStudents.value.slice((studentPage.value - 1) * studentPageSize.value, studentPage.value * studentPageSize.value))
  const selectedStudent = computed(() => students.value.find((item) => item.id === selectedId.value) || filteredStudents.value[0] || students.value[0])

  function selectStudent(id: number) {
    selectedId.value = id
  }

  function reconcileSelection(preferredId?: number) {
    const next = preferredId || selectedStudent.value?.id || filteredStudents.value[0]?.id || students.value[0]?.id || null
    selectedId.value = next
  }

  watch([studentKeyword, degreeFilter], () => {
    studentPage.value = 1
    if (filteredStudents.value.length && !filteredStudents.value.some((student) => student.id === selectedId.value)) {
      selectedId.value = filteredStudents.value[0].id
    }
  })
  watch(studentPageSize, () => { studentPage.value = 1 })
  watch(studentTotalPages, (total) => {
    if (studentPage.value > total) studentPage.value = total
  })

  return {
    selectedId,
    studentKeyword,
    degreeFilter,
    studentPage,
    studentPageSize,
    filteredStudents,
    studentTotalPages,
    pagedStudents,
    selectedStudent,
    selectStudent,
    reconcileSelection,
  }
}

