<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Minhas questões</h1>
        <p class="page-sub">Todas as questões que você criou ou importou</p>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters-card fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <div class="search-wrap">
        <Icon name="lucide:search" class="search-icon" />
        <input v-model="busca" placeholder="Buscar no enunciado..." class="search-input" />
        <button v-if="busca" class="search-clear" @click="busca=''"><Icon name="lucide:x" class="w-3.5 h-3.5" /></button>
      </div>
      <div class="filter-row">
        <select v-model="examFiltro" class="filter-select">
          <option value="">Todos os simulados</option>
          <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.title }}</option>
        </select>
        <div class="source-pills">
          <button v-for="f in fonteFiltros" :key="f.value"
            class="pill" :class="fonteFiltro===f.value?'pill-on':'pill-off'"
            @click="fonteFiltro=f.value">{{ f.label }}</button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div v-if="!loading" class="stats-row fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div class="stat-chip">
        <Icon name="lucide:layers" class="w-3.5 h-3.5 text-gray-400" />
        <span><strong>{{ questoesFiltradas.length }}</strong> questão(ões)</span>
      </div>
      <div class="stat-chip">
        <Icon name="lucide:file-text" class="w-3.5 h-3.5 text-blue-400" />
        <span class="text-blue-700"><strong>{{ contarFonte('upload') }}</strong> importadas</span>
      </div>
      <div class="stat-chip">
        <Icon name="lucide:pencil" class="w-3.5 h-3.5 text-violet-400" />
        <span class="text-violet-700"><strong>{{ contarFonte('manual') }}</strong> manuais</span>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="list fade-in" :class="{ ready: mounted }" style="--d:.1s">
      <div v-for="i in 5" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!questoesFiltradas.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.1s">
      <Icon name="lucide:help-circle" class="w-10 h-10 text-gray-200" />
      <p>{{ busca||examFiltro||fonteFiltro!=='todos' ? 'Nenhuma questão encontrada' : 'Você ainda não criou nenhuma questão' }}</p>
    </div>

    <!-- Lista -->
    <div v-else class="list fade-in" :class="{ ready: mounted }" style="--d:.1s">
      <div v-for="(q, idx) in questoesFiltradas" :key="q.id" class="q-card" :style="`--i:${idx}`">
        <div class="q-header">
          <div class="q-badges">
            <span class="exam-tag">{{ examTitle(q.exam_id) }}</span>
            <span v-if="q.has_images" class="img-tag"><Icon name="lucide:image" class="w-2.5 h-2.5" /> imagem</span>
            <span class="source-tag">{{ sourceLabel(q.source) }}</span>
          </div>
          <span v-if="q.correct_label" class="answer-tag">Gabarito: {{ q.correct_label }}</span>
        </div>
        <div class="q-stem">{{ truncate(q.stem, 200) }}</div>
        <div class="q-opts">
          <div v-for="opt in (q.options??[]).slice(0, q.options_count||4)" :key="opt.label"
            class="q-opt" :class="q.correct_label===opt.label?'q-opt--correct':''">
            <strong>{{ opt.label }}</strong>
            <span>{{ truncate(opt.text, 70) }}</span>
            <Icon v-if="q.correct_label===opt.label" name="lucide:check" class="w-3 h-3 ml-auto text-emerald-500 flex-shrink-0" />
          </div>
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
const loading      = ref(true)
const busca        = ref('')
const examFiltro   = ref<number|''>('')
const fonteFiltro  = ref('todos')

const fonteFiltros = [
  { value:'todos',  label:'Todos' },
  { value:'manual', label:'Manual' },
  { value:'upload', label:'Importado' },
]

const questoesFiltradas = computed(() => {
  let list = allQuestions.value
  if (examFiltro.value)           list = list.filter(q=>q.exam_id===examFiltro.value)
  if (fonteFiltro.value==='manual') list = list.filter(q=>q.source==='manual')
  if (fonteFiltro.value==='upload') list = list.filter(q=>q.source!=='manual')
  if (busca.value) { const qb=busca.value.toLowerCase(); list=list.filter(q=>q.stem?.toLowerCase().includes(qb)) }
  return list
})

function contarFonte(tipo: string) {
  if (tipo==='manual') return allQuestions.value.filter(q=>q.source==='manual').length
  return allQuestions.value.filter(q=>q.source!=='manual').length
}
function examTitle(id: number) { return exams.value.find(e=>e.id===id)?.title??`Simulado #${id}` }
function truncate(text: string, n: number) { return text?.length>n?text.slice(0,n)+'…':text }
function sourceLabel(s: string) { return ({manual:'Manual',paste:'Colado',docx:'Word',txt:'Texto',pdf:'PDF'}as any)[s]??s }

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const [eRes] = await Promise.allSettled([get<any[]>('/exams/')])
  if (eRes.status==='fulfilled') exams.value = eRes.value
  const results = await Promise.allSettled(exams.value.map(e=>get<any[]>(`/exams/${e.id}/questions`)))
  const all: any[] = []
  results.forEach((r,i) => {
    if (r.status==='fulfilled') r.value.forEach(q=>all.push({...q, exam_id:exams.value[i].id, options_count:exams.value[i].options_count}))
  })
  allQuestions.value = all
  loading.value = false
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; }
.page-title { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub   { font-size:.8rem; color:#9ca3af; margin:0; }
.filters-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem; display:flex; flex-direction:column; gap:.75rem; }
.search-wrap  { position:relative; }
.search-icon  { position:absolute; left:.875rem; top:50%; transform:translateY(-50%); width:1rem; height:1rem; color:#d1d5db; }
.search-input { width:100%; padding:.625rem .875rem .625rem 2.5rem; border:1px solid #e5e7eb; border-radius:.75rem; font-size:.8rem; background:white; outline:none; transition:border-color .15s; }
.search-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.search-clear { position:absolute; right:.75rem; top:50%; transform:translateY(-50%); color:#d1d5db; } .search-clear:hover { color:#6b7280; }
.filter-row   { display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; }
.filter-select{ padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.78rem; background:white; color:#374151; outline:none; }
.source-pills { display:flex; gap:.375rem; }
.pill  { padding:.375rem .75rem; border-radius:9999px; font-size:.72rem; font-weight:700; border:1.5px solid; cursor:pointer; transition:all .13s; }
.pill-off { border-color:#e5e7eb; background:white; color:#6b7280; }
.pill-off:hover { border-color:#d1d5db; }
.pill-on  { border-color:#111827; background:#111827; color:white; }
.stats-row { display:flex; align-items:center; gap:.875rem; flex-wrap:wrap; }
.stat-chip  { display:flex; align-items:center; gap:.375rem; font-size:.78rem; color:#6b7280; }
.stat-chip strong { color:#111827; }
.list { display:flex; flex-direction:column; gap:.625rem; }
.skel-card { height:8rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s infinite; animation-delay:calc(var(--i,0)*60ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.q-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem 1.25rem; display:flex; flex-direction:column; gap:.625rem; animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*35ms); }
.q-card:hover { border-color:#e5e7eb; }
@keyframes card-in { from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:translateY(0)} }
.q-header { display:flex; align-items:center; justify-content:space-between; gap:.5rem; flex-wrap:wrap; }
.q-badges { display:flex; align-items:center; gap:.375rem; flex-wrap:wrap; }
.exam-tag   { font-size:.65rem; font-weight:600; padding:.15rem .5rem; border-radius:9999px; background:#f3f4f6; color:#374151; max-width:14rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.img-tag    { font-size:.62rem; font-weight:700; padding:.15rem .4rem; border-radius:9999px; background:#ede9fe; color:#5b21b6; display:inline-flex; align-items:center; gap:.2rem; }
.source-tag { font-size:.62rem; font-weight:700; padding:.15rem .4rem; border-radius:9999px; background:#f0f9ff; color:#0369a1; }
.answer-tag { font-size:.62rem; font-weight:700; padding:.15rem .45rem; border-radius:9999px; background:#d1fae5; color:#065f46; flex-shrink:0; }
.q-stem { font-size:.8rem; color:#374151; line-height:1.6; }
.q-opts { display:flex; flex-direction:column; gap:.25rem; }
.q-opt  { display:flex; align-items:flex-start; gap:.5rem; padding:.3rem .5rem; border-radius:.5rem; background:#f9fafb; font-size:.72rem; color:#6b7280; }
.q-opt strong { flex-shrink:0; width:.875rem; }
.q-opt--correct { background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
</style>