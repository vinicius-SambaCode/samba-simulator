<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Questões</h1>
        <p class="page-sub">
          <span v-if="!loading">{{ questoesFiltradas.length }} questão{{ questoesFiltradas.length!==1?'ões':'' }}</span>
          <span v-else class="skel-line" />
        </p>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filter-card fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <div class="search-wrap">
        <Icon name="lucide:search" class="search-icon" />
        <input v-model="busca" placeholder="Buscar no enunciado..." class="search-input" />
        <button v-if="busca" class="search-clear" @click="busca = ''">
          <Icon name="lucide:x" class="w-3.5 h-3.5" />
        </button>
      </div>
      <div class="filter-row">
        <select v-model="filtroExam" class="filter-select">
          <option value="">Todos os simulados</option>
          <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.title }}</option>
        </select>
        <select v-model="filtroDisc" class="filter-select">
          <option value="">Todas as disciplinas</option>
          <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
        <select v-model="filtroState" class="filter-select">
          <option value="">Todos os estados</option>
          <option value="submitted">Enviada</option>
          <option value="approved">Aprovada</option>
          <option value="draft">Rascunho</option>
          <option value="rejected">Rejeitada</option>
        </select>
        <button v-if="filtroAtivo" class="clear-btn" @click="limparFiltros">
          <Icon name="lucide:x" class="w-3.5 h-3.5" /> Limpar
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="q-list fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="i in 5" :key="i" class="skel-q" :style="`--i:${i}`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!questoesFiltradas.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <Icon name="lucide:file-question" class="w-10 h-10 text-gray-200" />
      <p>{{ filtroAtivo ? 'Nenhuma questão encontrada' : 'Nenhuma questão cadastrada ainda' }}</p>
    </div>

    <!-- Lista -->
    <div v-else class="q-list fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="(q, idx) in questoesFiltradas" :key="q.id" class="q-card" :style="`--i:${idx}`">
        <div class="q-header">
          <span class="q-exam">{{ examName(q.exam_id) }}</span>
          <span class="q-disc">{{ disciplineName(q.discipline_id) }}</span>
          <span class="state-badge" :class="stateBadge(q.state)">{{ stateLabel(q.state) }}</span>
          <span v-if="q.has_images" class="img-tag">
            <Icon name="lucide:image" class="w-2.5 h-2.5" /> imagem
          </span>
        </div>
        <div class="q-stem question-content" v-html="q.stem.length > 200 ? q.stem.slice(0,200)+'…' : q.stem" />
        <div v-if="q.options?.length" class="q-opts">
          <div v-for="opt in q.options.slice(0,2)" :key="opt.label" class="q-opt"
            :class="q.correct_label===opt.label?'q-opt--correct':''">
            <span class="opt-letter">{{ opt.label }}</span>
            <span class="opt-text">{{ opt.text.length > 80 ? opt.text.slice(0,80)+'…' : opt.text }}</span>
            <Icon v-if="q.correct_label===opt.label" name="lucide:check" class="w-3 h-3 text-emerald-500 ml-auto" />
          </div>
          <p v-if="q.options.length > 2" class="q-more">+ {{ q.options.length - 2 }} alternativa{{ q.options.length-2!==1?'s':'' }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const mounted = ref(false)

const allQuestions = ref<any[]>([])
const exams        = ref<any[]>([])
const disciplines  = ref<any[]>([])
const loading      = ref(true)
const busca        = ref('')
const filtroExam   = ref<number|''>('')
const filtroDisc   = ref<number|''>('')
const filtroState  = ref('')

const filtroAtivo = computed(() => !!(busca.value||filtroExam.value||filtroDisc.value||filtroState.value))

const questoesFiltradas = computed(() => {
  let list = allQuestions.value
  if (filtroExam.value)  list = list.filter(q => q.exam_id === filtroExam.value)
  if (filtroDisc.value)  list = list.filter(q => q.discipline_id === filtroDisc.value)
  if (filtroState.value) list = list.filter(q => q.state === filtroState.value)
  if (busca.value) {
    const q = busca.value.toLowerCase()
    list = list.filter(q2 => q2.stem.toLowerCase().includes(q))
  }
  return list
})

function examName(id: number) { return exams.value.find(e=>e.id===id)?.title ?? `Simulado #${id}` }
function disciplineName(id: number) { return disciplines.value.find(d=>d.id===id)?.name ?? `#${id}` }
function stateLabel(s: string) { return ({draft:'Rascunho',submitted:'Enviada',approved:'Aprovada',rejected:'Rejeitada'}as any)[s]??s }
function stateBadge(s: string) { return ({draft:'badge-gray',submitted:'badge-blue',approved:'badge-green',rejected:'badge-red'}as any)[s]??'badge-gray' }
function limparFiltros() { busca.value=''; filtroExam.value=''; filtroDisc.value=''; filtroState.value='' }

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const [eRes,dRes] = await Promise.allSettled([get<any[]>('/exams/'), get<any[]>('/disciplines/')])
  if (eRes.status==='fulfilled') exams.value       = eRes.value
  if (dRes.status==='fulfilled') disciplines.value = dRes.value

  const qResults = await Promise.allSettled(exams.value.map(e => get<any[]>(`/exams/${e.id}/questions`)))
  const all: any[] = []
  exams.value.forEach((e, i) => {
    const r = qResults[i]
    if (r.status === 'fulfilled') all.push(...r.value.map((q:any) => ({...q, exam_id:e.id})))
  })
  allQuestions.value = all
  loading.value = false
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub    { font-size:.8rem; color:#9ca3af; margin:0; }
.skel-line   { display:inline-block; width:10rem; height:.875rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s ease-in-out infinite; }

.filter-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem; display:flex; flex-direction:column; gap:.75rem; }
.search-wrap { position:relative; }
.search-icon { position:absolute; left:.875rem; top:50%; transform:translateY(-50%); width:.875rem; height:.875rem; color:#d1d5db; }
.search-input { width:100%; padding:.55rem .875rem .55rem 2.5rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; background:white; outline:none; transition:border-color .13s; }
.search-input:focus { border-color:#93c5fd; }
.search-clear { position:absolute; right:.875rem; top:50%; transform:translateY(-50%); color:#d1d5db; }
.search-clear:hover { color:#6b7280; }
.filter-row { display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; }
.filter-select { padding:.4rem .625rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.75rem; color:#374151; background:white; outline:none; }
.clear-btn { display:inline-flex; align-items:center; gap:.3rem; padding:.4rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.75rem; font-weight:600; color:#6b7280; background:white; cursor:pointer; transition:all .13s; }
.clear-btn:hover { background:#f9fafb; color:#374151; }

.q-list { display:flex; flex-direction:column; gap:.625rem; }
.skel-q { height:9rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*60ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }

.q-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem 1.25rem; display:flex; flex-direction:column; gap:.625rem; animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*40ms); transition:border-color .15s; }
.q-card:hover { border-color:#e5e7eb; }
@keyframes card-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }

.q-header { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }
.q-exam  { font-size:.68rem; font-weight:600; color:#6b7280; flex-shrink:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:12rem; }
.q-disc  { font-size:.68rem; color:#9ca3af; flex-shrink:0; }
.img-tag { display:inline-flex; align-items:center; gap:.25rem; font-size:.62rem; font-weight:700; padding:.1rem .4rem; border-radius:9999px; background:#ede9fe; color:#5b21b6; }

.state-badge { font-size:.62rem; font-weight:700; padding:.15rem .45rem; border-radius:9999px; }
.badge-gray  { background:#f3f4f6; color:#6b7280; }
.badge-blue  { background:#dbeafe; color:#1e40af; }
.badge-green { background:#d1fae5; color:#065f46; }
.badge-red   { background:#fee2e2; color:#991b1b; }

.q-stem { font-size:.8rem; color:#374151; line-height:1.6; }
.q-opts { display:flex; flex-direction:column; gap:.3rem; }
.q-opt  { display:flex; align-items:flex-start; gap:.5rem; padding:.3rem .625rem; border-radius:.5rem; background:#f9fafb; font-size:.75rem; color:#6b7280; }
.q-opt--correct { background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; }
.opt-letter { font-weight:700; flex-shrink:0; width:.875rem; }
.opt-text   { flex:1; overflow:hidden; display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; }
.q-more { font-size:.68rem; color:#9ca3af; text-align:right; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
</style>