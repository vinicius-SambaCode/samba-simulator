<!-- pages/dashboard/coordenador/simulados/[id]/editar.vue -->
<template>
  <div class="max-w-2xl mx-auto space-y-5">

    <!-- Voltar -->
    <div class="animate-fade-in">
      <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}`"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-gray-400 hover:text-gray-700 transition-colors mb-4">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" />
        Voltar para o simulado
      </NuxtLink>
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-xl font-black text-gray-900 tracking-tight">Configurar simulado</h2>
          <p class="text-sm text-gray-400 mt-0.5">
            <span v-if="!loading">{{ exam?.title }}</span>
            <span v-else class="inline-block w-32 h-4 bg-gray-100 rounded animate-pulse" />
          </p>
        </div>
        <span v-if="exam?.status === 'locked'"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 text-xs font-bold rounded-xl">
          <Icon name="lucide:lock" class="w-3.5 h-3.5" />
          Simulado travado
        </span>
      </div>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-40 bg-white rounded-2xl border border-gray-100 animate-pulse" />
    </div>

    <template v-else>

      <!-- Info básica -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:40ms">
        <div class="flex items-center gap-2 px-5 py-4 border-b border-gray-50">
          <Icon name="lucide:info" class="w-4 h-4 text-gray-400" />
          <h3 class="text-sm font-bold text-gray-900">Informações básicas</h3>
        </div>
        <div class="p-5 grid grid-cols-2 gap-4">
          <div>
            <p class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Título</p>
            <p class="text-sm font-semibold text-gray-800">{{ exam?.title }}</p>
          </div>
          <div>
            <p class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Área</p>
            <p class="text-sm font-semibold text-gray-800">{{ exam?.area || '—' }}</p>
          </div>
          <div>
            <p class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Alternativas</p>
            <p class="text-sm font-semibold text-gray-800">{{ exam?.options_count }} (A–{{ exam?.options_count === 4 ? 'D' : 'E' }})</p>
          </div>
          <div>
            <p class="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Gabarito por</p>
            <p class="text-sm font-semibold text-gray-800">
              {{ exam?.answer_source === 'teachers' ? 'Professores' : 'Coordenador' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Cotas por disciplina -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:80ms">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <Icon name="lucide:target" class="w-4 h-4 text-gray-400" />
            <h3 class="text-sm font-bold text-gray-900">Cotas por disciplina</h3>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="quotasSuccess" class="text-[11px] font-bold text-emerald-600 flex items-center gap-1">
              <Icon name="lucide:check" class="w-3 h-3" /> Salvo!
            </span>
            <button
              :disabled="savingQuotas || exam?.status === 'locked'"
              class="text-[11px] font-bold px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5"
              :class="savingQuotas || exam?.status === 'locked'
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
              @click="saveQuotas">
              <svg v-if="savingQuotas" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              <Icon v-else name="lucide:save" class="w-3 h-3" />
              {{ savingQuotas ? 'Salvando...' : 'Salvar cotas' }}
            </button>
          </div>
        </div>

        <div class="p-5 space-y-2">
          <div class="flex items-center justify-between px-4 py-2.5 bg-gray-50 rounded-xl mb-4">
            <span class="text-xs font-bold text-gray-500">Total esperado</span>
            <span class="text-lg font-black text-gray-900 tabular-nums">
              {{ Object.values(quotaForm).reduce((a, b) => a + b, 0) }}
            </span>
          </div>

          <div v-for="disc in disciplines" :key="disc.id"
            class="flex items-center gap-4 p-3.5 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-gray-800">{{ disc.name }}</p>
              <p class="text-[11px] text-gray-400 mt-0.5">
                <span class="font-semibold text-gray-600">{{ quotaMap[disc.id]?.submitted ?? 0 }}</span>
                enviadas
                <span v-if="quotaForm[disc.id] > 0"> de <span class="font-semibold">{{ quotaForm[disc.id] }}</span></span>
              </p>
              <div v-if="quotaForm[disc.id] > 0" class="mt-2 h-1 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-300"
                  :class="(quotaMap[disc.id]?.submitted ?? 0) >= quotaForm[disc.id] ? 'bg-emerald-400' : 'bg-blue-300'"
                  :style="`width:${Math.min(100, ((quotaMap[disc.id]?.submitted ?? 0) / quotaForm[disc.id]) * 100)}%`" />
              </div>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <button :disabled="exam?.status === 'locked'"
                class="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center font-black text-base text-gray-500 transition-colors"
                :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-50'"
                @click="changeQuota(disc.id, -1)">−</button>
              <input :value="quotaForm[disc.id] ?? 0"
                :disabled="exam?.status === 'locked'"
                type="number" min="0" max="99"
                class="w-14 text-center text-sm font-black text-gray-900 border border-gray-200 rounded-lg py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 tabular-nums"
                :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : ''"
                @input="setQuota(disc.id, Number(($event.target as HTMLInputElement).value))" />
              <button :disabled="exam?.status === 'locked'"
                class="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center font-black text-base text-gray-500 transition-colors"
                :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-50'"
                @click="changeQuota(disc.id, 1)">+</button>
            </div>
          </div>

          <div v-if="quotasError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl mt-2">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500 font-medium">{{ quotasError }}</p>
          </div>
        </div>
      </div>

      <!-- Atribuir professores por turma -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:120ms">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <Icon name="lucide:user-check" class="w-4 h-4 text-gray-400" />
            <h3 class="text-sm font-bold text-gray-900">Professores por turma</h3>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="teachersSuccess" class="text-[11px] font-bold text-emerald-600 flex items-center gap-1">
              <Icon name="lucide:check" class="w-3 h-3" /> Salvo!
            </span>
          </div>
        </div>

        <div class="p-5">
          <p class="text-xs text-gray-400 mb-4 leading-relaxed">
            Defina qual professor é responsável por cada disciplina em cada turma.
            Isso permite que o professor envie questões para o simulado.
          </p>

          <div v-if="!assignedClasses.length"
            class="text-center py-10">
            <Icon name="lucide:users" class="w-8 h-8 text-gray-200 mx-auto mb-2" />
            <p class="text-xs text-gray-400">Nenhuma turma vinculada ainda.</p>
            <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}`"
              class="text-xs font-bold text-blue-500 hover:text-blue-600 mt-1 inline-block">
              Vincular turmas →
            </NuxtLink>
          </div>

          <div v-else class="space-y-5">
            <div v-for="cls in assignedClasses" :key="cls.id">
              <!-- Header turma -->
              <div class="flex items-center gap-2 mb-2">
                <div class="w-6 h-6 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
                  <Icon name="lucide:users" class="w-3 h-3 text-blue-500" />
                </div>
                <p class="text-xs font-black text-gray-700 uppercase tracking-wide">{{ cls.name }}</p>
              </div>

              <div class="space-y-2 pl-8">
                <div v-for="disc in disciplines" :key="disc.id"
                  class="flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors">
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-bold text-gray-700">{{ disc.name }}</p>
                    <!-- Vínculo existente -->
                    <p v-if="getExistingLink(cls.id, disc.id)" class="text-[11px] text-emerald-600 font-semibold mt-0.5 flex items-center gap-1">
                      <Icon name="lucide:check" class="w-2.5 h-2.5" />
                      {{ teacherName(getExistingLink(cls.id, disc.id)!.teacher_user_id) }}
                    </p>
                  </div>

                  <div class="flex items-center gap-2 flex-shrink-0">
                    <select
                      v-model="teacherForm[`${cls.id}_${disc.id}`]"
                      class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-700 max-w-[150px]">
                      <option value="">— selecionar —</option>
                      <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.name }}</option>
                    </select>
                    <button
                      :disabled="!teacherForm[`${cls.id}_${disc.id}`] || savingTeacher[`${cls.id}_${disc.id}`]"
                      class="px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition-all flex items-center gap-1"
                      :class="!teacherForm[`${cls.id}_${disc.id}`] || savingTeacher[`${cls.id}_${disc.id}`]
                        ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                        : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
                      @click="saveTeacherLink(cls.id, disc.id)">
                      <svg v-if="savingTeacher[`${cls.id}_${disc.id}`]" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                      </svg>
                      <Icon v-else name="lucide:link" class="w-3 h-3" />
                      Vincular
                    </button>
                    <!-- Remover vínculo existente -->
                    <button
                      v-if="getExistingLink(cls.id, disc.id)"
                      class="w-7 h-7 rounded-lg hover:bg-red-50 flex items-center justify-center transition-colors"
                      @click="removeTeacherLink(getExistingLink(cls.id, disc.id)!.id)">
                      <Icon name="lucide:x" class="w-3 h-3 text-gray-300 hover:text-red-400" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="teachersError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl mt-4">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500 font-medium">{{ teachersError }}</p>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const { get, post, delete: del } = useApi()
const examId = computed(() => Number(route.params.id))

// Data
const exam            = ref<any>(null)
const disciplines     = ref<any[]>([])
const allClasses      = ref<any[]>([])
const assignedClasses = ref<any[]>([])
const teachers        = ref<any[]>([])
const teacherSubjects = ref<any[]>([])
const loading         = ref(true)

// Cotas
const quotaForm     = reactive<Record<number, number>>({})
const quotaMap      = ref<Record<number, any>>({})
const savingQuotas  = ref(false)
const quotasError   = ref('')
const quotasSuccess = ref(false)

// Professores
const teacherForm    = reactive<Record<string, number | ''>>({})
const savingTeacher  = reactive<Record<string, boolean>>({})
const teachersError  = ref('')
const teachersSuccess = ref(false)

// Helpers
function changeQuota(discId: number, delta: number) {
  quotaForm[discId] = Math.max(0, (quotaForm[discId] ?? 0) + delta)
}
function setQuota(discId: number, val: number) {
  quotaForm[discId] = Math.max(0, isNaN(val) ? 0 : val)
}
function teacherName(id: number) {
  return teachers.value.find(t => t.id === id)?.name ?? `Prof. #${id}`
}
function getExistingLink(classId: number, discId: number) {
  return teacherSubjects.value.find(
    ts => ts.class_id === classId && ts.discipline_id === discId
  ) ?? null
}

async function saveQuotas() {
  savingQuotas.value = true
  quotasError.value  = ''
  quotasSuccess.value = false
  try {
    const items = Object.entries(quotaForm)
      .filter(([, v]) => v > 0)
      .map(([discipline_id, quota]) => ({ discipline_id: Number(discipline_id), quota }))
    if (!items.length) throw new Error('Defina ao menos uma cota maior que zero.')
    await post(`/exams/${examId.value}/quotas`, { items })
    quotasSuccess.value = true
    setTimeout(() => quotasSuccess.value = false, 3000)
  } catch (e: any) {
    quotasError.value = e.message ?? 'Erro ao salvar cotas.'
  } finally {
    savingQuotas.value = false
  }
}

async function saveTeacherLink(classId: number, discId: number) {
  const key = `${classId}_${discId}`
  const teacherId = teacherForm[key]
  if (!teacherId) return

  savingTeacher[key] = true
  teachersError.value = ''

  try {
    // Remove vínculo existente se houver
    const existing = getExistingLink(classId, discId)
    if (existing) {
      await del(`/school/teacher-subjects/${existing.id}`)
      teacherSubjects.value = teacherSubjects.value.filter(ts => ts.id !== existing.id)
    }

    // Cria novo vínculo
    const created = await post<any>('/school/teacher-subjects', {
      teacher_user_id: Number(teacherId),
      class_id: classId,
      discipline_id: discId,
    })
    teacherSubjects.value.push(created)

    // Também vincula ao simulado
    await post(`/exams/${examId.value}/assign-teachers`, {
      items: [{
        class_id: classId,
        discipline_id: discId,
        teacher_user_id: Number(teacherId),
      }]
    }).catch(() => {}) // ignora erro se já existir

    teacherForm[key] = ''
    teachersSuccess.value = true
    setTimeout(() => teachersSuccess.value = false, 3000)
  } catch (e: any) {
    teachersError.value = e.message ?? 'Erro ao vincular professor.'
  } finally {
    savingTeacher[key] = false
  }
}

async function removeTeacherLink(linkId: number) {
  try {
    await del(`/school/teacher-subjects/${linkId}`)
    teacherSubjects.value = teacherSubjects.value.filter(ts => ts.id !== linkId)
  } catch (e: any) {
    teachersError.value = e.message ?? 'Erro ao remover vínculo.'
  }
}

onMounted(async () => {
  const [examRes, discRes, progressRes, examClassesRes, allClassesRes, teachersRes, subjectsRes] = await Promise.allSettled([
    get<any>(`/exams/${examId.value}`),
    get<any[]>('/disciplines/'),
    get<any>(`/exams/${examId.value}/progress`),
    get<any[]>(`/exams/${examId.value}/classes`),  // endpoint dedicado
    get<any[]>('/school/classes'),
    get<any[]>('/school/teachers'),
    get<any[]>('/school/teacher-subjects'),
  ])

  if (examRes.status === 'fulfilled')      exam.value            = examRes.value
  if (discRes.status === 'fulfilled')      disciplines.value     = discRes.value
  if (allClassesRes.status === 'fulfilled') allClasses.value     = allClassesRes.value
  if (teachersRes.status === 'fulfilled')  teachers.value        = teachersRes.value
  if (subjectsRes.status === 'fulfilled')  teacherSubjects.value = subjectsRes.value

  // Quotas
  if (progressRes.status === 'fulfilled' && progressRes.value?.disciplines) {
    for (const d of progressRes.value.disciplines) {
      quotaForm[d.discipline_id] = d.quota
      quotaMap.value[d.discipline_id] = d
    }
  }
  if (discRes.status === 'fulfilled') {
    for (const d of discRes.value) {
      if (quotaForm[d.id] === undefined) quotaForm[d.id] = 0
    }
  }

  // Turmas do simulado via endpoint dedicado
  // examClassesRes retorna [{class_id, class_name}]
  // Precisamos do objeto completo (com .id e .name) para o template
  if (examClassesRes.status === 'fulfilled' && allClassesRes.status === 'fulfilled') {
    const ids = new Set(examClassesRes.value.map((c: any) => c.class_id))
    assignedClasses.value = allClasses.value.filter(c => ids.has(c.id))
  }

  loading.value = false
})
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }
</style>