<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <NuxtLink :to="`/dashboard/coordenador/simulados/${examId}`" class="back-link">
          <Icon name="lucide:arrow-left" class="w-3.5 h-3.5" /> Voltar ao simulado
        </NuxtLink>
        <h1 class="page-title">Gabarito</h1>
        <p class="page-sub">
          <span v-if="!loading">{{ exam?.title }} · {{ questions.length }} questões</span>
          <span v-else class="skel-line" />
        </p>
      </div>
      <div class="header-right">
        <div class="progress-pill" :class="allAnswered ? 'pill-green' : 'pill-amber'">
          <span class="font-bold">{{ answeredCount }}/{{ questions.length }}</span>
          <span>com gabarito</span>
        </div>
        <button class="btn-primary"
          :disabled="savingAll || !pendingChanges.size"
          @click="saveAll">
          <svg v-if="savingAll" class="spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
            <path fill="currentColor" d="M4 12a8 8 0 018-8v8z" class="opacity-75"/>
          </svg>
          <Icon v-else name="lucide:save" class="w-4 h-4" />
          {{ savingAll ? 'Salvando...' : `Salvar${pendingChanges.size ? ` (${pendingChanges.size})` : ''}` }}
        </button>
      </div>
    </div>

    <!-- Status -->
    <div v-if="!loading && allAnswered" class="alert alert-green fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <Icon name="lucide:check-circle-2" class="w-5 h-5 flex-shrink-0" />
      <p>Todas as questões têm gabarito definido.</p>
    </div>
    <div v-else-if="!loading && questions.length && !allAnswered" class="alert alert-amber fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <Icon name="lucide:alert-triangle" class="w-5 h-5 flex-shrink-0" />
      <p>{{ questions.length - answeredCount }} questão(ões) sem gabarito.</p>
    </div>

    <!-- Filtros -->
    <div v-if="!loading && questions.length" class="filters fade-in" :class="{ ready: mounted }" style="--d:.1s">
      <button v-for="f in filtros" :key="f.value"
        class="pill" :class="filtroAtivo === f.value ? 'pill-active' : 'pill-idle'"
        @click="filtroAtivo = filtroAtivo === f.value ? 'all' : f.value">
        {{ f.label }} <span class="pill-count">{{ f.count }}</span>
      </button>
      <select v-model="filterDisc" class="filter-select ml-auto">
        <option value="">Todas as disciplinas</option>
        <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
      </select>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="q-grid fade-in" :class="{ ready: mounted }" style="--d:.1s">
      <div v-for="i in 6" :key="i" class="skel-q" :style="`--i:${i}`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!questoesFiltradas.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.1s">
      <Icon name="lucide:inbox" class="w-10 h-10 text-gray-200" />
      <p>Nenhuma questão encontrada</p>
    </div>

    <!-- Grid de questões -->
    <div v-else class="q-grid fade-in" :class="{ ready: mounted }" style="--d:.1s">
      <div v-for="(q, i) in questoesFiltradas" :key="q.id" class="q-card"
        :class="localAnswers[q.id] ? 'q-card--answered' : ''">
        <div class="q-header">
          <span class="q-num">#{{ questoesMap[q.id]?.order_idx ?? i+1 }}</span>
          <span class="q-disc">{{ disciplineName(q.discipline_id) }}</span>
          <span v-if="pendingChanges.has(q.id)" class="unsaved-dot" title="Alteração não salva" />
        </div>
        <div class="q-stem question-content" v-html="renderStem(q.stem, q.images ?? [])" />
        <div class="q-opts">
          <button v-for="opt in q.options" :key="opt.label"
            class="q-opt"
            :class="localAnswers[q.id] === opt.label ? 'q-opt--selected' : ''"
            @click="setAnswer(q.id, opt.label)">
            <span class="opt-circle" :class="localAnswers[q.id] === opt.label ? 'opt-circle--on' : ''">
              {{ opt.label }}
            </span>
            <span class="opt-text question-content" v-html="renderOption(opt.text, opt.label, q.images??[])" />
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
useHead({ link: [{ rel:'stylesheet', href:'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css' }] })

const route = useRoute()
const { get, patch } = useApi()
const { renderStem, renderOption } = useQuestionRenderer()
const examId  = computed(() => Number(route.params.id))
const mounted = ref(false)

const exam        = ref<any>(null)
const questions   = ref<any[]>([])
const disciplines = ref<any[]>([])
const loading     = ref(true)
const savingAll   = ref(false)
const filtroAtivo = ref('all')
const filterDisc  = ref<number|''>('')

// gabarito local: question_id → label
const localAnswers  = reactive<Record<number,string>>({})
const pendingChanges= ref(new Set<number>())
// mapa question_id → link (para saber order_idx)
const questoesMap   = ref<Record<number,any>>({})

const answeredCount = computed(() => questions.value.filter(q=>!!localAnswers[q.id]).length)
const allAnswered   = computed(() => questions.value.length > 0 && answeredCount.value === questions.value.length)

const filtros = computed(() => [
  { value:'all',        label:'Todas',        count: questions.value.length },
  { value:'answered',   label:'Com gabarito', count: answeredCount.value },
  { value:'unanswered', label:'Sem gabarito', count: questions.value.length - answeredCount.value },
])

const questoesFiltradas = computed(() => {
  let list = questions.value
  if (filterDisc.value) list = list.filter(q => q.discipline_id === filterDisc.value)
  if (filtroAtivo.value === 'answered')   list = list.filter(q =>  !!localAnswers[q.id])
  if (filtroAtivo.value === 'unanswered') list = list.filter(q => !localAnswers[q.id])
  return list
})

function disciplineName(id: number) { return disciplines.value.find(d=>d.id===id)?.name??`#${id}` }

function setAnswer(questionId: number, label: string) {
  if (localAnswers[questionId] === label) {
    delete localAnswers[questionId]
    pendingChanges.value.delete(questionId)
  } else {
    localAnswers[questionId] = label
    pendingChanges.value.add(questionId)
  }
}

async function saveAll() {
  if (!pendingChanges.value.size) return
  savingAll.value = true
  const ids = [...pendingChanges.value]
  await Promise.allSettled(ids.map(async qid => {
    const link = questoesMap.value[qid]
    if (!link) return
    try {
      await patch(`/exams/${examId.value}/links/${link.id}/answer`, {}, `answer=${localAnswers[qid]??''}`)
      pendingChanges.value.delete(qid)
    } catch {}
  }))
  savingAll.value = false
}

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const [examRes, linksRes, discRes] = await Promise.allSettled([
    get<any>(`/exams/${examId.value}`),
    get<any[]>(`/exams/${examId.value}/links`),
    get<any[]>('/disciplines/'),
  ])
  if (examRes.status === 'fulfilled')  exam.value        = examRes.value
  if (discRes.status === 'fulfilled')  disciplines.value = discRes.value
  if (linksRes.status === 'fulfilled') {
    const links = linksRes.value
    for (const link of links) {
      questoesMap.value[link.question_id] = link
      if (link.correct_label) localAnswers[link.question_id] = link.correct_label
    }
    // Load questions
    const qRes = await get<any[]>(`/exams/${examId.value}/questions`).catch(()=>[])
    questions.value = qRes
  }
  loading.value = false
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }

.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.back-link { display:inline-flex; align-items:center; gap:.4rem; font-size:.72rem; font-weight:700; color:#9ca3af; text-decoration:none; margin-bottom:.5rem; }
.back-link:hover { color:#374151; }
.page-title { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub   { font-size:.8rem; color:#9ca3af; margin:0; }
.skel-line  { display:inline-block; width:12rem; height:.875rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s ease-in-out infinite; }
.header-right { display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; }

.progress-pill { display:flex; align-items:center; gap:.5rem; padding:.4rem .875rem; border-radius:9999px; font-size:.75rem; }
.pill-green { background:#d1fae5; color:#065f46; }
.pill-amber { background:#fef3c7; color:#92400e; }

.alert { display:flex; align-items:center; gap:.75rem; padding:.875rem 1.125rem; border-radius:.875rem; font-size:.8rem; font-weight:600; }
.alert p { margin:0; }
.alert-green { background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; }
.alert-amber { background:#fffbeb; border:1px solid #fde68a; color:#92400e; }

.filters { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }
.pill { display:inline-flex; align-items:center; gap:.35rem; padding:.4rem .75rem; border-radius:9999px; font-size:.72rem; font-weight:700; border:1.5px solid; cursor:pointer; transition:all .13s; }
.pill-idle   { border-color:#e5e7eb; background:white; color:#6b7280; }
.pill-idle:hover { border-color:#d1d5db; }
.pill-active { border-color:#111827; background:#111827; color:white; }
.pill-count  { font-size:.65rem; opacity:.7; }
.filter-select { font-size:.72rem; border:1px solid #e5e7eb; border-radius:.625rem; padding:.4rem .625rem; background:white; color:#374151; outline:none; }

.q-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:.75rem; }
.skel-q { height:14rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*60ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }

.q-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem; display:flex; flex-direction:column; gap:.75rem; transition:border-color .15s; }
.q-card--answered { border-color:#bbf7d0; }
.q-header { display:flex; align-items:center; gap:.5rem; }
.q-num   { font-size:.68rem; font-weight:700; color:#9ca3af; }
.q-disc  { font-size:.68rem; color:#9ca3af; flex:1; }
.unsaved-dot { width:.45rem; height:.45rem; border-radius:50%; background:#f59e0b; }
.q-stem  { font-size:.8rem; color:#374151; line-height:1.6; }
.q-opts  { display:flex; flex-direction:column; gap:.3rem; }
.q-opt   { display:flex; align-items:flex-start; gap:.5rem; padding:.375rem .5rem; border-radius:.5rem; border:1.5px solid #f3f4f6; cursor:pointer; text-align:left; background:white; transition:all .13s; font-size:.75rem; color:#6b7280; }
.q-opt:hover { border-color:#d1d5db; }
.q-opt--selected { border-color:#10b981; background:#f0fdf4; color:#166534; }
.opt-circle { width:1.5rem; height:1.5rem; border-radius:9999px; border:2px solid currentColor; display:flex; align-items:center; justify-content:center; font-size:.65rem; font-weight:800; flex-shrink:0; transition:all .13s; }
.opt-circle--on { background:#10b981; border-color:#10b981; color:white; }
.opt-text { flex:1; }

.btn-primary { display:inline-flex; align-items:center; gap:.4rem; padding:.55rem 1.1rem; background:#111827; color:white; font-size:.8rem; font-weight:700; border-radius:.75rem; border:none; cursor:pointer; transition:all .13s; }
.btn-primary:hover:not(:disabled) { background:#1f2937; }
.btn-primary:disabled { background:#e5e7eb; color:#9ca3af; cursor:not-allowed; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
@keyframes spin { to { transform:rotate(360deg); } }
.spin { animation:spin .8s linear infinite; }

.question-content :deep(img) { max-width:100%; border-radius:.375rem; }
.question-content :deep(.katex) { font-size:.85em; }
</style>