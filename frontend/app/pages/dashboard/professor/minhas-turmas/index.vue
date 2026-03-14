<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Minhas turmas</h1>
        <p class="page-sub">Turmas em que você foi vinculado pelo coordenador</p>
      </div>
      <button class="btn-refresh" :class="loading?'loading':''" @click="carregarDados">
        <Icon :name="loading?'lucide:loader-2':'lucide:refresh-cw'" class="w-3.5 h-3.5" :class="loading?'animate-spin':''" />
        Atualizar
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="turmas-grid fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <div v-for="i in 4" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!minhasTurmas.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <Icon name="lucide:users" class="w-10 h-10 text-gray-200" />
      <p>Você ainda não foi vinculado a nenhuma turma</p>
      <p class="empty-sub">O coordenador precisa criar o vínculo turma + disciplina</p>
    </div>

    <!-- Grid de turmas -->
    <TransitionGroup v-else name="list-item" tag="div" class="turmas-grid fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <div v-for="(item, idx) in minhasTurmas" :key="item.class_id" class="turma-card" :style="`--i:${idx}`">

        <!-- Faixa cor -->
        <div class="turma-stripe" :class="CORES[idx % CORES.length].stripe" />

        <div class="turma-body">
          <!-- Header -->
          <div class="turma-header">
            <div class="turma-avatar" :class="CORES[idx % CORES.length].bg">
              {{ iniciais(item.class_name) }}
            </div>
            <div class="turma-info">
              <p class="turma-name">{{ item.class_name }}</p>
              <p class="turma-discs">{{ item.disciplines.join(', ') }}</p>
            </div>
            <span v-if="students[item.class_id]" class="alunos-badge">
              {{ students[item.class_id].length }} aluno{{ students[item.class_id].length!==1?'s':'' }}
            </span>
          </div>

          <!-- Simulados ativos desta turma -->
          <div v-if="simuladosDaTurma(item.class_id).length" class="exams-section">
            <p class="exams-label">Simulados ativos</p>
            <div class="exams-list">
              <NuxtLink
                v-for="exam in simuladosDaTurma(item.class_id)" :key="exam.id"
                :to="`/dashboard/professor/simulados/${exam.id}`"
                class="exam-chip">
                <span class="chip-dot" :class="progressoColor(exam.id)" />
                <span class="chip-title">{{ exam.title }}</span>
                <span class="chip-pct" :class="progressoColor(exam.id)">{{ progressoPct(exam.id) }}%</span>
              </NuxtLink>
            </div>
          </div>

          <!-- Alunos (preview) -->
          <div v-if="students[item.class_id]?.length" class="alunos-preview">
            <div v-for="st in students[item.class_id].slice(0,6)" :key="st.id" class="aluno-avatar" :title="st.name">
              {{ iniciais(st.name) }}
            </div>
            <span v-if="students[item.class_id].length>6" class="alunos-more">
              +{{ students[item.class_id].length - 6 }}
            </span>
          </div>
        </div>
      </div>
    </TransitionGroup>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const mounted = ref(false)
const loading = ref(true)

const minhasTurmas = ref<any[]>([])
const students     = ref<Record<number, any[]>>({})
const exams        = ref<any[]>([])
const progressMap  = ref<Record<number, any>>({})
const assignMap    = ref<Record<number, any>>({})

const CORES = [
  { stripe:'bg-blue-500',   bg:'bg-blue-500'   },
  { stripe:'bg-violet-500', bg:'bg-violet-500' },
  { stripe:'bg-emerald-500',bg:'bg-emerald-500'},
  { stripe:'bg-amber-500',  bg:'bg-amber-500'  },
  { stripe:'bg-rose-500',   bg:'bg-rose-500'   },
  { stripe:'bg-teal-500',   bg:'bg-teal-500'   },
]

function iniciais(name: string) { return name.split(' ').filter(Boolean).slice(0,2).map(w=>w[0]?.toUpperCase()).join('') }

function simuladosDaTurma(classId: number) {
  return exams.value.filter(e => {
    if (e.status !== 'collecting') return false
    const assign = assignMap.value[e.id]
    return assign?.class_id === classId
  })
}

function progressoPct(examId: number) {
  const prog = progressMap.value[examId]
  const discs = prog?.disciplines ?? []
  const quota = discs.reduce((s: number, d: any) => s + (d.quota ?? 0), 0)
  const done  = discs.reduce((s: number, d: any) => s + (d.submitted ?? 0), 0)
  if (!quota) return 0
  return Math.min(100, Math.round(done / quota * 100))
}

function progressoColor(examId: number) {
  const pct = progressoPct(examId)
  return pct === 100 ? 'text-emerald-500' : pct > 0 ? 'text-amber-500' : 'text-gray-300'
}

async function carregarDados() {
  loading.value = true
  try {
    const [subjectsRes, examsRes] = await Promise.allSettled([
      get<any[]>('/school/my-subjects'),
      get<any[]>('/exams/'),
    ])

    const subjects: any[] = subjectsRes.status === 'fulfilled' ? subjectsRes.value : []
    exams.value = examsRes.status === 'fulfilled' ? examsRes.value : []

    // Agrupa disciplines por class_id
    const turmasMap: Record<number, any> = {}
    for (const s of subjects) {
      if (!turmasMap[s.class_id]) {
        turmasMap[s.class_id] = { class_id: s.class_id, class_name: s.class_name, disciplines: [] }
      }
      turmasMap[s.class_id].disciplines.push(s.discipline_name)
    }
    minhasTurmas.value = Object.values(turmasMap)

    // Carrega alunos por turma
    await Promise.allSettled(
      minhasTurmas.value.map(async t => {
        try { students.value[t.class_id] = await get<any[]>(`/school/students?class_id=${t.class_id}`) } catch { students.value[t.class_id] = [] }
      })
    )

    // Carrega progresso + assignments dos simulados collecting
    const collectingExams = exams.value.filter(e => e.status === 'collecting')
    await Promise.allSettled(collectingExams.map(async e => {
      try {
        const [prog, assign] = await Promise.all([
          get<any>(`/exams/${e.id}/progress`),
          get<any>(`/exams/${e.id}/my-assignment`).catch(() => null),
        ])
        progressMap.value[e.id] = prog
        if (assign) assignMap.value[e.id] = assign
      } catch {}
    }))
  } finally { loading.value = false }
}

onMounted(async () => {
  await nextTick(); setTimeout(() => { mounted.value = true }, 30)
  await carregarDados()
})
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
.turmas-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:.875rem; }
.skel-card { height:14rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s infinite; animation-delay:calc(var(--i,0)*80ms); }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-state p { font-size:.875rem; font-weight:600; color:#9ca3af; margin:0; }
.empty-sub { font-size:.75rem; color:#d1d5db !important; }
.turma-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; animation:card-in .35s ease both; animation-delay:calc(var(--i,0)*50ms); }
@keyframes card-in { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.turma-stripe { height:.35rem; width:100%; }
.turma-body   { padding:1.125rem; display:flex; flex-direction:column; gap:.875rem; }
.turma-header { display:flex; align-items:flex-start; gap:.875rem; }
.turma-avatar { width:2.75rem; height:2.75rem; border-radius:.75rem; color:white; font-size:.8rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.turma-info   { flex:1; min-width:0; }
.turma-name   { font-size:.9rem; font-weight:800; color:#111827; margin:0 0 .15rem; }
.turma-discs  { font-size:.72rem; color:#9ca3af; margin:0; line-height:1.4; }
.alunos-badge { font-size:.65rem; font-weight:700; padding:.2rem .5rem; border-radius:9999px; background:#f3f4f6; color:#6b7280; flex-shrink:0; }
.exams-section { border-top:1px solid #f9fafb; padding-top:.75rem; }
.exams-label  { font-size:.65rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#9ca3af; margin:0 0 .5rem; }
.exams-list   { display:flex; flex-direction:column; gap:.35rem; }
.exam-chip    { display:flex; align-items:center; gap:.5rem; padding:.4rem .625rem; background:#fafafa; border-radius:.625rem; text-decoration:none; transition:background .13s; }
.exam-chip:hover { background:#f3f4f6; }
.chip-dot   { width:.4rem; height:.4rem; border-radius:50%; background:currentColor; flex-shrink:0; }
.chip-title { font-size:.72rem; font-weight:600; color:#374151; flex:1; min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.chip-pct   { font-size:.68rem; font-weight:700; flex-shrink:0; }
.alunos-preview { display:flex; align-items:center; gap:.25rem; border-top:1px solid #f9fafb; padding-top:.75rem; }
.aluno-avatar { width:1.75rem; height:1.75rem; border-radius:9999px; background:#f3f4f6; font-size:.6rem; font-weight:700; color:#6b7280; display:flex; align-items:center; justify-content:center; border:2px solid white; margin-left:-.375rem; }
.aluno-avatar:first-child { margin-left:0; }
.alunos-more { font-size:.68rem; font-weight:700; color:#9ca3af; margin-left:.25rem; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
.list-item-enter-active { transition:all .28s ease; }
.list-item-enter-from   { opacity:0; transform:translateY(8px); }
.list-item-leave-to     { opacity:0; }
.list-item-move         { transition:transform .3s ease; }
</style>