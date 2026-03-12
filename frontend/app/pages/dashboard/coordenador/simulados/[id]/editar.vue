<!-- pages/dashboard/coordenador/simulados/[id]/editar.vue -->
<template>
  <div class="h-[calc(100vh-4rem)] flex flex-col gap-4 overflow-hidden">

    <!-- Header compacto -->
    <div class="flex items-center justify-between gap-4 flex-shrink-0 animate-fade-in">
      <div class="flex items-center gap-3">
        <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}`"
          class="w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center transition-colors">
          <Icon name="lucide:arrow-left" class="w-4 h-4 text-gray-400" />
        </NuxtLink>
        <div>
          <h2 class="text-lg font-black text-gray-900 tracking-tight">
            <span v-if="loading" class="inline-block w-48 h-5 bg-gray-100 rounded animate-pulse" />
            <span v-else>{{ exam?.title }}</span>
          </h2>
          <p class="text-xs text-gray-400">Configurar cotas e professores</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="exam?.status === 'locked'"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 text-xs font-bold rounded-xl">
          <Icon name="lucide:lock" class="w-3 h-3" />Travado
        </span>
        <span v-else-if="exam?.status === 'collecting'"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-amber-50 text-amber-700 text-xs font-bold rounded-xl">
          <Icon name="lucide:pen" class="w-3 h-3" />Em coleta
        </span>
      </div>
    </div>

    <div v-if="loading" class="grid grid-cols-2 gap-4 flex-1">
      <div class="bg-white rounded-2xl border border-gray-100 animate-pulse" />
      <div class="bg-white rounded-2xl border border-gray-100 animate-pulse" />
    </div>

    <div v-else class="grid grid-cols-2 gap-4 flex-1 min-h-0">

      <!-- COLUNA ESQUERDA: Cotas por disciplina -->
      <div class="flex flex-col bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-3.5 border-b border-gray-50 flex-shrink-0">
          <div class="flex items-center gap-2">
            <Icon name="lucide:target" class="w-4 h-4 text-gray-400" />
            <h3 class="text-sm font-bold text-gray-900">Cotas por disciplina</h3>
          </div>
          <div class="flex items-center gap-2">
            <Transition name="fade-msg">
              <span v-if="quotasSuccess" class="text-[11px] font-bold text-emerald-600 flex items-center gap-1">
                <Icon name="lucide:check" class="w-3 h-3" /> Salvo!
              </span>
            </Transition>
            <button
              :disabled="savingQuotas || exam?.status === 'locked'"
              class="flex items-center gap-1.5 text-[11px] font-bold px-3 py-1.5 rounded-lg transition-all"
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

        <!-- Total -->
        <div class="flex items-center justify-between mx-4 mt-3 mb-2 px-4 py-2.5 bg-gray-50 rounded-xl">
          <span class="text-xs font-bold text-gray-500">Total esperado</span>
          <span class="text-xl font-black text-gray-900 tabular-nums">
            {{ Object.values(quotaForm).reduce((a: number, b: number) => a + b, 0) }}
          </span>
        </div>

        <!-- Lista disciplinas com scroll -->
        <div class="flex-1 overflow-y-auto px-4 pb-4 space-y-1.5">
          <div v-for="disc in disciplinasComCota" :key="disc.id"
            class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-gray-800 leading-tight">{{ disc.name }}</p>
              <div class="flex items-center gap-1.5 mt-1">
                <div class="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-300"
                    :class="(quotaMap[disc.id]?.submitted ?? 0) >= quotaForm[disc.id] && quotaForm[disc.id] > 0 ? 'bg-emerald-400' : 'bg-blue-300'"
                    :style="`width:${quotaForm[disc.id] > 0 ? Math.min(100, ((quotaMap[disc.id]?.submitted ?? 0) / quotaForm[disc.id]) * 100) : 0}%`" />
                </div>
                <span class="text-[10px] text-gray-400 tabular-nums flex-shrink-0">
                  {{ quotaMap[disc.id]?.submitted ?? 0 }}/{{ quotaForm[disc.id] ?? 0 }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1 flex-shrink-0">
              <button :disabled="exam?.status === 'locked'"
                class="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center font-black text-gray-500 transition-colors"
                :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-50 hover:border-gray-300'"
                @click="changeQuota(disc.id, -1)">−</button>
              <input :value="quotaForm[disc.id] ?? 0" :disabled="exam?.status === 'locked'"
                type="number" min="0" max="99"
                class="w-12 text-center text-sm font-black text-gray-900 border border-gray-200 rounded-lg py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-200 tabular-nums"
                :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : ''"
                @input="setQuota(disc.id, Number(($event.target as HTMLInputElement).value))" />
              <button :disabled="exam?.status === 'locked'"
                class="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center font-black text-gray-500 transition-colors"
                :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-50 hover:border-gray-300'"
                @click="changeQuota(disc.id, 1)">+</button>
            </div>
          </div>

          <!-- Disciplinas sem cota (colapsadas) -->
          <button v-if="disciplinesSemCota.length"
            class="w-full flex items-center justify-between px-3.5 py-2 text-[11px] font-bold text-gray-400 hover:text-gray-600 transition-colors"
            @click="showAllDiscs = !showAllDiscs">
            <span>+ {{ disciplinesSemCota.length }} disciplina{{ disciplinesSemCota.length > 1 ? 's' : '' }} sem cota</span>
            <Icon :name="showAllDiscs ? 'lucide:chevron-up' : 'lucide:chevron-down'" class="w-3.5 h-3.5" />
          </button>

          <template v-if="showAllDiscs">
            <div v-for="disc in disciplinesSemCota" :key="disc.id"
              class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl border border-dashed border-gray-100 hover:border-gray-200 transition-colors">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-gray-500">{{ disc.name }}</p>
              </div>
              <div class="flex items-center gap-1 flex-shrink-0">
                <button :disabled="exam?.status === 'locked'"
                  class="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center font-black text-gray-400 transition-colors"
                  :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-50'"
                  @click="changeQuota(disc.id, -1)">−</button>
                <input :value="quotaForm[disc.id] ?? 0" :disabled="exam?.status === 'locked'"
                  type="number" min="0" max="99"
                  class="w-12 text-center text-sm font-black text-gray-500 border border-gray-200 rounded-lg py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-200"
                  @input="setQuota(disc.id, Number(($event.target as HTMLInputElement).value))" />
                <button :disabled="exam?.status === 'locked'"
                  class="w-7 h-7 rounded-lg border border-gray-200 flex items-center justify-center font-black text-gray-400 transition-colors"
                  :class="exam?.status === 'locked' ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-50'"
                  @click="changeQuota(disc.id, 1)">+</button>
              </div>
            </div>
          </template>

          <div v-if="quotasError" class="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-100 rounded-xl">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500">{{ quotasError }}</p>
          </div>
        </div>
      </div>

      <!-- COLUNA DIREITA: Professores por turma/disciplina -->
      <div class="flex flex-col bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-3.5 border-b border-gray-50 flex-shrink-0">
          <div class="flex items-center gap-2">
            <Icon name="lucide:user-check" class="w-4 h-4 text-gray-400" />
            <h3 class="text-sm font-bold text-gray-900">Professores por turma</h3>
          </div>
          <Transition name="fade-msg">
            <span v-if="teachersSuccess" class="text-[11px] font-bold text-emerald-600 flex items-center gap-1">
              <Icon name="lucide:check" class="w-3 h-3" /> Vinculado!
            </span>
          </Transition>
        </div>

        <!-- Sem turmas -->
        <div v-if="!assignedClasses.length" class="flex-1 flex flex-col items-center justify-center text-center p-8">
          <div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center mb-3">
            <Icon name="lucide:users" class="w-5 h-5 text-gray-200" />
          </div>
          <p class="text-xs font-bold text-gray-400">Nenhuma turma vinculada</p>
          <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}`"
            class="text-xs font-bold text-blue-500 hover:text-blue-600 mt-2 inline-flex items-center gap-1">
            <Icon name="lucide:arrow-left" class="w-3 h-3" />
            Vincular turmas primeiro
          </NuxtLink>
        </div>

        <!-- Tabs de turmas -->
        <template v-else>
          <div class="flex gap-1 px-4 pt-3 pb-0 overflow-x-auto flex-shrink-0">
            <button v-for="cls in assignedClasses" :key="cls.id"
              class="px-3 py-1.5 rounded-t-lg text-xs font-bold transition-all whitespace-nowrap border-b-2"
              :class="activeClassTab === cls.id
                ? 'bg-gray-900 text-white border-gray-900'
                : 'text-gray-500 hover:text-gray-700 border-transparent hover:bg-gray-50'"
              @click="activeClassTab = cls.id">
              {{ cls.name }}
            </button>
          </div>

          <!-- Conteúdo da turma selecionada -->
          <div class="flex-1 overflow-y-auto p-4 space-y-2">
            <template v-if="activeClassTab">
              <div v-for="disc in disciplinasComCota" :key="disc.id"
                class="p-3 rounded-xl border transition-colors"
                :class="getExistingLink(activeClassTab, disc.id) ? 'border-emerald-200 bg-emerald-50/30' : 'border-gray-100 hover:border-gray-200'">

                <div class="flex items-center justify-between mb-2">
                  <p class="text-xs font-bold text-gray-800">{{ disc.name }}</p>
                  <span v-if="getExistingLink(activeClassTab, disc.id)"
                    class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 flex items-center gap-1">
                    <Icon name="lucide:check" class="w-2.5 h-2.5" />
                    {{ teacherName(getExistingLink(activeClassTab, disc.id)!.teacher_user_id) }}
                  </span>
                </div>

                <div class="flex items-center gap-2">
                  <select v-model="teacherForm[`${activeClassTab}_${disc.id}`]"
                    class="flex-1 text-xs border border-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-700">
                    <option value="">— selecionar professor —</option>
                    <option v-for="t in teachersByDisc(disc.id)" :key="t.id" :value="t.id">{{ t.name }}</option>
                  </select>
                  <button
                    :disabled="!teacherForm[`${activeClassTab}_${disc.id}`] || savingTeacher[`${activeClassTab}_${disc.id}`]"
                    class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-[11px] font-bold transition-all"
                    :class="!teacherForm[`${activeClassTab}_${disc.id}`]
                      ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                      : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
                    @click="saveTeacherLink(activeClassTab, disc.id)">
                    <svg v-if="savingTeacher[`${activeClassTab}_${disc.id}`]" class="animate-spin w-3 h-3" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                    </svg>
                    <Icon v-else name="lucide:link" class="w-3 h-3" />
                    Vincular
                  </button>
                  <button v-if="getExistingLink(activeClassTab, disc.id)"
                    class="w-7 h-7 rounded-lg hover:bg-red-50 flex items-center justify-center transition-colors"
                    @click="removeTeacherLink(getExistingLink(activeClassTab, disc.id)!.id)">
                    <Icon name="lucide:x" class="w-3 h-3 text-gray-300 hover:text-red-400" />
                  </button>
                </div>
              </div>

              <p v-if="disciplinasComCota.length === 0" class="text-xs text-gray-400 text-center py-6">
                Configure cotas na coluna esquerda primeiro
              </p>
            </template>
          </div>

          <div v-if="teachersError" class="mx-4 mb-3 flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-100 rounded-xl">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500">{{ teachersError }}</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const { get, post, delete: del } = useApi()
const examId = computed(() => Number(route.params.id))

const exam            = ref<any>(null)
const disciplines     = ref<any[]>([])
const allClasses      = ref<any[]>([])
const assignedClasses = ref<any[]>([])
const teachers        = ref<any[]>([])
const teacherSubjects = ref<any[]>([])
const loading         = ref(true)
const showAllDiscs    = ref(false)
const activeClassTab  = ref<number | null>(null)

// Cotas
const quotaForm      = reactive<Record<number, number>>({})
const quotaMap       = ref<Record<number, any>>({})
const savingQuotas   = ref(false)
const quotasError    = ref('')
const quotasSuccess  = ref(false)

// Professores
const teacherForm     = reactive<Record<string, number | ''>>({})
const savingTeacher   = reactive<Record<string, boolean>>({})
const teachersError   = ref('')
const teachersSuccess = ref(false)

// Disciplinas separadas por cota
const disciplinasComCota = computed(() =>
  disciplines.value.filter(d => (quotaForm[d.id] ?? 0) > 0)
)
const disciplinesSemCota = computed(() =>
  disciplines.value.filter(d => !(quotaForm[d.id] ?? 0))
)

// Filtra professores que têm vínculo com a disciplina selecionada
function teachersByDisc(discId: number) {
  const ids = new Set(teacherSubjects.value
    .filter(ts => ts.discipline_id === discId)
    .map(ts => ts.teacher_user_id))
  // Se não há vínculos cadastrados, mostra todos
  return ids.size ? teachers.value.filter(t => ids.has(t.id)) : teachers.value
}

function changeQuota(discId: number, delta: number) {
  quotaForm[discId] = Math.max(0, (quotaForm[discId] ?? 0) + delta)
}
function setQuota(discId: number, val: number) {
  quotaForm[discId] = Math.max(0, isNaN(val) ? 0 : val)
}
function teacherName(id: number) {
  const t = teachers.value.find(t => t.id === id)
  return t ? t.name.split(' ')[0] : `#${id}`
}
function getExistingLink(classId: number, discId: number) {
  return teacherSubjects.value.find(ts => ts.class_id === classId && ts.discipline_id === discId) ?? null
}

async function saveQuotas() {
  savingQuotas.value = true; quotasError.value = ''; quotasSuccess.value = false
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
  savingTeacher[key] = true; teachersError.value = ''
  try {
    const existing = getExistingLink(classId, discId)
    if (existing) {
      await del(`/school/teacher-subjects/${existing.id}`)
      teacherSubjects.value = teacherSubjects.value.filter(ts => ts.id !== existing.id)
    }
    const created = await post<any>('/school/teacher-subjects', {
      teacher_user_id: Number(teacherId), class_id: classId, discipline_id: discId,
    })
    teacherSubjects.value.push(created)
    await post(`/exams/${examId.value}/assign-teachers`, {
      items: [{ class_id: classId, discipline_id: discId, teacher_user_id: Number(teacherId) }]
    }).catch(() => {})
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
    teachersError.value = e.message ?? 'Erro ao remover.'
  }
}

onMounted(async () => {
  const [eR, dR, pR, ecR, acR, tR, sR] = await Promise.allSettled([
    get<any>(`/exams/${examId.value}`),
    get<any[]>('/disciplines/'),
    get<any>(`/exams/${examId.value}/progress`),
    get<any[]>(`/exams/${examId.value}/classes`),
    get<any[]>('/school/classes'),
    get<any[]>('/school/teachers'),
    get<any[]>('/school/teacher-subjects'),
  ])
  if (eR.status === 'fulfilled')  exam.value            = eR.value
  if (dR.status === 'fulfilled')  disciplines.value     = dR.value
  if (acR.status === 'fulfilled') allClasses.value      = acR.value
  if (tR.status === 'fulfilled')  teachers.value        = tR.value
  if (sR.status === 'fulfilled')  teacherSubjects.value = sR.value

  if (pR.status === 'fulfilled' && pR.value?.disciplines) {
    for (const d of pR.value.disciplines) {
      quotaForm[d.discipline_id] = d.quota
      quotaMap.value[d.discipline_id] = d
    }
  }
  if (dR.status === 'fulfilled') {
    for (const d of dR.value) {
      if (quotaForm[d.id] === undefined) quotaForm[d.id] = 0
    }
  }
  if (ecR.status === 'fulfilled' && acR.status === 'fulfilled') {
    const ids = new Set(ecR.value.map((c: any) => c.class_id))
    assignedClasses.value = allClasses.value.filter(c => ids.has(c.id))
    if (assignedClasses.value.length) activeClassTab.value = assignedClasses.value[0].id
  }
  loading.value = false
})
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(4px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-in { animation: fade-in 0.25s ease both }
.fade-msg-enter-active, .fade-msg-leave-active { transition: opacity 0.3s ease }
.fade-msg-enter-from, .fade-msg-leave-to { opacity: 0 }
</style>
