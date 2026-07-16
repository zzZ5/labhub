import { computed, ref, watch, type Ref } from 'vue'

import type { StudentProfile } from '../../../api/students'
import { useListPagination } from '../../../composables/useListPagination'
import { useDebouncedValue } from '../../../composables/useDebouncedValue'

export function useStudentDirectory(students: Ref<StudentProfile[]>) {
  const selectedId = ref<number | null>(null)
  const studentKeyword = ref('')
  const debouncedKeyword = useDebouncedValue(studentKeyword)
  const degreeFilter = ref('')

  const filteredStudents = computed(() => {
    const keyword = debouncedKeyword.value.trim().toLowerCase()
    return students.value.filter((student) => {
      const matchesDegree = !degreeFilter.value || student.degree_type === degreeFilter.value
      const haystack = `${student.name} ${student.grade} ${student.research_direction} ${student.research_topic} ${student.user_email} ${student.user_username}`.toLowerCase()
      return matchesDegree && (!keyword || haystack.includes(keyword))
    })
  })
  const filteredTotal = computed(() => filteredStudents.value.length)
  const { page: studentPage, totalPages: studentTotalPages, paginate, resetPage } = useListPagination(filteredTotal)
  const pagedStudents = computed(() => paginate(filteredStudents.value))
  const selectedStudent = computed(() => students.value.find((item) => item.id === selectedId.value) || filteredStudents.value[0] || students.value[0])

  function selectStudent(id: number) {
    selectedId.value = id
  }

  function reconcileSelection(preferredId?: number) {
    const next = preferredId || selectedStudent.value?.id || filteredStudents.value[0]?.id || students.value[0]?.id || null
    selectedId.value = next
  }

  watch([debouncedKeyword, degreeFilter], () => {
    resetPage()
    if (filteredStudents.value.length && !filteredStudents.value.some((student) => student.id === selectedId.value)) {
      selectedId.value = filteredStudents.value[0].id
    }
  })

  return {
    selectedId,
    studentKeyword,
    degreeFilter,
    studentPage,
    filteredStudents,
    studentTotalPages,
    pagedStudents,
    selectedStudent,
    selectStudent,
    reconcileSelection,
  }
}
