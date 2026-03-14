<template>
  <div class="page">

    <div class="page-header" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Simulados</h1>
        <p class="page-sub">
          <span v-if="loading" class="skel-line" />
          <span v-else>{{ exams.length }} simulado{{ exams.length !== 1 ? 's' : '' }} cadastrado{{ exams.length !== 1 ? 's' : '' }}</span>
        </p>
      </div>
      <NuxtLink to="/dashboard/coordenador/simulados/novo" class="btn-primary">
        <Icon name="lucide:plus" class="w-4 h-4" /> Novo simulado
      </NuxtLink>
    </div>

    <!-- Busca + filtros -->
    <div class="filters" :class="{ ready: mounted }">
      <div class="search-wrap">
        <Icon name="lucide:search" class="search-icon" />
        <input v-model="busca" placeholder="Buscar por título ou área..." class="search-input" />
        <button v-if="busca" class="search-clear" @click="busca = ''">
          <Icon name="lucide:x" class="w-3.5 h-3.5" />
        </button>
      </div>
      <div class="filter-pills">
        <button v-for="f in filtros" :key="f.value"
          class="pill" :class="filtroAtivo === f.value ? 'pill-active' : 'pill-idle'"
          @click="filtroAtivo = filtroAtivo === f.value ? '' : f.value">
          {{ f.label }}
          <span v-if="contagemStatus[f.value]" class="pill-count">{{ contagemStatus[f.value] }}</span>
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="exam-grid">
      <div v-for="i in 6" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <!-- Empty -->
    <div v-else-if="examsFiltrados.length === 0" class="empty-state" :class="{ ready: mounted }">
      <Icon name="lucide:file-x" class="w-10 h-10 text-gray-200" />
      <p class="empty-title">{{ busca || filtroAtivo ? 'Nenhum resultado' : 'Nenhum simulado cadastrado' }}</p>
      <p class="empty-sub">{{ busca || filtroAtivo ? 'Tente outros filtros' : 'Clique em "Novo simulado" para começar' }}</p>
    </div>

    <!-- Grid -->
    <div v-else class="exam-grid">
      <NuxtLink v-for="(exam, idx) in examsFiltrados" :key="exam.id"
        :to="`/dashboard/coordenador/simulados/${exam.id}`"
        class="exam-card" :style="`--i:${idx}`">
        <div class="exam-card-top">
          <span class="status-badge" :class="statusBadge(exam.status)">
            <span class="status-dot" :class="statusDot(exam.status)" />
            {{ statusLabel(exam.status) }}
          </span>
          <span class="exam-date">{{ formatDate(exam.created_at) }}</span>
        </div>
        <div class="exam-body">
          <p class="exam-title">{{ exam.title }}</p>
          <p class="exam-area">{{ exam.area || 'Sem área definida' }}</p>
        </div>
        <div class="exam-footer">
          <div class="exam-meta">
            <span class="meta-item"><Icon name="lucide:list-ordered" class="w-3 h-3" /> {{ exam.options_count }} opções</span>
            <span class="meta-item"><Icon name="lucide:users" class="w-3 h-3" /> {{ answerSourceLabel(exam.answer_source) }}</span>
          </div>
          <Icon name="lucide:arrow-right" class="exam-arrow" />
        </div>
      </NuxtLink>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const exams       = ref<any[]>([])
const loading     = ref(true)
const mounted     = ref(false)
const busca       = ref('')
const filtroAtivo = ref('')

const filtros = [
  { value: 'collecting', label: 'Em coleta'  },
  { value: 'review',     label: 'Em revisão' },
  { value: 'locked',     label: 'Travado'    },
  { value: 'generated',  label: 'Gerado'     },
  { value: 'published',  label: 'Publicado'  },
]

const contagemStatus = computed(() => {
  const m: Record<string,number> = {}
  for (const e of exams.value) m[e.status] = (m[e.status] ?? 0) + 1
  return m
})

const examsFiltrados = computed(() => {
  let list = exams.value
  if (filtroAtivo.value) list = list.filter(e => e.status === filtroAtivo.value)
  if (busca.value) {
    const q = busca.value.toLowerCase()
    list = list.filter(e => e.title.toLowerCase().includes(q) || (e.area ?? '').toLowerCase().includes(q))
  }
  return list
})

function statusLabel(s: string) {
  return ({ collecting:'Em coleta', review:'Em revisão', locked:'Travado', generated:'Gerado', published:'Publicado', draft:'Rascunho' } as any)[s] ?? s
}
function statusBadge(s: string) {
  return ({ collecting:'sb-amber', review:'sb-purple', locked:'sb-blue', generated:'sb-indigo', published:'sb-emerald', draft:'sb-gray' } as any)[s] ?? 'sb-gray'
}
function statusDot(s: string) {
  return ({ collecting:'dot-amber', review:'dot-purple', locked:'dot-blue', generated:'dot-indigo', published:'dot-emerald', draft:'dot-gray' } as any)[s] ?? 'dot-gray'
}
function answerSourceLabel(s: string) {
  return ({ teachers:'Professores', coordinator_omr:'Coord. OMR' } as any)[s] ?? s
}
function formatDate(d: string) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('pt-BR', { day:'2-digit', month:'short', year:'numeric' })
}

onMounted(async () => {
  await nextTick(); setTimeout(() => { mounted.value = true }, 30)
  try { exams.value = await get<any[]>('/exams/') } catch { exams.value = [] } finally { loading.value = false }
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }

.page-header {
  display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap;
  opacity:0; transform:translateY(10px); transition:opacity .35s ease, transform .35s ease;
}
.page-header.ready { opacity:1; transform:translateY(0); }
.page-title { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub   { font-size:.8rem; color:#9ca3af; margin:0; }

.filters {
  display:flex; gap:.75rem; flex-wrap:wrap;
  opacity:0; transform:translateY(8px); transition:opacity .35s ease .07s, transform .35s ease .07s;
}
.filters.ready { opacity:1; transform:translateY(0); }

.search-wrap { position:relative; flex:1; min-width:200px; }
.search-icon { position:absolute; left:.875rem; top:50%; transform:translateY(-50%); width:1rem; height:1rem; color:#d1d5db; }
.search-input {
  width:100%; padding:.625rem .875rem .625rem 2.5rem;
  border:1px solid #e5e7eb; border-radius:.75rem; font-size:.8rem; background:white;
  outline:none; transition:border-color .15s, box-shadow .15s;
}
.search-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.search-clear { position:absolute; right:.75rem; top:50%; transform:translateY(-50%); color:#d1d5db; }
.search-clear:hover { color:#6b7280; }

.filter-pills { display:flex; align-items:center; gap:.4rem; flex-wrap:wrap; }
.pill {
  display:inline-flex; align-items:center; gap:.3rem;
  padding:.4rem .75rem; border-radius:9999px; font-size:.72rem; font-weight:700;
  border:1.5px solid; cursor:pointer; white-space:nowrap; transition:all .13s;
}
.pill-idle   { border-color:#e5e7eb; background:white; color:#6b7280; }
.pill-idle:hover { border-color:#d1d5db; color:#374151; }
.pill-active { border-color:#111827; background:#111827; color:white; }
.pill-count  { font-size:.65rem; opacity:.7; }

/* Grid */
.exam-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:.75rem; }

.skel-card {
  height:10rem; background:white; border:1px solid #f3f4f6; border-radius:1rem;
  animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*60ms);
}
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.5} }
.skel-line { display:inline-block; width:55%; height:.8rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s ease-in-out infinite; }

.empty-state {
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  padding:4rem 1rem; gap:.5rem; text-align:center;
  background:white; border:2px dashed #f3f4f6; border-radius:1rem;
  opacity:0; transform:translateY(8px); transition:opacity .35s ease .14s, transform .35s ease .14s;
}
.empty-state.ready { opacity:1; transform:translateY(0); }
.empty-title { font-size:.875rem; font-weight:700; color:#9ca3af; margin:.5rem 0 0; }
.empty-sub   { font-size:.75rem; color:#d1d5db; margin:0; }

.exam-card {
  background:white; border:1px solid #f3f4f6; border-radius:1rem;
  padding:1.125rem; display:flex; flex-direction:column; gap:.875rem;
  text-decoration:none; cursor:pointer;
  transition:border-color .15s, box-shadow .15s, transform .15s;
  animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*40ms + 80ms);
}
.exam-card:hover { border-color:#e5e7eb; box-shadow:0 4px 16px rgba(0,0,0,.07); transform:translateY(-2px); }
@keyframes card-in { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

.exam-card-top { display:flex; align-items:center; justify-content:space-between; }
.exam-date     { font-size:.68rem; color:#9ca3af; }

.status-badge  { display:inline-flex; align-items:center; gap:.35rem; font-size:.65rem; font-weight:700; padding:.2rem .5rem; border-radius:9999px; }
.status-dot    { width:.4rem; height:.4rem; border-radius:50%; }
.sb-amber      { background:#fef3c7; color:#92400e; }   .dot-amber   { background:#fbbf24; }
.sb-purple     { background:#ede9fe; color:#5b21b6; }   .dot-purple  { background:#a78bfa; }
.sb-blue       { background:#dbeafe; color:#1e40af; }   .dot-blue    { background:#60a5fa; }
.sb-indigo     { background:#e0e7ff; color:#3730a3; }   .dot-indigo  { background:#818cf8; }
.sb-emerald    { background:#d1fae5; color:#065f46; }   .dot-emerald { background:#34d399; }
.sb-gray       { background:#f3f4f6; color:#6b7280; }   .dot-gray    { background:#9ca3af; }

.exam-body  { flex:1; }
.exam-title { font-size:.875rem; font-weight:700; color:#111827; margin:0 0 .2rem; line-height:1.3; }
.exam-area  { font-size:.72rem; color:#9ca3af; margin:0; }

.exam-footer { display:flex; align-items:center; justify-content:space-between; padding-top:.625rem; border-top:1px solid #f9fafb; }
.exam-meta   { display:flex; gap:.875rem; }
.meta-item   { display:flex; align-items:center; gap:.3rem; font-size:.7rem; color:#9ca3af; }
.exam-arrow  { width:.875rem; height:.875rem; color:#d1d5db; transition:transform .13s, color .13s; }
.exam-card:hover .exam-arrow { color:#60a5fa; transform:translateX(3px); }

.btn-primary {
  display:inline-flex; align-items:center; gap:.5rem; padding:.6rem 1.1rem;
  background:#111827; color:white; font-size:.8rem; font-weight:700;
  border-radius:.75rem; text-decoration:none; transition:background .13s, transform .13s; white-space:nowrap;
}
.btn-primary:hover  { background:#1f2937; transform:translateY(-1px); }
.btn-primary:active { transform:scale(.97); }
</style>