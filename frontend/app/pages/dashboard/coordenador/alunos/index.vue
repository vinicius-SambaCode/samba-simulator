<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Alunos</h1>
        <p class="page-sub">
          <span v-if="!loading">{{ totalAlunos }} aluno{{ totalAlunos!==1?'s':'' }} em {{ allClasses.length }} turma{{ allClasses.length!==1?'s':'' }}</span>
          <span v-else class="skel-line" />
        </p>
      </div>
    </div>

    <div class="filters-row fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <div class="search-wrap">
        <Icon name="lucide:search" class="search-icon" />
        <input v-model="busca" placeholder="Buscar por nome ou RA..." class="search-input" />
        <button v-if="busca" class="search-clear" @click="busca = ''">
          <Icon name="lucide:x" class="w-3.5 h-3.5" />
        </button>
      </div>
      <select v-model="turmaFiltro" class="filter-select">
        <option value="">Todas as turmas</option>
        <option v-for="t in allClasses" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>
    </div>

    <div v-if="loading" class="list-col fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="i in 4" :key="i" class="skel-group" :style="`--i:${i}`" />
    </div>

    <div v-else-if="!turmasVisiveis.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <Icon name="lucide:users" class="w-10 h-10 text-gray-200" />
      <p>{{ busca ? 'Nenhum aluno encontrado' : 'Nenhum aluno cadastrado' }}</p>
      <button v-if="busca || turmaFiltro" class="link-btn" @click="busca=''; turmaFiltro=''">Limpar filtros</button>
    </div>

    <div v-else class="list-col fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <div v-for="(turma, idx) in turmasVisiveis" :key="turma.id" class="turma-group" :style="`--i:${idx}`">
        <div class="turma-header" @click="toggleTurma(turma.id)">
          <div class="turma-badge">{{ turma.name }}</div>
          <span class="turma-count">{{ turma.alunos.length }} aluno{{ turma.alunos.length!==1?'s':'' }}</span>
          <Icon :name="expandedTurmas.has(turma.id) ? 'lucide:chevron-up' : 'lucide:chevron-down'"
            class="w-4 h-4 text-gray-300 ml-auto" />
        </div>
        <Transition name="expand">
          <ul v-if="expandedTurmas.has(turma.id)" class="aluno-list">
            <li v-for="a in turma.alunos" :key="a.id" class="aluno-row">
              <div class="aluno-avatar">{{ initials(a.name) }}</div>
              <div class="aluno-info">
                <span class="aluno-name">{{ a.name }}</span>
                <span class="aluno-ra">RA {{ a.ra }}</span>
              </div>
            </li>
          </ul>
        </Transition>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const mounted = ref(false)

const allStudents   = ref<any[]>([])
const allClasses    = ref<any[]>([])
const loading       = ref(true)
const busca         = ref('')
const turmaFiltro   = ref<number|''>('')
const expandedTurmas= ref(new Set<number>())

function initials(name: string) { return name.split(' ').filter(Boolean).slice(0,2).map(w=>w[0]?.toUpperCase()).join('') }
function toggleTurma(id: number) { if (expandedTurmas.value.has(id)) expandedTurmas.value.delete(id); else expandedTurmas.value.add(id) }

const turmasComAlunos = computed(() => {
  return allClasses.value.map(cls => ({
    ...cls,
    alunos: allStudents.value.filter(s => s.class_id === cls.id)
  })).filter(t => t.alunos.length > 0)
})

const turmasVisiveis = computed(() => {
  let list = turmasComAlunos.value
  if (turmaFiltro.value) list = list.filter(t => t.id === turmaFiltro.value)
  if (busca.value) {
    const q = busca.value.toLowerCase()
    list = list.map(t => ({ ...t, alunos: t.alunos.filter((a:any) => a.name.toLowerCase().includes(q) || a.ra.toLowerCase().includes(q)) })).filter(t => t.alunos.length > 0)
  }
  return list
})

const totalAlunos = computed(() => allStudents.value.length)

onMounted(async () => {
  await nextTick(); setTimeout(() => { mounted.value = true }, 30)
  const [sRes, cRes] = await Promise.allSettled([
    get<any[]>('/school/students/'), get<any[]>('/school/classes'),
  ])
  if (sRes.status === 'fulfilled') allStudents.value = sRes.value
  if (cRes.status === 'fulfilled') {
    allClasses.value = cRes.value
    // Auto-expand first class
    if (cRes.value.length) expandedTurmas.value.add(cRes.value[0].id)
  }
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
.skel-line   { display:inline-block; width:12rem; height:.875rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s ease-in-out infinite; }

.filters-row { display:flex; gap:.75rem; flex-wrap:wrap; }
.search-wrap { position:relative; flex:1; min-width:200px; }
.search-icon { position:absolute; left:.875rem; top:50%; transform:translateY(-50%); width:.875rem; height:.875rem; color:#d1d5db; }
.search-input { width:100%; padding:.625rem .875rem .625rem 2.5rem; border:1px solid #e5e7eb; border-radius:.875rem; font-size:.8rem; background:white; outline:none; transition:border-color .13s; }
.search-input:focus { border-color:#93c5fd; box-shadow:0 0 0 3px #eff6ff; }
.search-clear { position:absolute; right:.875rem; top:50%; transform:translateY(-50%); color:#d1d5db; }
.search-clear:hover { color:#6b7280; }
.filter-select { padding:.625rem .875rem; border:1px solid #e5e7eb; border-radius:.875rem; font-size:.8rem; color:#374151; background:white; outline:none; min-width:180px; }

.list-col { display:flex; flex-direction:column; gap:.625rem; }
.skel-group { height:5rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*80ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.link-btn { font-size:.72rem; font-weight:600; color:#3b82f6; background:none; border:none; cursor:pointer; }

.turma-group { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*50ms); }
@keyframes card-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.turma-header { display:flex; align-items:center; gap:.875rem; padding:.875rem 1.25rem; cursor:pointer; }
.turma-badge  { width:2.25rem; height:2.25rem; border-radius:.625rem; background:#eff6ff; color:#1d4ed8; font-size:.72rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.turma-count  { font-size:.75rem; color:#6b7280; font-weight:600; }

.aluno-list  { list-style:none; margin:0; padding:0; border-top:1px solid #f9fafb; }
.aluno-row   { display:flex; align-items:center; gap:.75rem; padding:.65rem 1.25rem; border-bottom:1px solid #f9fafb; }
.aluno-row:last-child { border-bottom:none; }
.aluno-avatar { width:1.875rem; height:1.875rem; border-radius:9999px; background:#e0e7ff; color:#3730a3; font-size:.62rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.aluno-info  { flex:1; min-width:0; display:flex; flex-direction:column; gap:.08rem; }
.aluno-name  { font-size:.8rem; font-weight:600; color:#374151; }
.aluno-ra    { font-size:.65rem; color:#9ca3af; }

@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
.expand-enter-active { transition:all .22s ease; overflow:hidden; }
.expand-leave-active { transition:all .18s ease; overflow:hidden; }
.expand-enter-from, .expand-leave-to { opacity:0; max-height:0; }
.expand-enter-to, .expand-leave-from { opacity:1; max-height:60rem; }
</style>