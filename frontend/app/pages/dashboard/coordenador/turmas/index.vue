<!-- pages/dashboard/coordenador/turmas.vue -->
<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between animate-fade-in">
      <div>
        <h2 class="text-xl font-black text-gray-900 tracking-tight">Turmas</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ classes.length }} turma{{ classes.length !== 1 ? 's' : '' }} cadastrada{{ classes.length !== 1 ? 's' : '' }}</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="flex items-center gap-2 px-4 py-2.5 border border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-bold rounded-xl transition-all duration-200"
          @click="showImportModal = true">
          <Icon name="lucide:upload" class="w-4 h-4" />
          <span class="hidden sm:inline">Importar CSV</span>
        </button>
        <button
          class="flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-700 text-white text-sm font-bold rounded-xl transition-all duration-200 hover:scale-[1.02] active:scale-95"
          @click="showModal = true">
          <Icon name="lucide:plus" class="w-4 h-4" />
          Nova turma
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-6">
      <div v-for="nivel in 2" :key="nivel">
        <div class="h-4 w-32 bg-gray-100 rounded animate-pulse mb-3" />
        <div class="grid gap-3 sm:grid-cols-3 lg:grid-cols-5">
          <div v-for="i in 5" :key="i" class="h-28 bg-white rounded-2xl border border-gray-100 animate-pulse" :style="`animation-delay:${i*40}ms`" />
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="classes.length === 0"
      class="flex flex-col items-center justify-center py-28 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-in">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:users" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">Nenhuma turma cadastrada</p>
      <p class="text-xs text-gray-300 mt-1">Crie uma turma ou importe via CSV</p>
    </div>

    <!-- Agrupado por nível -->
    <div v-else class="space-y-7">

      <!-- Ensino Médio -->
      <div v-if="classesPorNivel.medio.length" class="animate-fade-up" style="animation-delay:60ms">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-4 rounded-full bg-blue-500" />
            <span class="text-[11px] font-black text-gray-500 uppercase tracking-widest">Ensino Médio</span>
          </div>
          <div class="flex-1 h-px bg-gray-100" />
          <span class="text-[11px] font-semibold text-gray-300">{{ classesPorNivel.medio.length }} turmas</span>
        </div>
        <div class="grid gap-2.5 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          <NuxtLink
            v-for="(cls, idx) in classesPorNivel.medio" :key="cls.id"
            :to="`/dashboard/coordenador/turmas/${cls.id}`"
            class="group bg-white rounded-2xl border border-gray-100 p-4 flex flex-col gap-3 hover:border-blue-200 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 animate-fade-up"
            :style="`animation-delay:${80 + idx*30}ms`">
            <div class="flex items-center justify-between">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm flex-shrink-0 shadow-sm"
                :class="coresMedio[idx % coresMedio.length]">
                {{ cls.name }}
              </div>
              <Icon name="lucide:arrow-right" class="w-3.5 h-3.5 text-gray-200 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
            </div>
            <div>
              <p class="text-sm font-black text-gray-900 group-hover:text-blue-600 transition-colors leading-none">{{ cls.name }}</p>
              <p class="text-[10px] text-gray-400 mt-0.5">Ensino Médio</p>
            </div>
            <div class="h-px bg-gray-50" />
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1">
                <Icon name="lucide:graduation-cap" class="w-3 h-3 text-gray-300" />
                <span class="text-xs font-black text-gray-700 tabular-nums">
                  <span v-if="loadingStudents[cls.id]" class="inline-block w-4 h-3 bg-gray-100 rounded animate-pulse" />
                  <span v-else>{{ students[cls.id]?.length ?? 0 }}</span>
                </span>
              </div>
              <div class="flex items-center gap-1">
                <Icon name="lucide:file-text" class="w-3 h-3 text-gray-300" />
                <span class="text-xs font-black text-gray-700 tabular-nums">{{ examsDaTurma(cls.id) }}</span>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- Ensino Fundamental -->
      <div v-if="classesPorNivel.fundamental.length" class="animate-fade-up" style="animation-delay:120ms">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-4 rounded-full bg-emerald-500" />
            <span class="text-[11px] font-black text-gray-500 uppercase tracking-widest">Ensino Fundamental</span>
          </div>
          <div class="flex-1 h-px bg-gray-100" />
          <span class="text-[11px] font-semibold text-gray-300">{{ classesPorNivel.fundamental.length }} turmas</span>
        </div>
        <div class="grid gap-2.5 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          <NuxtLink
            v-for="(cls, idx) in classesPorNivel.fundamental" :key="cls.id"
            :to="`/dashboard/coordenador/turmas/${cls.id}`"
            class="group bg-white rounded-2xl border border-gray-100 p-4 flex flex-col gap-3 hover:border-emerald-200 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 animate-fade-up"
            :style="`animation-delay:${140 + idx*30}ms`">
            <div class="flex items-center justify-between">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm flex-shrink-0 shadow-sm"
                :class="coresFund[idx % coresFund.length]">
                {{ cls.name }}
              </div>
              <Icon name="lucide:arrow-right" class="w-3.5 h-3.5 text-gray-200 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
            </div>
            <div>
              <p class="text-sm font-black text-gray-900 group-hover:text-emerald-600 transition-colors leading-none">{{ cls.name }}</p>
              <p class="text-[10px] text-gray-400 mt-0.5">Ens. Fundamental</p>
            </div>
            <div class="h-px bg-gray-50" />
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1">
                <Icon name="lucide:graduation-cap" class="w-3 h-3 text-gray-300" />
                <span class="text-xs font-black text-gray-700 tabular-nums">
                  <span v-if="loadingStudents[cls.id]" class="inline-block w-4 h-3 bg-gray-100 rounded animate-pulse" />
                  <span v-else>{{ students[cls.id]?.length ?? 0 }}</span>
                </span>
              </div>
              <div class="flex items-center gap-1">
                <Icon name="lucide:file-text" class="w-3 h-3 text-gray-300" />
                <span class="text-xs font-black text-gray-700 tabular-nums">{{ examsDaTurma(cls.id) }}</span>
              </div>
            </div>
          </NuxtLink>
        </div>
      </div>

    </div>

    <!-- ── Modal nova turma ── -->
    <Transition name="modal">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="closeModal" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-modal-in">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="text-base font-black text-gray-900">Nova turma</h3>
              <p class="text-xs text-gray-400 mt-0.5">Selecione nível, série/ano e seção</p>
            </div>
            <button class="w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center transition-colors" @click="closeModal">
              <Icon name="lucide:x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <div class="space-y-4">

            <!-- Nível -->
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Nível</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="n in niveis" :key="n.value"
                  class="py-2.5 rounded-xl text-sm font-bold border-2 transition-all duration-150"
                  :class="novoForm.nivel === n.value
                    ? 'border-gray-900 bg-gray-900 text-white'
                    : 'border-gray-100 bg-gray-50 text-gray-500 hover:border-gray-300'"
                  @click="selectNivel(n.value)">
                  {{ n.label }}
                </button>
              </div>
            </div>

            <!-- Série / Ano -->
            <Transition name="slide-down" mode="out-in">
              <div v-if="novoForm.nivel" :key="novoForm.nivel">
                <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">
                  {{ novoForm.nivel === 'medio' ? 'Série' : 'Ano' }}
                </label>
                <div class="grid gap-2" :class="gradesFiltradas.length <= 4 ? 'grid-cols-4' : 'grid-cols-5'">
                  <button
                    v-for="g in gradesFiltradas" :key="g.id"
                    class="py-2 rounded-xl text-sm font-bold border-2 transition-all duration-150 text-center"
                    :class="novoForm.grade_id === g.id
                      ? 'border-gray-900 bg-gray-900 text-white'
                      : 'border-gray-100 bg-gray-50 text-gray-600 hover:border-gray-300'"
                    @click="novoForm.grade_id = g.id; novoForm.section_id = null">
                    {{ g.label }}
                  </button>
                </div>
              </div>
            </Transition>

            <!-- Seção -->
            <Transition name="slide-down" mode="out-in">
              <div v-if="novoForm.grade_id" key="section">
                <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Seção</label>
                <div class="flex gap-2">
                  <button
                    v-for="s in sections" :key="s.id"
                    class="w-10 h-10 rounded-xl text-sm font-black border-2 transition-all duration-150"
                    :class="novoForm.section_id === s.id
                      ? 'border-gray-900 bg-gray-900 text-white'
                      : 'border-gray-100 bg-gray-50 text-gray-600 hover:border-gray-300'"
                    @click="novoForm.section_id = s.id">
                    {{ s.label }}
                  </button>
                </div>
              </div>
            </Transition>

            <!-- Preview -->
            <Transition name="slide-down">
              <div v-if="previewNome"
                class="flex items-center gap-3 px-3 py-2.5 bg-gray-50 rounded-xl border border-gray-100">
                <div class="w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-black flex-shrink-0"
                  :class="novoForm.nivel === 'medio' ? 'bg-blue-500' : 'bg-emerald-500'">
                  {{ previewNome }}
                </div>
                <div>
                  <p class="text-sm font-black text-gray-900">{{ previewNome }}</p>
                  <p class="text-[11px] text-gray-400">{{ novoForm.nivel === 'medio' ? 'Ensino Médio' : 'Ensino Fundamental' }}</p>
                </div>
              </div>
            </Transition>

            <!-- Erro -->
            <div v-if="modalError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
              <p class="text-xs text-red-500 font-medium">{{ modalError }}</p>
            </div>

            <button
              :disabled="!novoForm.grade_id || !novoForm.section_id || saving"
              class="w-full py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="!novoForm.grade_id || !novoForm.section_id || saving
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
              @click="createClass">
              <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ saving ? 'Criando...' : 'Criar turma' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── Modal importar CSV ── -->
    <Transition name="modal">
      <div v-if="showImportModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="closeImport" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-modal-in">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="text-base font-black text-gray-900">Importar alunos via CSV</h3>
              <p class="text-xs text-gray-400 mt-0.5">Arquivo no padrão SEDUC-SP</p>
            </div>
            <button class="w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center transition-colors" @click="closeImport">
              <Icon name="lucide:x" class="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Turma de destino</label>
              <select v-model="importForm.class_id"
                class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all bg-white appearance-none">
                <option value="" disabled>Selecione a turma...</option>
                <optgroup v-if="classesPorNivel.medio.length" label="Ensino Médio">
                  <option v-for="cls in classesPorNivel.medio" :key="cls.id" :value="cls.id">{{ cls.name }}</option>
                </optgroup>
                <optgroup v-if="classesPorNivel.fundamental.length" label="Ensino Fundamental">
                  <option v-for="cls in classesPorNivel.fundamental" :key="cls.id" :value="cls.id">{{ cls.name }}</option>
                </optgroup>
              </select>
            </div>

            <!-- Drop zone -->
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1.5">Arquivo CSV</label>
              <div
                class="relative border-2 border-dashed rounded-2xl p-6 text-center transition-all duration-200 cursor-pointer"
                :class="csvFile ? 'border-emerald-300 bg-emerald-50' : isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
                @dragover.prevent="isDragging = true"
                @dragleave="isDragging = false"
                @drop.prevent="onDrop"
                @click="(csvInput as HTMLInputElement)?.click()">
                <input ref="csvInput" type="file" accept=".csv" class="hidden" @change="onFileChange" />
                <Transition name="fade-swap" mode="out-in">
                  <div v-if="csvFile" key="file" class="flex items-center justify-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center">
                      <Icon name="lucide:file-check" class="w-4 h-4 text-emerald-600" />
                    </div>
                    <div class="text-left">
                      <p class="text-sm font-bold text-emerald-700">{{ csvFile.name }}</p>
                      <p class="text-xs text-emerald-500">{{ (csvFile.size / 1024).toFixed(1) }} KB</p>
                    </div>
                    <button class="w-6 h-6 rounded-lg hover:bg-emerald-200 flex items-center justify-center ml-1 transition-colors"
                      @click.stop="csvFile = null">
                      <Icon name="lucide:x" class="w-3 h-3 text-emerald-600" />
                    </button>
                  </div>
                  <div v-else key="empty">
                    <Icon name="lucide:upload-cloud" class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <p class="text-sm font-semibold text-gray-500">Arraste o CSV aqui</p>
                    <p class="text-xs text-gray-400 mt-0.5">ou clique para selecionar</p>
                  </div>
                </Transition>
              </div>
            </div>

            <!-- Formato -->
            <div class="px-3 py-2.5 bg-gray-50 rounded-xl border border-gray-100">
              <p class="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">Formato esperado (SEDUC-SP)</p>
              <p class="text-[11px] text-gray-500 mb-1">Separador <code class="bg-gray-200 px-1 rounded">;</code> · apenas alunos <strong>Ativos</strong></p>
              <code class="text-[10px] text-gray-400 font-mono">Nº de chamada;Nome do Aluno;RA;Dig. RA;...;Situação do Aluno</code>
            </div>

            <!-- Resultado -->
            <div v-if="importResult"
              class="flex items-start gap-2.5 px-3 py-2.5 rounded-xl border"
              :class="importResult.error ? 'bg-red-50 border-red-100' : 'bg-emerald-50 border-emerald-100'">
              <Icon :name="importResult.error ? 'lucide:circle-x' : 'lucide:check-circle-2'"
                class="w-4 h-4 flex-shrink-0 mt-0.5"
                :class="importResult.error ? 'text-red-400' : 'text-emerald-500'" />
              <p class="text-xs font-medium" :class="importResult.error ? 'text-red-600' : 'text-emerald-700'">
                {{ importResult.message }}
              </p>
            </div>

            <button
              :disabled="!importForm.class_id || !csvFile || importing"
              class="w-full py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="!importForm.class_id || !csvFile || importing
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
              @click="importCsv">
              <svg v-if="importing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              <Icon v-else name="lucide:upload" class="w-4 h-4" />
              {{ importing ? 'Importando...' : 'Importar alunos' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get, post, upload } = useApi()

const classes  = ref<any[]>([])
const grades   = ref<any[]>([])
const sections = ref<any[]>([])
const exams    = ref<any[]>([])
const students        = ref<Record<number, any[]>>({})
const loadingStudents = ref<Record<number, boolean>>({})
const loading  = ref(true)

// Modal nova turma
const showModal  = ref(false)
const saving     = ref(false)
const modalError = ref('')
const novoForm   = reactive({ nivel: '' as 'medio' | 'fundamental' | '', grade_id: null as any, section_id: null as any })

// Modal importar CSV
const showImportModal = ref(false)
const importing       = ref(false)
const isDragging      = ref(false)
const csvFile         = ref<File | null>(null)
const importResult    = ref<{ error: boolean; message: string } | null>(null)
const importForm      = reactive({ class_id: '' as any })
const csvInput        = ref<HTMLInputElement>()

const niveis = [
  { value: 'medio',       label: 'Ensino Médio' },
  { value: 'fundamental', label: 'Fundamental' },
]

const coresMedio = ['bg-blue-500', 'bg-violet-500', 'bg-indigo-500', 'bg-sky-500', 'bg-purple-500']
const coresFund  = ['bg-emerald-500', 'bg-teal-500', 'bg-green-500', 'bg-cyan-500', 'bg-lime-600']

// Agrupa turmas por nível — usa o campo grade.level se disponível, senão deduz pelo nome
const classesPorNivel = computed(() => {
  const medio: any[]       = []
  const fundamental: any[] = []
  for (const cls of classes.value) {
    const level = cls.grade?.level ?? cls.level
    if (level === 'fundamental') fundamental.push(cls)
    else medio.push(cls)
  }
  // Ordena: médio por série (1ª→3ª) e seção; fundamental por ano (6º→9º) e seção
  medio.sort((a, b) => a.name.localeCompare(b.name))
  fundamental.sort((a, b) => a.name.localeCompare(b.name))
  return { medio, fundamental }
})

const gradesFiltradas = computed(() =>
  grades.value
    .filter(g => g.level === novoForm.nivel)
    .sort((a, b) => a.year_number - b.year_number)
)

const previewNome = computed(() => {
  if (!novoForm.grade_id || !novoForm.section_id) return ''
  const g = grades.value.find(g => g.id === novoForm.grade_id)
  const s = sections.value.find(s => s.id === novoForm.section_id)
  if (!g || !s) return ''
  return `${g.label}${s.label}`
})

function selectNivel(nivel: string) {
  novoForm.nivel = nivel as any
  novoForm.grade_id = null
  novoForm.section_id = null
}

function examsDaTurma(classId: number) {
  return exams.value.filter(e => e.class_ids?.includes(classId) || e.classes?.includes(classId)).length
}

function closeModal() {
  showModal.value = false
  novoForm.nivel = ''
  novoForm.grade_id = null
  novoForm.section_id = null
  modalError.value = ''
}

function closeImport() {
  showImportModal.value = false
  csvFile.value = null
  importResult.value = null
  importForm.class_id = ''
  isDragging.value = false
}

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) { csvFile.value = file; importResult.value = null }
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file?.name.endsWith('.csv')) { csvFile.value = file; importResult.value = null }
}

async function createClass() {
  if (!novoForm.grade_id || !novoForm.section_id) return
  saving.value = true
  modalError.value = ''
  try {
    const created = await post<any>('/school/classes', {
      grade_id:   novoForm.grade_id,
      section_id: novoForm.section_id,
    })
    classes.value.push(created)
    closeModal()
  } catch (e: any) {
    modalError.value = e.message ?? 'Erro ao criar turma.'
  } finally {
    saving.value = false
  }
}

async function importCsv() {
  if (!csvFile.value || !importForm.class_id) return
  importing.value = true
  importResult.value = null
  try {
    const fd = new FormData()
    fd.append('file', csvFile.value)
    const res = await upload<any>(
      `/school/students/import?class_id=${importForm.class_id}&dry_run=false`,
      fd
    )
    importResult.value = {
      error: false,
      message: `${res.created} criado(s), ${res.updated} atualizado(s), ${res.skipped_inactive} inativos ignorados.`,
    }
    const updated = await get<any[]>(`/school/students/?class_id=${importForm.class_id}`)
    students.value[importForm.class_id] = updated
    csvFile.value = null
  } catch (e: any) {
    importResult.value = { error: true, message: e.message ?? 'Erro ao importar CSV.' }
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  const [classList, gradeList, sectionList, examList] = await Promise.allSettled([
    get<any[]>('/school/classes'),
    get<any[]>('/school/grades'),
    get<any[]>('/school/sections'),
    get<any[]>('/exams/'),
  ])
  if (classList.status === 'fulfilled')   classes.value  = classList.value
  if (gradeList.status === 'fulfilled')   grades.value   = gradeList.value
  if (sectionList.status === 'fulfilled') sections.value = sectionList.value
  if (examList.status === 'fulfilled')    exams.value    = examList.value
  loading.value = false

  classes.value.forEach(async cls => {
    loadingStudents.value[cls.id] = true
    try {
      students.value[cls.id] = await get<any[]>(`/school/students/?class_id=${cls.id}`)
    } catch {
      students.value[cls.id] = []
    } finally {
      loadingStudents.value[cls.id] = false
    }
  })
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

.slide-down-enter-active, .slide-down-leave-active { transition: opacity 0.18s ease, transform 0.18s ease }
.slide-down-enter-from { opacity: 0; transform: translateY(6px) }
.slide-down-leave-to   { opacity: 0; transform: translateY(-4px) }

.fade-swap-enter-active, .fade-swap-leave-active { transition: opacity 0.15s ease }
.fade-swap-enter-from, .fade-swap-leave-to { opacity: 0 }
</style>