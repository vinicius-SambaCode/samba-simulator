<template>
  <div class="page">

    <!-- Overlay geração PDF -->
    <Transition name="pop">
      <div v-if="batchOverlay" class="overlay">
        <div class="overlay-card">
          <div class="overlay-spinner">
            <svg class="spin-svg" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="34" fill="none" stroke="#e5e7eb" stroke-width="6"/>
              <circle cx="40" cy="40" r="34" fill="none" stroke="#3b82f6" stroke-width="6"
                stroke-linecap="round"
                :stroke-dasharray="`${(batchElapsed % 20) * 10.7} 214`"
                style="transform:rotate(-90deg);transform-origin:center;transition:stroke-dasharray 1s linear"/>
            </svg>
            <Icon name="lucide:book-open" class="overlay-icon" />
          </div>
          <p class="overlay-label">{{ batchSteps[batchStepIdx]?.label ?? 'Processando…' }}</p>
          <p class="overlay-sub">{{ batchSteps[batchStepIdx]?.sublabel ?? '' }}</p>
          <div class="overlay-timer">
            <Icon name="lucide:timer" class="w-4 h-4 text-gray-400" />
            <span>{{ fmtTime(batchElapsed) }}</span>
          </div>
          <div v-if="batchSteps.length > 1" class="overlay-steps">
            <div v-for="(step, i) in batchSteps" :key="i"
              class="overlay-step" :class="i === batchStepIdx ? 'step-active' : step.done ? 'step-done' : 'step-pending'">
              <div class="step-dot">
                <Icon v-if="step.done" name="lucide:check" class="w-3 h-3 text-emerald-500" />
                <div v-else-if="i === batchStepIdx" class="dot-pulse" />
                <div v-else class="dot-empty" />
              </div>
              <span>{{ step.label }}</span>
            </div>
          </div>
          <p class="overlay-hint">Não feche esta janela…</p>
        </div>
      </div>
    </Transition>

    <!-- Breadcrumb -->
    <div :class="{ ready: mounted }" class="fade-in">
      <NuxtLink to="/dashboard/coordenador/simulados" class="back-link">
        <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" /> Todos os simulados
      </NuxtLink>
    </div>

    <!-- Header card -->
    <div :class="{ ready: mounted }" class="fade-in" style="--d:.04s">
      <div v-if="loading" class="skel-header" />
      <div v-else class="header-card">
        <div class="header-main">
          <div class="header-icon" :class="statusBg(exam?.status)">
            <Icon :name="statusIcon(exam?.status)" class="w-5 h-5" :class="statusIconColor(exam?.status)" />
          </div>
          <div class="header-info">
            <div class="header-title-row">
              <h1 class="header-title">{{ exam?.title }}</h1>
              <span class="status-badge" :class="statusBadge(exam?.status)">
                <span class="status-dot" :class="statusDotColor(exam?.status)" />
                {{ statusLabel(exam?.status) }}
              </span>
            </div>
            <p class="header-meta">
              {{ exam?.area || 'Sem área' }} · {{ exam?.options_count }} alternativas · {{ answerSourceLabel(exam?.answer_source) }}
            </p>
          </div>
        </div>
        <div class="header-actions">
          <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/editar`" class="btn-secondary">
            <Icon name="lucide:settings-2" class="w-3.5 h-3.5" /> <span class="hidden sm:inline">Configurar</span>
          </NuxtLink>
          <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/gabarito`" class="btn-secondary">
            <Icon name="lucide:check-square" class="w-3.5 h-3.5" /> <span class="hidden sm:inline">Gabarito</span>
          </NuxtLink>
          <button v-if="exam?.status === 'collecting' || exam?.status === 'review'"
            class="btn-primary" @click="showLockModal = true">
            <Icon name="lucide:lock" class="w-3.5 h-3.5" /> <span class="hidden sm:inline">Travar</span>
          </button>
          <button v-if="exam?.status === 'locked'"
            class="btn-indigo" @click="showGenerateModal = true">
            <Icon name="lucide:book-open" class="w-3.5 h-3.5" /> <span class="hidden sm:inline">Gerar cadernos</span>
          </button>
          <span v-if="exam?.status === 'generated' || exam?.status === 'published'" class="btn-done">
            <Icon name="lucide:check-circle-2" class="w-3.5 h-3.5" />
            <span class="hidden sm:inline">{{ exam?.status === 'published' ? 'Publicado' : 'Gerado' }}</span>
          </span>
        </div>
        <!-- Stats strip -->
        <div class="stats-strip">
          <div v-for="s in statCards" :key="s.label" class="stat-item">
            <div class="stat-icon-sm" :class="s.iconBg">
              <Icon :name="s.icon" class="w-3.5 h-3.5" :class="s.iconColor" />
            </div>
            <div>
              <p class="stat-value">{{ s.value }}</p>
              <p class="stat-label">{{ s.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Grid progresso + turmas -->
    <div class="main-grid fade-in" :class="{ ready: mounted }" style="--d:.08s">

      <!-- Progresso disciplinas -->
      <div class="card">
        <div class="card-header">
          <div class="card-title"><Icon name="lucide:bar-chart-2" class="w-4 h-4 text-gray-400" /> Progresso por disciplina</div>
          <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/editar`" class="link-sm">
            <Icon name="lucide:settings-2" class="w-3 h-3" /> Cotas
          </NuxtLink>
        </div>
        <div v-if="loadingProgress" class="card-loading">
          <div v-for="i in 3" :key="i" class="skel-row" :style="`--i:${i}`" />
        </div>
        <div v-else-if="!progress?.disciplines?.length" class="card-empty">
          <Icon name="lucide:inbox" class="w-7 h-7 text-gray-200" />
          <p>Nenhuma cota definida</p>
          <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}/editar`" class="link-sm">Configurar →</NuxtLink>
        </div>
        <div v-else class="disc-list">
          <div v-for="disc in progress.disciplines" :key="disc.discipline_id" class="disc-item">
            <div class="disc-top">
              <span class="disc-name">{{ disciplineName(disc.discipline_id) }}</span>
              <div class="disc-right">
                <span class="disc-count">{{ disc.submitted }}/{{ disc.quota }}</span>
                <span class="disc-tag" :class="disc.remaining === 0 ? 'tag-green' : 'tag-amber'">
                  {{ disc.remaining === 0 ? 'Completo' : `${disc.remaining} restante${disc.remaining !== 1 ? 's' : ''}` }}
                </span>
              </div>
            </div>
            <div class="prog-bar">
              <div class="prog-fill" :class="disc.remaining === 0 ? 'bg-emerald-400' : 'bg-blue-400'"
                :style="`width:${disc.quota > 0 ? Math.min(100, disc.submitted/disc.quota*100) : 0}%`" />
            </div>
          </div>
        </div>
      </div>

      <!-- Turmas -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <Icon name="lucide:users" class="w-4 h-4 text-gray-400" /> Turmas
            <span class="count-badge">{{ examClasses.length }}</span>
          </div>
          <button v-if="exam?.status === 'collecting'" class="link-sm" @click="showAssignModal = true">
            <Icon name="lucide:plus" class="w-3 h-3" /> Vincular
          </button>
        </div>
        <div v-if="loadingClasses" class="card-loading">
          <div v-for="i in 3" :key="i" class="skel-row" :style="`--i:${i}`" />
        </div>
        <div v-else-if="!examClasses.length" class="card-empty">
          <Icon name="lucide:users" class="w-7 h-7 text-gray-200" />
          <p>Nenhuma turma vinculada</p>
          <button v-if="exam?.status === 'collecting'" class="link-sm" @click="showAssignModal = true">Vincular turmas →</button>
        </div>
        <ul v-else class="class-list">
          <li v-for="cls in examClasses" :key="cls.class_id" class="class-item">
            <div class="class-icon"><Icon name="lucide:users" class="w-3.5 h-3.5 text-blue-400" /></div>
            <span class="class-name">{{ cls.class_name }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Cadernos (generated+) -->
    <div v-if="exam?.status === 'generated' || exam?.status === 'published'" class="card fade-in" :class="{ ready: mounted }" style="--d:.12s">
      <div class="card-header">
        <div class="card-title"><Icon name="lucide:download" class="w-4 h-4 text-gray-400" /> Download de cadernos</div>
      </div>
      <div class="booklet-section">
        <div class="booklet-tabs">
          <button v-for="cls in examClasses" :key="cls.class_id"
            class="booklet-tab" :class="bookletClassId === cls.class_id ? 'booklet-tab--on' : ''"
            @click="selectBookletClass(cls.class_id)">
            {{ cls.class_name }}
          </button>
        </div>
        <div v-if="bookletClassId" class="booklet-actions">
          <button class="btn-download" :disabled="batchLoading.booklets" @click="downloadBatch('booklets')">
            <Icon name="lucide:book-open" class="w-4 h-4" />
            {{ batchLoading.booklets ? 'Gerando...' : 'Baixar todos os cadernos' }}
          </button>
          <button class="btn-download" :disabled="batchLoading.answers" @click="downloadBatch('answers')">
            <Icon name="lucide:file-check" class="w-4 h-4" />
            {{ batchLoading.answers ? 'Gerando...' : 'Baixar cartões resposta' }}
          </button>
        </div>
        <p v-if="bookletError" class="error-msg">{{ bookletError }}</p>
        <div v-if="loadingBooklets" class="card-loading">
          <div v-for="i in 3" :key="i" class="skel-row" :style="`--i:${i}`" />
        </div>
        <ul v-else-if="students.length" class="student-list">
          <li v-for="st in students" :key="st.id" class="student-item">
            <div class="student-info">
              <span class="student-name">{{ st.name }}</span>
              <span class="student-ra">RA {{ st.ra }}</span>
            </div>
            <div class="student-actions">
              <button class="btn-dl-sm" :disabled="pdfLoading[`b_${st.id}`]" @click="downloadStudentBooklet(st.id, st.name, 'booklet')">
                <Icon name="lucide:book-open" class="w-3.5 h-3.5" />
              </button>
              <button class="btn-dl-sm" :disabled="pdfLoading[`a_${st.id}`]" @click="downloadStudentBooklet(st.id, st.name, 'answer')">
                <Icon name="lucide:file-check" class="w-3.5 h-3.5" />
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Questões (colapsável, fechado por padrão) -->
    <div class="card fade-in" :class="{ ready: mounted }" style="--d:.16s">
      <button class="card-header card-header--toggle" @click="questoesOpen = !questoesOpen">
        <div class="card-title">
          <Icon name="lucide:help-circle" class="w-4 h-4 text-gray-400" />
          Questões
          <span class="count-badge">{{ questions.length }}</span>
        </div>
        <div class="flex items-center gap-2">
          <select v-if="questoesOpen" v-model="filterDisc" class="filter-select" @click.stop>
            <option value="">Todas as disciplinas</option>
            <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
          <Icon :name="questoesOpen ? 'lucide:chevron-up' : 'lucide:chevron-down'" class="w-4 h-4 text-gray-400 flex-shrink-0" />
        </div>
      </button>

      <Transition name="collapse">
        <div v-if="questoesOpen">
          <div v-if="loadingQuestions" class="card-loading">
            <div v-for="i in 3" :key="i" class="skel-row tall" :style="`--i:${i}`" />
          </div>
          <div v-else-if="!questionsFiltradas.length" class="card-empty">
            <Icon name="lucide:file-question" class="w-7 h-7 text-gray-200" />
            <p>Nenhuma questão enviada</p>
          </div>
          <div v-else class="q-list">
            <div v-for="(q, i) in questionsFiltradas" :key="q.id" class="q-item group">
              <div class="q-num">{{ i + 1 }}</div>
              <div class="q-body">
                <div class="q-stem question-content" v-html="renderStem(q.stem, q.images ?? [])" />
                <div class="q-options">
                  <div v-for="opt in q.options" :key="opt.label" class="q-opt"
                    :class="q.correct_label === opt.label ? 'q-opt--correct' : ''">
                    <span class="q-opt-label">{{ opt.label }}</span>
                    <span class="question-content" v-html="renderOption(opt.text, opt.label, q.images ?? [])" />
                    <Icon v-if="q.correct_label === opt.label" name="lucide:check" class="w-3 h-3 text-emerald-500 ml-auto flex-shrink-0" />
                  </div>
                </div>
              </div>
              <div class="q-actions">
                <button class="q-action" title="Editar" @click="openEditQuestion(q)">
                  <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Modal: travar -->
    <Transition name="modal">
      <div v-if="showLockModal" class="modal-overlay" @click.self="showLockModal = false">
        <div class="modal-box">
          <div class="modal-icon-wrap bg-blue-50">
            <Icon name="lucide:lock" class="w-5 h-5 text-blue-500" />
          </div>
          <h3 class="modal-title">Travar simulado</h3>
          <p class="modal-body">Após travado, professores não poderão mais enviar questões.</p>
          <p v-if="lockError" class="error-msg">{{ lockError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showLockModal = false">Cancelar</button>
            <button class="btn-blue" :disabled="locking" @click="lockExam">
              {{ locking ? 'Travando...' : 'Sim, travar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: gerar cadernos -->
    <Transition name="modal">
      <div v-if="showGenerateModal" class="modal-overlay" @click.self="showGenerateModal = false">
        <div class="modal-box">
          <div class="modal-icon-wrap bg-indigo-50">
            <Icon name="lucide:book-open" class="w-5 h-5 text-indigo-500" />
          </div>
          <h3 class="modal-title">Gerar cadernos</h3>
          <p class="modal-body">Será gerado um caderno e cartão de resposta para cada aluno das turmas vinculadas.</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showGenerateModal = false">Cancelar</button>
            <button class="btn-indigo" @click="generateBooklets">Gerar</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: vincular turmas -->
    <Transition name="modal">
      <div v-if="showAssignModal" class="modal-overlay" @click.self="showAssignModal = false">
        <div class="modal-box modal-box--wide">
          <h3 class="modal-title">Vincular turmas</h3>
          <div class="relative mb-3">
            <Icon name="lucide:search" class="search-icon-sm" />
            <input v-model="buscaTurma" placeholder="Buscar turma..." class="field-input pl-8" />
          </div>
          <div class="class-selector">
            <label v-for="cls in turmasFiltradas" :key="cls.id" class="class-check-item">
              <input type="checkbox" :value="cls.id" v-model="selectedClasses" class="accent-blue-600" />
              <span>{{ cls.name }}</span>
            </label>
            <p v-if="!turmasFiltradas.length" class="empty-note">Todas as turmas já estão vinculadas</p>
          </div>
          <p v-if="assignError" class="error-msg mt-2">{{ assignError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showAssignModal = false">Cancelar</button>
            <button class="btn-primary" :disabled="!selectedClasses.length || assigning" @click="assignClasses">
              {{ assigning ? 'Vinculando...' : `Vincular ${selectedClasses.length || ''} turma${selectedClasses.length !== 1 ? 's' : ''}` }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: editar questão -->
    <Transition name="modal">
      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal-box modal-box--wide">
          <h3 class="modal-title">Editar questão</h3>
          <div class="field mb-3">
            <label class="field-label">Enunciado</label>
            <textarea v-model="editForm.stem" rows="4" class="field-input resize-none" />
          </div>
          <div class="field mb-3">
            <label class="field-label">Alternativas</label>
            <div class="space-y-1.5">
              <div v-for="opt in editForm.options" :key="opt.label" class="flex items-center gap-2">
                <button class="opt-sel-btn"
                  :class="editForm.correct_label === opt.label ? 'opt-sel-btn--on' : ''"
                  @click="editForm.correct_label = opt.label">{{ opt.label }}</button>
                <input v-model="opt.text" class="field-input flex-1" />
              </div>
            </div>
          </div>
          <p v-if="editError" class="error-msg mb-2">{{ editError }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="showEditModal = false">Cancelar</button>
            <button class="btn-primary" :disabled="savingEdit" @click="saveEdit">
              {{ savingEdit ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

useHead({ link: [{ rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }] })

const route   = useRoute()
const { get, post, patch, accessToken } = useApi()
const { renderStem, renderOption } = useQuestionRenderer()
const BASE_URL = useRuntimeConfig().public.apiBase as string
const examId   = computed(() => Number(route.params.id))
const mounted  = ref(false)

// Data
const exam        = ref<any>(null)
const progress    = ref<any>(null)
const examClasses = ref<any[]>([])
const disciplines = ref<any[]>([])
const allClasses  = ref<any[]>([])
const questions   = ref<any[]>([])
const students    = ref<any[]>([])
const filterDisc  = ref<number | ''>('')

// Loading
const loading         = ref(true)
const loadingProgress = ref(true)
const loadingClasses  = ref(true)
const loadingQuestions= ref(true)
const loadingBooklets = ref(false)

// Modals
const showLockModal     = ref(false)
const showGenerateModal = ref(false)
const showAssignModal   = ref(false)
const showEditModal     = ref(false)
const locking   = ref(false); const lockError   = ref('')
const assigning = ref(false); const assignError = ref('')
const generating= ref(false); const generateError= ref('')
const savingEdit= ref(false); const editError   = ref('')

const selectedClasses  = ref<number[]>([])
const buscaTurma       = ref('')
const bookletClassId   = ref<number | null>(null)
const questoesOpen     = ref(false)
const bookletError     = ref('')
const pdfLoading       = ref<Record<string,boolean>>({})
const batchLoading     = ref({ booklets: false, answers: false })

// Edit modal
const editingQuestion = ref<any>(null)
const editForm = reactive<{ stem: string; options: {label:string;text:string}[]; correct_label: string }>({ stem:'', options:[], correct_label:'' })

// Batch overlay
const batchOverlay  = ref(false)
const batchElapsed  = ref(0)
const batchTimer    = ref<any>(null)
const batchStepIdx  = ref(0)
const batchSteps    = ref<any[]>([])

const questionsFiltradas = computed(() =>
  filterDisc.value ? questions.value.filter(q => q.discipline_id === filterDisc.value) : questions.value
)
const turmasFiltradas = computed(() => {
  const vinculadas = new Set(examClasses.value.map(c => c.class_id))
  const lista = allClasses.value.filter(c => !vinculadas.has(c.id))
  const q = buscaTurma.value.toLowerCase()
  return q ? lista.filter(c => c.name.toLowerCase().includes(q)) : lista
})
const statCards = computed(() => [
  { label:'Questões', value: questions.value.length, icon:'lucide:file-text', iconBg:'bg-blue-50', iconColor:'text-blue-500' },
  { label:'Total esperado', value: progress.value?.disciplines?.reduce((s:number,d:any)=>s+d.quota,0)??0, icon:'lucide:target', iconBg:'bg-violet-50', iconColor:'text-violet-500' },
  { label:'Turmas', value: examClasses.value.length, icon:'lucide:users', iconBg:'bg-emerald-50', iconColor:'text-emerald-500' },
  { label:'Alternativas', value: exam.value?.options_count ?? '—', icon:'lucide:list-ordered', iconBg:'bg-gray-50', iconColor:'text-gray-400' },
])

function statusBg(s?: string) { return ({collecting:'bg-amber-50',review:'bg-purple-50',locked:'bg-blue-50',generated:'bg-indigo-50',published:'bg-emerald-50',draft:'bg-gray-50'}as any)[s??'']??'bg-gray-50' }
function statusIcon(s?: string) { return ({collecting:'lucide:pencil',review:'lucide:eye',locked:'lucide:lock',generated:'lucide:book-open',published:'lucide:check-circle-2',draft:'lucide:file'}as any)[s??'']??'lucide:file' }
function statusIconColor(s?: string) { return ({collecting:'text-amber-500',review:'text-purple-500',locked:'text-blue-500',generated:'text-indigo-500',published:'text-emerald-500',draft:'text-gray-400'}as any)[s??'']??'text-gray-400' }
function statusBadge(s?: string) { return ({collecting:'sb-amber',review:'sb-purple',locked:'sb-blue',generated:'sb-indigo',published:'sb-emerald',draft:'sb-gray'}as any)[s??'']??'sb-gray' }
function statusDotColor(s?: string) { return ({collecting:'dot-amber',review:'dot-purple',locked:'dot-blue',generated:'dot-indigo',published:'dot-emerald',draft:'dot-gray'}as any)[s??'']??'dot-gray' }
function statusLabel(s?: string) { return ({collecting:'Em coleta',review:'Em revisão',locked:'Travado',generated:'Gerado',published:'Publicado',draft:'Rascunho'}as any)[s??'']??s }
function answerSourceLabel(s?: string) { return ({teachers:'Gabarito pelos professores',coordinator_omr:'Gabarito via OMR'}as any)[s??'']??s }
function disciplineName(id: number) { return disciplines.value.find(d=>d.id===id)?.name??`Disciplina #${id}` }
function fmtTime(s: number) { return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}` }

function openEditQuestion(q: any) {
  editingQuestion.value = q
  editForm.stem = q.stem
  editForm.options = q.options.map((o:any) => ({ label:o.label, text:o.text }))
  editForm.correct_label = q.correct_label ?? ''
  editError.value = ''; showEditModal.value = true
}
async function saveEdit() {
  if (!editingQuestion.value) return
  savingEdit.value = true; editError.value = ''
  try {
    const updated = await patch<any>(`/exams/${examId.value}/questions/${editingQuestion.value.id}`, {
      stem: editForm.stem, options: editForm.options, correct_label: editForm.correct_label || null,
    })
    const idx = questions.value.findIndex(q=>q.id===editingQuestion.value.id)
    if (idx !== -1) questions.value[idx] = updated
    showEditModal.value = false
  } catch (e:any) { editError.value = e.message??'Erro ao salvar.' } finally { savingEdit.value = false }
}
async function lockExam() {
  locking.value = true; lockError.value = ''
  try { await post(`/exams/${examId.value}/lock`, {}); exam.value.status='locked'; showLockModal.value=false }
  catch (e:any) { lockError.value = e.message??'Erro ao travar.' } finally { locking.value=false }
}
async function assignClasses() {
  if (!selectedClasses.value.length) return
  assigning.value = true; assignError.value = ''
  try {
    await post(`/exams/${examId.value}/assign-classes`, { class_ids: selectedClasses.value })
    examClasses.value = await get<any[]>(`/exams/${examId.value}/classes`)
    showAssignModal.value=false; selectedClasses.value=[]; buscaTurma.value=''
  } catch (e:any) { assignError.value=e.message??'Erro ao vincular.' } finally { assigning.value=false }
}

function startBatchTimer(classNames: string[]) {
  batchSteps.value = classNames.map(n=>({ label:`Gerando PDFs — ${n}`, sublabel:'Caderno + cartão de resposta…', done:false }))
  batchStepIdx.value=0; batchOverlay.value=true; batchElapsed.value=0
  clearInterval(batchTimer.value); batchTimer.value=setInterval(()=>{batchElapsed.value++},1000)
}
function stopBatchTimer() { clearInterval(batchTimer.value); batchTimer.value=null; setTimeout(()=>{batchOverlay.value=false},600) }
function advanceBatchStep() { if (batchSteps.value[batchStepIdx.value]) batchSteps.value[batchStepIdx.value].done=true; batchStepIdx.value++ }

async function generateBooklets() {
  generating.value=true; generateError.value=''; showGenerateModal.value=false
  const classIds = examClasses.value.map((c:any)=>c.class_id)
  startBatchTimer(examClasses.value.map((c:any)=>c.class_name))
  try {
    if (!classIds.length) throw new Error('Nenhuma turma vinculada.')
    const token = accessToken.value
    for (const classId of classIds) {
      const res = await fetch(`${BASE_URL}/exams/${examId.value}/pdf/generate?class_id=${classId}`, {
        method:'POST', headers: token ? { Authorization:`Bearer ${token}` } : {}, credentials:'include',
      })
      if (!res.ok) { const err=await res.json().catch(()=>({detail:`Erro ${res.status}`})); throw new Error(err.detail) }
      advanceBatchStep()
    }
    exam.value.status='generated'
    if (bookletClassId.value) await loadStudents(bookletClassId.value)
  } catch (e:any) { generateError.value=e.message??'Erro ao gerar cadernos.' } finally { generating.value=false; stopBatchTimer() }
}

async function selectBookletClass(classId: number) { bookletClassId.value=classId; await loadStudents(classId) }
async function loadStudents(classId: number) {
  loadingBooklets.value=true; bookletError.value=''
  try { students.value = await get<any[]>(`/school/students?class_id=${classId}`) }
  catch { students.value=[]; bookletError.value='Não foi possível carregar alunos.' } finally { loadingBooklets.value=false }
}

async function _fetchBlob(path: string): Promise<Blob> {
  const token = accessToken.value
  const res = await fetch(`${BASE_URL}${path}`, { headers: token ? { Authorization:`Bearer ${token}` } : {}, credentials:'include' })
  if (!res.ok) throw new Error(`Erro ${res.status}`)
  return res.blob()
}
async function _triggerDownload(blob: Blob, filename: string) {
  const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=filename
  document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(()=>URL.revokeObjectURL(url),1000)
}
async function downloadStudentBooklet(studentId: number, studentName: string, type: 'booklet'|'answer') {
  const key=`${type==='booklet'?'b':'a'}_${studentId}`; pdfLoading.value[key]=true; bookletError.value=''
  try {
    const blob=await _fetchBlob(`/exams/${examId.value}/pdf/download?student_id=${studentId}&type=${type==='booklet'?'booklet':'answer_sheet'}`)
    _triggerDownload(blob, `${type}_${studentId}.pdf`)
  } catch (e:any) { bookletError.value=`Erro: ${e?.message??'tente novamente'}` } finally { pdfLoading.value[key]=false }
}
async function downloadBatch(type: 'booklets'|'answers') {
  batchLoading.value[type]=true; bookletError.value=''
  try {
    const blob=await _fetchBlob(`/exams/${examId.value}/pdf/batch/?class_id=${bookletClassId.value}&type=${type==='booklets'?'booklets':'omr'}`)
    _triggerDownload(blob, `${type}_exam${examId.value}.pdf`)
  } catch (e:any) { bookletError.value=`Erro: ${e?.message??'tente novamente'}` } finally { batchLoading.value[type]=false }
}

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const [examRes,progressRes,classesRes,discRes,allClassesRes,questionsRes] = await Promise.allSettled([
    get<any>(`/exams/${examId.value}`),
    get<any>(`/exams/${examId.value}/progress`),
    get<any[]>(`/exams/${examId.value}/classes`),
    get<any[]>('/disciplines/'),
    get<any[]>('/school/classes'),
    get<any[]>(`/exams/${examId.value}/questions`),
  ])
  if (examRes.status==='fulfilled')      exam.value        = examRes.value
  if (progressRes.status==='fulfilled')  progress.value    = progressRes.value
  if (classesRes.status==='fulfilled')   examClasses.value = classesRes.value
  if (discRes.status==='fulfilled')      disciplines.value = discRes.value
  if (allClassesRes.status==='fulfilled')allClasses.value  = allClassesRes.value
  if (questionsRes.status==='fulfilled') questions.value   = questionsRes.value
  loading.value=false; loadingProgress.value=false; loadingClasses.value=false; loadingQuestions.value=false
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }

.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }

.back-link { display:inline-flex; align-items:center; gap:.4rem; font-size:.75rem; font-weight:700; color:#9ca3af; text-decoration:none; transition:color .13s; }
.back-link:hover { color:#374151; }

/* Header card */
.skel-header { height:7rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; }
.header-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1.25rem; display:flex; flex-direction:column; gap:1rem; }
.header-main { display:flex; align-items:flex-start; gap:1rem; flex-wrap:wrap; }
.header-icon { width:3rem; height:3rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.header-info { flex:1; min-width:0; }
.header-title-row { display:flex; align-items:center; gap:.625rem; flex-wrap:wrap; margin-bottom:.25rem; }
.header-title { font-size:1.25rem; font-weight:800; color:#111827; margin:0; line-height:1.2; }
.header-meta  { font-size:.75rem; color:#9ca3af; margin:0; }
.header-actions { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }

.stats-strip { display:grid; grid-template-columns:repeat(2,1fr); gap:.75rem; padding-top:1rem; border-top:1px solid #f9fafb; }
@media(min-width:640px) { .stats-strip { grid-template-columns:repeat(4,1fr); } }
.stat-item { display:flex; align-items:center; gap:.625rem; }
.stat-icon-sm { width:2rem; height:2rem; border-radius:.5rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.stat-value { font-size:1rem; font-weight:800; color:#111827; line-height:1; }
.stat-label { font-size:.65rem; color:#9ca3af; margin-top:.15rem; }

/* Buttons */
.btn-primary, .btn-secondary, .btn-indigo, .btn-done, .btn-blue, .btn-cancel, .btn-download {
  display:inline-flex; align-items:center; gap:.4rem;
  padding:.5rem .875rem; border-radius:.625rem; font-size:.75rem; font-weight:700;
  cursor:pointer; white-space:nowrap; transition:all .13s; border:none; text-decoration:none;
}
.btn-primary  { background:#111827; color:white; } .btn-primary:hover { background:#1f2937; }
.btn-secondary { background:white; color:#374151; border:1px solid #e5e7eb; } .btn-secondary:hover { background:#f9fafb; }
.btn-indigo   { background:#4f46e5; color:white; } .btn-indigo:hover { background:#4338ca; }
.btn-blue     { background:#2563eb; color:white; } .btn-blue:hover { background:#1d4ed8; }
.btn-done     { background:#ede9fe; color:#5b21b6; cursor:default; }
.btn-cancel   { background:white; color:#6b7280; border:1px solid #e5e7eb; } .btn-cancel:hover { background:#f9fafb; }
.btn-download { background:#f9fafb; color:#374151; border:1px solid #e5e7eb; } .btn-download:hover { background:#f3f4f6; }
.btn-download:disabled { opacity:.5; cursor:not-allowed; }

/* Cards */
.card { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; }
.card-header { display:flex; align-items:center; justify-content:space-between; padding:.875rem 1.25rem; border-bottom:1px solid #f9fafb; }
.card-title  { display:flex; align-items:center; gap:.5rem; font-size:.8rem; font-weight:700; color:#111827; }
.link-sm     { display:inline-flex; align-items:center; gap:.25rem; font-size:.7rem; font-weight:600; color:#3b82f6; text-decoration:none; background:none; border:none; cursor:pointer; }
.link-sm:hover { color:#2563eb; }
.count-badge { font-size:.65rem; font-weight:700; padding:.1rem .4rem; border-radius:9999px; background:#f3f4f6; color:#6b7280; }
.card-loading { padding:.75rem 1rem; display:flex; flex-direction:column; gap:.5rem; }
.skel-row { height:3rem; background:#f9fafb; border-radius:.625rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*120ms); }
.skel-row.tall { height:4.5rem; }
.card-empty { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:2.5rem 1rem; gap:.5rem; }
.card-empty p { font-size:.78rem; color:#9ca3af; margin:0; }

/* Main grid */
.main-grid { display:grid; grid-template-columns:1fr; gap:.75rem; }
@media(min-width:1024px) { .main-grid { grid-template-columns:1fr 1fr; } }

/* Disciplinas */
.disc-list { display:flex; flex-direction:column; }
.disc-item { padding:.875rem 1.25rem; border-bottom:1px solid #f9fafb; display:flex; flex-direction:column; gap:.5rem; }
.disc-item:last-child { border-bottom:none; }
.disc-top  { display:flex; align-items:center; justify-content:space-between; gap:.5rem; }
.disc-name { font-size:.8rem; font-weight:700; color:#374151; }
.disc-right{ display:flex; align-items:center; gap:.5rem; }
.disc-count{ font-size:.75rem; font-weight:700; color:#111827; }
.disc-tag  { font-size:.65rem; font-weight:700; padding:.15rem .45rem; border-radius:9999px; }
.tag-green { background:#d1fae5; color:#065f46; }
.tag-amber { background:#fef3c7; color:#92400e; }
.prog-bar  { height:.25rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.prog-fill { height:100%; border-radius:9999px; transition:width .7s ease; }

/* Classes list */
.class-list { list-style:none; margin:0; padding:0; }
.class-item { display:flex; align-items:center; gap:.75rem; padding:.75rem 1.25rem; border-bottom:1px solid #f9fafb; }
.class-item:last-child { border-bottom:none; }
.class-icon { width:1.75rem; height:1.75rem; border-radius:.5rem; background:#eff6ff; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.class-name { font-size:.8rem; font-weight:600; color:#374151; }

/* Status badges */
.status-badge { display:inline-flex; align-items:center; gap:.35rem; font-size:.65rem; font-weight:700; padding:.2rem .5rem; border-radius:9999px; }
.status-dot   { width:.4rem; height:.4rem; border-radius:50%; }
.sb-amber  { background:#fef3c7; color:#92400e; } .dot-amber  { background:#fbbf24; }
.sb-purple { background:#ede9fe; color:#5b21b6; } .dot-purple { background:#a78bfa; }
.sb-blue   { background:#dbeafe; color:#1e40af; } .dot-blue   { background:#60a5fa; }
.sb-indigo { background:#e0e7ff; color:#3730a3; } .dot-indigo { background:#818cf8; }
.sb-emerald{ background:#d1fae5; color:#065f46; } .dot-emerald{ background:#34d399; }
.sb-gray   { background:#f3f4f6; color:#6b7280; } .dot-gray   { background:#9ca3af; }

/* Questions */
.q-list { display:flex; flex-direction:column; gap:0; }
.q-item { display:flex; gap:.875rem; padding:1rem 1.25rem; border-bottom:1px solid #f9fafb; }
.q-item:last-child { border-bottom:none; }
.q-num  { width:1.5rem; height:1.5rem; border-radius:9999px; background:#f3f4f6; font-size:.7rem; font-weight:700; color:#6b7280; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:.1rem; }
.q-body { flex:1; min-width:0; }
.q-stem { font-size:.8rem; color:#374151; line-height:1.6; margin-bottom:.625rem; }
.q-options { display:flex; flex-direction:column; gap:.3rem; }
.q-opt  { display:flex; align-items:flex-start; gap:.5rem; padding:.35rem .625rem; border-radius:.5rem; background:#f9fafb; font-size:.75rem; color:#6b7280; }
.q-opt--correct { background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; }
.q-opt-label { font-weight:700; flex-shrink:0; width:.875rem; }
.q-actions { display:flex; flex-direction:column; gap:.25rem; opacity:0; transition:opacity .15s; }
.q-item:hover .q-actions { opacity:1; }
.q-action { padding:.375rem; border-radius:.5rem; background:none; border:none; cursor:pointer; color:#9ca3af; transition:color .13s, background .13s; }
.q-action:hover { color:#3b82f6; background:#eff6ff; }

/* Filter */
.filter-select { font-size:.72rem; border:1px solid #e5e7eb; border-radius:.625rem; padding:.375rem .625rem; background:white; color:#374151; outline:none; }
.filter-select:focus { border-color:#93c5fd; }

/* Booklets */
.booklet-section { padding:1rem 1.25rem; display:flex; flex-direction:column; gap:.875rem; }
.booklet-tabs    { display:flex; gap:.4rem; flex-wrap:wrap; }
.booklet-tab     { padding:.4rem .875rem; border-radius:9999px; font-size:.72rem; font-weight:700; border:1.5px solid #e5e7eb; background:white; color:#6b7280; cursor:pointer; transition:all .13s; }
.booklet-tab--on { border-color:#111827; background:#111827; color:white; }
.booklet-actions { display:flex; gap:.5rem; flex-wrap:wrap; }
.error-msg  { font-size:.72rem; color:#ef4444; font-weight:600; }
.student-list { list-style:none; margin:0; padding:0; }
.student-item { display:flex; align-items:center; justify-content:space-between; padding:.625rem 0; border-bottom:1px solid #f9fafb; }
.student-item:last-child { border-bottom:none; }
.student-info { display:flex; flex-direction:column; gap:.1rem; }
.student-name { font-size:.78rem; font-weight:600; color:#374151; }
.student-ra   { font-size:.65rem; color:#9ca3af; }
.student-actions { display:flex; gap:.375rem; }
.btn-dl-sm { width:1.875rem; height:1.875rem; border-radius:.5rem; background:#f9fafb; border:1px solid #e5e7eb; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#6b7280; transition:all .13s; }
.btn-dl-sm:hover { background:#eff6ff; color:#3b82f6; border-color:#bfdbfe; }
.btn-dl-sm:disabled { opacity:.4; cursor:not-allowed; }

/* Modal */
.modal-overlay { position:fixed; inset:0; z-index:50; display:flex; align-items:center; justify-content:center; padding:1rem; background:rgba(0,0,0,.25); backdrop-filter:blur(2px); }
.modal-box { background:white; border-radius:1rem; padding:1.5rem; width:100%; max-width:24rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-box--wide { max-width:32rem; }
.modal-icon-wrap { width:2.5rem; height:2.5rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; }
.modal-title { font-size:1rem; font-weight:800; color:#111827; margin:0; }
.modal-body  { font-size:.8rem; color:#6b7280; margin:0; line-height:1.5; }
.modal-actions { display:flex; gap:.5rem; margin-top:.25rem; }
.class-selector { display:flex; flex-direction:column; gap:.375rem; max-height:14rem; overflow-y:auto; border:1px solid #f3f4f6; border-radius:.75rem; padding:.625rem; }
.class-check-item { display:flex; align-items:center; gap:.625rem; font-size:.8rem; color:#374151; cursor:pointer; padding:.25rem; }
.empty-note { font-size:.75rem; color:#9ca3af; text-align:center; padding:.5rem; }

/* Overlay PDF */
.overlay { position:fixed; inset:0; z-index:50; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,.5); backdrop-filter:blur(4px); }
.overlay-card { background:white; border-radius:1.25rem; padding:2rem; width:100%; max-width:24rem; display:flex; flex-direction:column; align-items:center; gap:1rem; }
.overlay-spinner { position:relative; width:5rem; height:5rem; }
.spin-svg { width:5rem; height:5rem; }
.overlay-icon { position:absolute; inset:0; margin:auto; width:2rem; height:2rem; color:#3b82f6; }
.overlay-label { font-size:.9rem; font-weight:700; color:#111827; text-align:center; }
.overlay-sub   { font-size:.75rem; color:#9ca3af; text-align:center; margin-top:-.5rem; }
.overlay-timer { display:flex; align-items:center; gap:.5rem; background:#f9fafb; border-radius:.75rem; padding:.625rem 1.25rem; }
.overlay-timer span { font-size:1.5rem; font-family:monospace; font-weight:700; color:#374151; }
.overlay-steps { width:100%; display:flex; flex-direction:column; gap:.5rem; }
.overlay-step  { display:flex; align-items:center; gap:.75rem; padding:.5rem .75rem; border-radius:.75rem; font-size:.75rem; }
.step-active  { background:#f9fafb; border:1px solid #f3f4f6; color:#374151; font-weight:600; }
.step-done    { opacity:.5; color:#6b7280; }
.step-pending { opacity:.3; color:#9ca3af; }
.step-dot     { width:1.25rem; height:1.25rem; border-radius:9999px; display:flex; align-items:center; justify-content:center; background:#f3f4f6; flex-shrink:0; }
.dot-pulse    { width:.5rem; height:.5rem; border-radius:50%; background:#3b82f6; animation:blink 1s infinite; }
.dot-empty    { width:.5rem; height:.5rem; border-radius:50%; background:#d1d5db; }
.overlay-hint { font-size:.7rem; color:#9ca3af; }

/* Form field in modal */
.field       { display:flex; flex-direction:column; gap:.375rem; }
.field-label { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#6b7280; }
.field-input { padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#111827; outline:none; transition:border-color .15s; }
.field-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.opt-sel-btn { width:2rem; height:2rem; border-radius:9999px; border:2px solid #e5e7eb; font-size:.75rem; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .13s; flex-shrink:0; background:white; color:#6b7280; }
.opt-sel-btn--on { border-color:#10b981; background:#10b981; color:white; }
.search-icon-sm { position:absolute; left:.75rem; top:50%; transform:translateY(-50%); width:1rem; height:1rem; color:#d1d5db; }
.pl-8 { padding-left:2rem; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

.card-header--toggle {
  width:100%; background:none; border:none; cursor:pointer;
  text-align:left; transition:background .13s; border-radius:0;
}
.card-header--toggle:hover { background:#fafafa; }

.collapse-enter-active { transition:all .25s ease; overflow:hidden; }
.collapse-leave-active { transition:all .2s ease;  overflow:hidden; }
.collapse-enter-from, .collapse-leave-to { opacity:0; max-height:0; }
.collapse-enter-to, .collapse-leave-from { max-height:200rem; }
.pop-enter-active { transition:all .25s cubic-bezier(.175,.885,.32,1.275); }
.pop-leave-active { transition:all .15s ease; }
.pop-enter-from, .pop-leave-to { opacity:0; transform:scale(.9); }
.modal-enter-active { transition:opacity .18s ease; }
.modal-leave-active { transition:opacity .15s ease; }
.modal-enter-from, .modal-leave-to { opacity:0; }

.question-content :deep(img) { max-width:100%; border-radius:.5rem; margin:.25rem 0; display:block; }
.question-content :deep(.katex-display) { margin:.5rem 0; overflow-x:auto; }
.question-content :deep(.katex) { font-size:.9em; }
</style>