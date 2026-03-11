<!-- pages/dashboard/coordenador/turmas/[id].vue -->
<template>
  <div class="space-y-5">

    <!-- Voltar -->
    <div class="animate-fade-in">
      <NuxtLink to="/dashboard/coordenador/turmas"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-gray-400 hover:text-gray-700 transition-colors mb-4">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" />
        Todas as turmas
      </NuxtLink>

      <!-- Header skeleton -->
      <div v-if="loading" class="h-16 bg-white rounded-2xl border border-gray-100 animate-pulse" />

      <!-- Header -->
      <div v-else class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-black text-lg shadow-sm"
            :class="corBg">
            {{ turma?.name }}
          </div>
          <div>
            <h2 class="text-2xl font-black text-gray-900 tracking-tight">{{ turma?.name }}</h2>
            <p class="text-sm text-gray-400 mt-0.5">
              {{ turma?.grade?.level === 'fundamental' ? 'Ensino Fundamental' : 'Ensino Médio' }} · Turma #{{ turma?.id }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            class="flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-700 text-white text-sm font-bold rounded-xl transition-all hover:scale-[1.02] active:scale-95"
            @click="showAlunoModal = true">
            <Icon name="lucide:user-plus" class="w-4 h-4" />
            <span class="hidden sm:inline">Adicionar aluno</span>
          </button>
          <button
            class="flex items-center gap-2 px-4 py-2.5 border border-red-200 hover:bg-red-50 text-red-500 text-sm font-bold rounded-xl transition-all active:scale-95"
            @click="showDeleteModal = true">
            <Icon name="lucide:trash-2" class="w-4 h-4" />
            <span class="hidden sm:inline">Excluir</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-3 animate-fade-up" style="animation-delay:60ms">
      <div v-for="s in statCards" :key="s.label"
        class="bg-white rounded-2xl border border-gray-100 p-4 flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" :class="s.iconBg">
          <Icon :name="s.icon" class="w-4 h-4" :class="s.iconColor" />
        </div>
        <div>
          <p class="text-xl font-black text-gray-900 tabular-nums leading-none">
            <span v-if="loading" class="inline-block w-6 h-5 bg-gray-100 rounded animate-pulse" />
            <span v-else>{{ s.value }}</span>
          </p>
          <p class="text-[11px] text-gray-400 font-medium mt-0.5">{{ s.label }}</p>
        </div>
      </div>
    </div>

    <!-- Alunos + Simulados -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">

      <!-- Alunos -->
      <div class="lg:col-span-3 bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:100ms">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <Icon name="lucide:graduation-cap" class="w-4 h-4 text-gray-400" />
            <h3 class="text-sm font-bold text-gray-900">Alunos</h3>
            <span class="text-[11px] font-bold px-1.5 py-0.5 rounded-md bg-gray-50 text-gray-500">{{ students.length }}</span>
          </div>
          <div class="relative">
            <Icon name="lucide:search" class="w-3 h-3 text-gray-300 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input v-model="busca"
              class="pl-7 pr-3 py-1.5 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all w-36"
              placeholder="Nome ou RA..." />
          </div>
        </div>

        <div v-if="loadingStudents" class="p-4 space-y-2">
          <div v-for="i in 5" :key="i" class="h-11 bg-gray-50 rounded-xl animate-pulse" :style="`animation-delay:${i*60}ms`" />
        </div>

        <div v-else-if="alunosFiltrados.length === 0"
          class="flex flex-col items-center justify-center py-14">
          <Icon name="lucide:users" class="w-8 h-8 text-gray-200 mb-2" />
          <p class="text-xs text-gray-400 font-medium">
            {{ busca ? 'Nenhum resultado' : 'Nenhum aluno cadastrado' }}
          </p>
        </div>

        <div v-else class="divide-y divide-gray-50 max-h-[480px] overflow-y-auto">
          <div
            v-for="(aluno, i) in alunosFiltrados" :key="aluno.id"
            class="flex items-center gap-3 px-5 py-3 hover:bg-gray-50/60 transition-colors group animate-fade-up"
            :style="`animation-delay:${i*25}ms`">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-black text-white flex-shrink-0"
              :class="corBg">
              {{ aluno.name[0] }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate">{{ aluno.name }}</p>
              <p class="text-[11px] text-gray-400 font-mono">RA: {{ aluno.ra }}</p>
            </div>
            <button
              class="opacity-0 group-hover:opacity-100 w-7 h-7 rounded-lg hover:bg-red-50 flex items-center justify-center transition-all"
              @click="deleteAluno(aluno.id)">
              <Icon name="lucide:trash-2" class="w-3.5 h-3.5 text-red-400" />
            </button>
          </div>
        </div>
      </div>

      <!-- Simulados -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:140ms">
        <div class="flex items-center gap-2 px-5 py-4 border-b border-gray-50">
          <Icon name="lucide:file-text" class="w-4 h-4 text-gray-400" />
          <h3 class="text-sm font-bold text-gray-900">Simulados</h3>
          <span class="text-[11px] font-bold px-1.5 py-0.5 rounded-md bg-gray-50 text-gray-500">{{ exams.length }}</span>
        </div>

        <div v-if="loadingExams" class="p-4 space-y-2">
          <div v-for="i in 3" :key="i" class="h-14 bg-gray-50 rounded-xl animate-pulse" />
        </div>

        <div v-else-if="exams.length === 0"
          class="flex flex-col items-center justify-center py-14 px-4 text-center">
          <Icon name="lucide:file-x" class="w-8 h-8 text-gray-200 mb-2" />
          <p class="text-xs text-gray-400 font-medium">Nenhum simulado vinculado</p>
        </div>

        <div v-else class="divide-y divide-gray-50">
          <NuxtLink
            v-for="exam in exams" :key="exam.id"
            :to="`/dashboard/coordenador/simulados/${exam.id}`"
            class="flex items-center gap-3 px-5 py-3.5 hover:bg-gray-50/60 transition-colors group">
            <div class="w-2 h-2 rounded-full flex-shrink-0" :class="statusDot(exam.status)" />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate group-hover:text-blue-600 transition-colors">{{ exam.title }}</p>
              <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full" :class="statusBadge(exam.status)">
                {{ statusLabel(exam.status) }}
              </span>
            </div>
            <Icon name="lucide:chevron-right" class="w-3.5 h-3.5 text-gray-200 group-hover:text-blue-400 flex-shrink-0 transition-colors" />
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Modal adicionar aluno -->
    <Transition name="modal">
      <div v-if="showAlunoModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showAlunoModal = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-modal-in">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="text-base font-black text-gray-900">Adicionar aluno</h3>
              <p class="text-xs text-gray-400 mt-0.5">Turma {{ turma?.name }}</p>
            </div>
            <button class="w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center transition-colors"
              @click="showAlunoModal = false">
              <Icon name="lucide:x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>
          <div class="space-y-3">
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Nome completo</label>
              <input v-model="alunoForm.name" placeholder="Ex: Maria Silva"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all" />
            </div>
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">RA</label>
              <input v-model="alunoForm.ra" placeholder="Registro do Aluno"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all" />
            </div>
            <div v-if="alunoError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
              <p class="text-xs text-red-500 font-medium">{{ alunoError }}</p>
            </div>
            <button
              :disabled="!alunoForm.name || !alunoForm.ra || savingAluno"
              class="w-full py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="!alunoForm.name || !alunoForm.ra || savingAluno
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
              @click="createAluno">
              <svg v-if="savingAluno" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ savingAluno ? 'Salvando...' : 'Adicionar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal excluir turma -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showDeleteModal = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-modal-in">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:trash-2" class="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h3 class="text-base font-black text-gray-900">Excluir turma</h3>
              <p class="text-xs text-gray-400 mt-0.5">Esta ação não pode ser desfeita</p>
            </div>
          </div>

          <p class="text-sm text-gray-600 mb-5">
            Tem certeza que deseja excluir a turma
            <span class="font-black text-gray-900">{{ turma?.name }}</span>?
            Os {{ students.length }} aluno{{ students.length !== 1 ? 's' : '' }} serão desvinculados.
          </p>

          <div v-if="deleteError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl mb-4">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-500 font-medium">{{ deleteError }}</p>
          </div>

          <div class="flex gap-2">
            <button
              class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600 transition-all"
              @click="showDeleteModal = false">
              Cancelar
            </button>
            <button
              :disabled="deleting"
              class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="deleting
                ? 'bg-red-200 text-red-300 cursor-not-allowed'
                : 'bg-red-500 hover:bg-red-600 text-white active:scale-95'"
              @click="deleteClass">
              <svg v-if="deleting" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ deleting ? 'Excluindo...' : 'Sim, excluir' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const { get, post, delete: del } = useApi()

const classId = computed(() => Number(route.params.id))

const turma           = ref<any>(null)
const students        = ref<any[]>([])
const exams           = ref<any[]>([])
const loading         = ref(true)
const loadingStudents = ref(true)
const loadingExams    = ref(true)
const busca           = ref('')

const showAlunoModal = ref(false)
const savingAluno    = ref(false)
const alunoError     = ref('')
const alunoForm      = reactive({ name: '', ra: '' })

const showDeleteModal = ref(false)
const deleting        = ref(false)
const deleteError     = ref('')

const coresMedio = ['bg-blue-500', 'bg-violet-500', 'bg-indigo-500', 'bg-sky-500', 'bg-purple-500']
const coresFund  = ['bg-emerald-500', 'bg-teal-500', 'bg-green-500', 'bg-cyan-500', 'bg-lime-600']

const corBg = computed(() => {
  const isFund = turma.value?.grade?.level === 'fundamental'
  const palette = isFund ? coresFund : coresMedio
  return palette[classId.value % palette.length]
})

const statCards = computed(() => [
  { label: 'Alunos',    value: students.value.length, icon: 'lucide:graduation-cap', iconBg: 'bg-blue-50',   iconColor: 'text-blue-500'   },
  { label: 'Simulados', value: exams.value.length,    icon: 'lucide:file-text',      iconBg: 'bg-violet-50', iconColor: 'text-violet-500' },
  { label: 'Turma ID',  value: `#${classId.value}`,  icon: 'lucide:hash',           iconBg: 'bg-gray-50',   iconColor: 'text-gray-400'   },
])

const alunosFiltrados = computed(() => {
  const q = busca.value.toLowerCase()
  if (!q) return students.value
  return students.value.filter(a =>
    a.name.toLowerCase().includes(q) || a.ra.includes(q)
  )
})

function statusLabel(s: string) {
  return ({ collecting: 'Em coleta', locked: 'Travado', published: 'Publicado', draft: 'Rascunho' } as any)[s] ?? s
}
function statusBadge(s: string) {
  return ({ collecting: 'bg-amber-50 text-amber-700', locked: 'bg-blue-50 text-blue-700', published: 'bg-emerald-50 text-emerald-700' } as any)[s] ?? 'bg-gray-50 text-gray-500'
}
function statusDot(s: string) {
  return ({ collecting: 'bg-amber-400', locked: 'bg-blue-400', published: 'bg-emerald-400' } as any)[s] ?? 'bg-gray-300'
}

async function createAluno() {
  if (!alunoForm.name || !alunoForm.ra) return
  savingAluno.value = true
  alunoError.value = ''
  try {
    const created = await post<any>('/school/students/', {
      name: alunoForm.name,
      ra: alunoForm.ra,
      class_id: classId.value,
    })
    students.value.push(created)
    alunoForm.name = ''
    alunoForm.ra = ''
    showAlunoModal.value = false
  } catch (e: any) {
    alunoError.value = e.message ?? 'Erro ao adicionar aluno.'
  } finally {
    savingAluno.value = false
  }
}

async function deleteAluno(id: number) {
  if (!confirm('Remover este aluno da turma?')) return
  try {
    await del(`/school/students/${id}`)
    students.value = students.value.filter(a => a.id !== id)
  } catch (e: any) {
    alert(e.message ?? 'Erro ao remover aluno.')
  }
}

async function deleteClass() {
  deleting.value = true
  deleteError.value = ''
  try {
    await del(`/school/classes/${classId.value}`)
    navigateTo('/dashboard/coordenador/turmas')
  } catch (e: any) {
    deleteError.value = e.message ?? 'Erro ao excluir turma.'
    deleting.value = false
  }
}

onMounted(async () => {
  const [classList, studentList, examList] = await Promise.allSettled([
    get<any[]>('/school/classes'),
    get<any[]>(`/school/students/?class_id=${classId.value}`),
    get<any[]>('/exams/'),
  ])

  if (classList.status === 'fulfilled') {
    turma.value = classList.value.find((c: any) => c.id === classId.value) ?? null
  }
  loading.value = false

  if (studentList.status === 'fulfilled') students.value = studentList.value
  loadingStudents.value = false

  if (examList.status === 'fulfilled') {
    const all = examList.value
    const filtered = all.filter((e: any) =>
      e.class_ids?.includes(classId.value) || e.classes?.includes(classId.value)
    )
    exams.value = filtered
  }
  loadingExams.value = false
})
</script>

<style scoped>
@keyframes fade-in  { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up  { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
@keyframes modal-in { from { opacity:0; transform:scale(0.94) translateY(10px) } to { opacity:1; transform:scale(1) translateY(0) } }

.animate-fade-in  { animation: fade-in  0.3s ease both }
.animate-fade-up  { animation: fade-up  0.38s ease both }
.animate-modal-in { animation: modal-in 0.22s cubic-bezier(0.34,1.56,0.64,1) both }

.modal-enter-active, .modal-leave-active { transition: opacity 0.18s ease }
.modal-enter-from, .modal-leave-to { opacity: 0 }
</style>