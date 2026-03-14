<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Meus simulados</h1>
        <p class="page-sub">Simulados em que você foi atribuído</p>
      </div>
      <button class="btn-refresh" :class="loading?'loading':''" @click="recarregar">
        <Icon :name="loading?'lucide:loader-2':'lucide:refresh-cw'" class="w-3.5 h-3.5" :class="loading?'animate-spin':''" />
        Atualizar
      </button>
    </div>

    <!-- Filtros -->
    <div class="pills fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <button v-for="f in filtros" :key="f.value"
        class="pill" :class="filtroAtivo===f.value?'pill-on':'pill-off'"
        @click="filtroAtivo=f.value">
        {{ f.label }}
        <span class="pill-count">{{ contarFiltro(f.value) }}</span>
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="list fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="i in 4" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!listaFiltrada.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <Icon name="lucide:clipboard-list" class="w-10 h-10 text-gray-200" />
      <p>{{ filtroAtivo==='todos' ? 'Aguarde ser atribuído pelo coordenador' : 'Nenhum simulado neste filtro' }}</p>
    </div>

    <!-- Lista -->
    <div v-else class="list fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <template v-for="(item, idx) in listaFiltrada" :key="item.exam.id">

        <!-- Clicável -->
        <NuxtLink v-if="itemTo(item)"
          :to="itemTo(item)"
          class="exam-row exam-row--link"
          :class="item.exam.status==='collecting' ? 'exam-row--active' : ''"
          :style="`--i:${idx}`">
          <div class="row-icon" :class="iconBg(item.exam.status, item.progresso)">
            <Icon :name="iconName(item.exam.status, item.progresso)" class="w-5 h-5"
              :class="[iconColor(item.exam.status, item.progresso), item.progresso>0&&item.progresso<100?'animate-pulse':'']" />
          </div>
          <div class="row-body">
            <div class="row-top">
              <span class="row-title">{{ item.exam.title }}</span>
              <span class="status-badge" :class="statusBadge(item.exam.status)">{{ statusLabel(item.exam.status) }}</span>
            </div>
            <template v-if="item.exam.status==='collecting' && item.progressInfo">
              <div class="prog-row">
                <div class="prog-bar">
                  <div class="prog-fill" :class="item.progresso===100?'bg-emerald-400':'bg-blue-400'" :style="`width:${item.progresso}%`" />
                </div>
                <span class="prog-text" :class="item.progresso===100?'text-emerald-600':''">{{ item.progressInfo.submitted }}/{{ item.progressInfo.quota }}</span>
                <span v-if="item.progresso<100" class="faltam-tag">faltam {{ item.progressInfo.quota - item.progressInfo.submitted }}</span>
              </div>
            </template>
            <p v-else class="row-meta">{{ item.exam.options_count }} alternativas<template v-if="item.progressInfo"> · {{ item.progressInfo.submitted }} questão(ões)</template></p>
          </div>
          <Icon name="lucide:chevron-right" class="row-arrow" />
        </NuxtLink>

        <!-- Não clicável -->
        <div v-else
          class="exam-row"
          :style="`--i:${idx}`">
          <div class="row-icon" :class="iconBg(item.exam.status, item.progresso)">
            <Icon :name="iconName(item.exam.status, item.progresso)" class="w-5 h-5" :class="iconColor(item.exam.status, item.progresso)" />
          </div>
          <div class="row-body">
            <div class="row-top">
              <span class="row-title">{{ item.exam.title }}</span>
              <span class="status-badge" :class="statusBadge(item.exam.status)">{{ statusLabel(item.exam.status) }}</span>
            </div>
            <p class="row-meta">{{ item.exam.options_count }} alternativas<template v-if="item.progressInfo"> · {{ item.progressInfo.submitted }} questão(ões)</template></p>
          </div>
          <Icon name="lucide:lock" class="w-3.5 h-3.5 text-gray-200 flex-shrink-0" />
        </div>

      </template>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const items   = ref<any[]>([])
const loading = ref(true)
const mounted = ref(false)
const filtroAtivo = ref('todos')

const filtros = [
  { value:'todos',      label:'Todos'      },
  { value:'collecting', label:'Em coleta'  },
  { value:'concluido',  label:'Concluídos' },
  { value:'outros',     label:'Outros'     },
]

const listaOrdenada = computed(() =>
  [...items.value].sort((a,b) => {
    if (a.exam.status==='collecting' && b.exam.status!=='collecting') return -1
    if (a.exam.status!=='collecting' && b.exam.status==='collecting') return 1
    return b.progresso - a.progresso
  })
)
const listaFiltrada = computed(() => {
  if (filtroAtivo.value==='todos')      return listaOrdenada.value
  if (filtroAtivo.value==='collecting') return listaOrdenada.value.filter(i=>i.exam.status==='collecting')
  if (filtroAtivo.value==='concluido')  return listaOrdenada.value.filter(i=>i.progresso===100)
  return listaOrdenada.value.filter(i=>i.exam.status!=='collecting')
})

function contarFiltro(v: string) {
  if (v==='todos')      return items.value.length
  if (v==='collecting') return items.value.filter(i=>i.exam.status==='collecting').length
  if (v==='concluido')  return items.value.filter(i=>i.progresso===100).length
  return items.value.filter(i=>i.exam.status!=='collecting').length
}

function itemTo(item: any) {
  if (item.exam.status==='collecting') return `/dashboard/professor/simulados/${item.exam.id}`
  if (['generated','published'].includes(item.exam.status)) return '/dashboard/professor/resultados'
  return null
}

function statusLabel(s: string) {
  return ({collecting:'Em coleta',locked:'Travado',published:'Publicado',generated:'Resultados',draft:'Rascunho'}as any)[s]??s
}
function statusBadge(s: string) {
  return ({collecting:'sb-amber',locked:'sb-blue',published:'sb-emerald',generated:'sb-purple',draft:'sb-gray'}as any)[s]??'sb-gray'
}
function iconName(status: string, progresso: number) {
  if (['published','generated'].includes(status)) return 'lucide:check-circle-2'
  if (status!=='collecting') return 'lucide:clock'
  if (progresso===100) return 'lucide:check-circle-2'
  if (progresso>0) return 'lucide:circle-dot'
  return 'lucide:clipboard-list'
}
function iconBg(status: string, progresso: number) {
  if (['published','generated'].includes(status)) return 'bg-emerald-50'
  if (status!=='collecting') return 'bg-blue-50'
  if (progresso===100) return 'bg-emerald-50'
  if (progresso>0) return 'bg-amber-50'
  return 'bg-gray-50'
}
function iconColor(status: string, progresso: number) {
  if (['published','generated'].includes(status)) return 'text-emerald-500'
  if (status!=='collecting') return 'text-blue-400'
  if (progresso===100) return 'text-emerald-500'
  if (progresso>0) return 'text-amber-500'
  return 'text-gray-400'
}

async function carregarDados() {
  loading.value=true
  try {
    const exams = await get<any[]>('/exams/')
    const [progressResults, assignmentResults] = await Promise.all([
      Promise.allSettled(exams.map(e => get<any>(`/exams/${e.id}/progress`))),
      Promise.allSettled(exams.map(e => get<any>(`/exams/${e.id}/my-assignment`).catch(()=>null))),
    ])
    items.value = exams.map((exam, i) => {
      const prog = progressResults[i].status==='fulfilled' ? progressResults[i].value : null
      const myAssignment = assignmentResults[i].status==='fulfilled' ? assignmentResults[i].value : null
      let progressInfo: any = null, progresso = 0
      if (prog?.disciplines?.length) {
        const discId = myAssignment?.discipline_id
        const myDisc = discId ? prog.disciplines.find((d:any)=>d.discipline_id===discId)??prog.disciplines[0] : prog.disciplines[0]
        progressInfo = { submitted: myDisc.submitted??0, quota: myDisc.quota??0 }
        if (progressInfo.quota>0) progresso = Math.min(100, Math.round(progressInfo.submitted/progressInfo.quota*100))
      }
      return { exam, progressInfo, progresso }
    })
  } catch { items.value=[] } finally { loading.value=false }
}

async function recarregar() { await carregarDados() }

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  await carregarDados()
})
onActivated(carregarDados)
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub    { font-size:.8rem; color:#9ca3af; margin:0; }
.btn-refresh { display:inline-flex; align-items:center; gap:.4rem; padding:.5rem .875rem; font-size:.75rem; font-weight:700; color:#6b7280; background:white; border:1px solid #e5e7eb; border-radius:.75rem; cursor:pointer; transition:all .13s; }
.btn-refresh:hover:not(.loading) { color:#374151; border-color:#d1d5db; }
.btn-refresh.loading { pointer-events:none; opacity:.7; }
.pills { display:flex; gap:.375rem; flex-wrap:wrap; }
.pill  { display:inline-flex; align-items:center; gap:.35rem; padding:.4rem .75rem; border-radius:9999px; font-size:.72rem; font-weight:700; border:1.5px solid; cursor:pointer; transition:all .13s; }
.pill-off { border-color:#e5e7eb; background:white; color:#6b7280; }
.pill-off:hover { border-color:#d1d5db; }
.pill-on  { border-color:#111827; background:#111827; color:white; }
.pill-count { font-size:.62rem; opacity:.65; }
.list { display:flex; flex-direction:column; gap:.5rem; }
.skel-card { height:5rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s infinite; animation-delay:calc(var(--i,0)*70ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.exam-row {
  display:flex; align-items:center; gap:.875rem; padding:.875rem 1.25rem;
  background:white; border:1px solid #f3f4f6; border-radius:1rem;
  animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*40ms);
  text-decoration:none; color:inherit;
}
.exam-row--link { transition:border-color .13s, box-shadow .13s, transform .13s; cursor:pointer; }
.exam-row--link:hover { border-color:#e5e7eb; box-shadow:0 2px 10px rgba(0,0,0,.06); transform:translateY(-1px); }
.exam-row--active { border-left:3px solid #f59e0b; }
@keyframes card-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.row-icon { width:2.75rem; height:2.75rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.row-body { flex:1; min-width:0; display:flex; flex-direction:column; gap:.35rem; }
.row-top  { display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }
.row-title { font-size:.875rem; font-weight:700; color:#111827; flex:1; min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.row-meta  { font-size:.72rem; color:#9ca3af; }
.row-arrow { width:.875rem; height:.875rem; color:#d1d5db; flex-shrink:0; transition:transform .13s, color .13s; }
.exam-row--link:hover .row-arrow { color:#9ca3af; transform:translateX(2px); }
.status-badge { font-size:.62rem; font-weight:700; padding:.15rem .45rem; border-radius:9999px; flex-shrink:0; }
.sb-amber   { background:#fef3c7; color:#92400e; }
.sb-blue    { background:#dbeafe; color:#1e40af; }
.sb-emerald { background:#d1fae5; color:#065f46; }
.sb-purple  { background:#ede9fe; color:#5b21b6; }
.sb-gray    { background:#f3f4f6; color:#6b7280; }
.prog-row  { display:flex; align-items:center; gap:.5rem; }
.prog-bar  { flex:1; height:.25rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.prog-fill { height:100%; border-radius:9999px; transition:width .6s ease; }
.prog-text { font-size:.68rem; font-weight:700; flex-shrink:0; }
.faltam-tag { font-size:.62rem; font-weight:700; padding:.1rem .4rem; border-radius:9999px; background:#fef3c7; color:#92400e; flex-shrink:0; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
</style>