<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Resultados</h1>
        <p class="page-sub">Desempenho da turma nos simulados em que você foi atribuído</p>
      </div>
    </div>

    <!-- Loading inicial -->
    <div v-if="loadingExams" class="list fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <div v-for="i in 3" :key="i" class="skel-card" :style="`--i:${i}`" />
    </div>

    <!-- Sem simulados -->
    <div v-else-if="!examsDisponiveis.length" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <Icon name="lucide:bar-chart-2" class="w-10 h-10 text-gray-200" />
      <p>Nenhum resultado disponível ainda</p>
      <p class="empty-sub">Os resultados aparecem após o simulado ser publicado</p>
    </div>

    <div v-else class="content-grid fade-in" :class="{ ready: mounted }" style="--d:.05s">

      <!-- Sidebar: seleção de simulado -->
      <div class="sidebar">
        <p class="section-label">Simulados</p>
        <div class="exam-list">
          <button v-for="exam in examsDisponiveis" :key="exam.id"
            class="exam-btn" :class="examSelecionado?.id===exam.id?'exam-btn--on':''"
            @click="selecionarExam(exam)">
            <div class="exam-btn-dot" :class="statusDot(exam.status)" />
            <div class="exam-btn-info">
              <span class="exam-btn-title">{{ exam.title }}</span>
              <span class="exam-btn-meta">{{ myAssignments[exam.id]?.class_name??'—' }} · {{ myAssignments[exam.id]?.discipline_name??'—' }}</span>
            </div>
            <Icon name="lucide:chevron-right" class="w-4 h-4 flex-shrink-0" :class="examSelecionado?.id===exam.id?'text-white/40':'text-gray-300'" />
          </button>
        </div>
      </div>

      <!-- Painel principal -->
      <div class="main-panel">

        <div v-if="loadingResultados" class="flex flex-col gap-3">
          <div v-for="i in 4" :key="i" class="skel-card" :style="`--i:${i}`" />
        </div>

        <template v-else-if="resultados">
          <!-- KPIs -->
          <div class="kpi-grid">
            <div class="kpi-card">
              <div class="kpi-icon bg-blue-50"><Icon name="lucide:users" class="w-4 h-4 text-blue-500" /></div>
              <div><span class="kpi-value">{{ resultados.students?.length??0 }}</span><span class="kpi-label">Alunos</span></div>
            </div>
            <div class="kpi-card">
              <div class="kpi-icon bg-emerald-50"><Icon name="lucide:target" class="w-4 h-4 text-emerald-500" /></div>
              <div><span class="kpi-value">{{ mediaGeral.toFixed(1) }}</span><span class="kpi-label">Média geral</span></div>
            </div>
            <div class="kpi-card">
              <div class="kpi-icon bg-amber-50"><Icon name="lucide:check-circle" class="w-4 h-4 text-amber-500" /></div>
              <div><span class="kpi-value">{{ mediaAcertos }}%</span><span class="kpi-label">Taxa de acerto</span></div>
            </div>
          </div>

          <!-- Abas -->
          <div class="tabs">
            <button v-for="t in tabs" :key="t.id" class="tab" :class="activeTab===t.id?'tab--on':''" @click="activeTab=t.id">
              {{ t.label }}
            </button>
          </div>

          <!-- Ranking -->
          <template v-if="activeTab==='ranking'">
            <div class="card">
              <div class="card-header">
                <div class="card-title">Ranking — {{ resultados.class_name }}</div>
              </div>
              <ul class="ranking-list">
                <li v-for="(st, i) in resultados.students" :key="st.student_id" class="ranking-row">
                  <span class="rank-pos" :class="i===0?'rank-1':i===1?'rank-2':i===2?'rank-3':''">{{ i+1 }}</span>
                  <div class="rank-info">
                    <span class="rank-name">{{ st.student_name }}</span>
                    <span class="rank-ra">RA {{ st.ra }}</span>
                  </div>
                  <div class="rank-bar-wrap">
                    <div class="rank-bar">
                      <div class="rank-fill" :class="ratingColor(st.nota)" :style="`width:${(st.nota/10)*100}%`" />
                    </div>
                    <span class="rank-acertos">{{ st.acertos }}/{{ st.total }}</span>
                  </div>
                  <span class="rank-nota" :class="ratingColor(st.nota)">{{ st.nota?.toFixed(1) }}</span>
                </li>
              </ul>
            </div>
          </template>

          <!-- Por disciplina -->
          <template v-else-if="activeTab==='disciplinas' && resultados.by_discipline">
            <div class="card">
              <div class="card-header"><div class="card-title">Desempenho por disciplina</div></div>
              <div class="disc-list">
                <div v-for="d in resultados.by_discipline" :key="d.discipline_name" class="disc-row">
                  <span class="disc-name">{{ d.discipline_name }}</span>
                  <div class="disc-right">
                    <div class="prog-bar"><div class="prog-fill" :class="ratingColor(d.media)" :style="`width:${(d.media/10)*100}%`" /></div>
                    <span class="disc-nota" :class="ratingColor(d.media)">{{ d.media?.toFixed(1) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- Questão a questão -->
          <template v-else-if="activeTab==='questoes' && questaoStats">
            <div class="card">
              <div class="card-header"><div class="card-title">Taxa de acerto por questão</div></div>
              <div class="q-stats-list">
                <div v-for="q in questaoStats.questions" :key="q.order_idx" class="q-stat-row">
                  <span class="q-stat-num">#{{ q.order_idx }}</span>
                  <div class="q-stat-bar"><div class="prog-fill" :class="ratingColor(q.taxa_acerto/10)" :style="`width:${q.taxa_acerto}%`" /></div>
                  <span class="q-stat-pct" :class="taxaCor(q.taxa_acerto)">{{ q.taxa_acerto }}%</span>
                </div>
              </div>
            </div>
          </template>
        </template>

        <div v-else-if="examSelecionado" class="empty-state">
          <Icon name="lucide:inbox" class="w-10 h-10 text-gray-200" />
          <p>Nenhum resultado disponível para esta turma</p>
        </div>

        <div v-else class="empty-state">
          <Icon name="lucide:bar-chart-2" class="w-10 h-10 text-gray-200" />
          <p>Selecione um simulado para ver os resultados</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const mounted = ref(false)

const exams           = ref<any[]>([])
const myAssignments   = ref<Record<number,any>>({})
const resultados      = ref<any>(null)
const questaoStats    = ref<any>(null)
const examSelecionado = ref<any>(null)
const loadingExams    = ref(true)
const loadingResultados = ref(false)
const activeTab       = ref('ranking')

const tabs = [
  { id:'ranking',     label:'Ranking' },
  { id:'disciplinas', label:'Por disciplina' },
  { id:'questoes',    label:'Por questão' },
]

const examsDisponiveis = computed(() =>
  exams.value.filter(e => ['generated','published'].includes(e.status))
)

const mediaGeral = computed(() => {
  const students = resultados.value?.students??[]
  if (!students.length) return 0
  return students.reduce((s:number,st:any)=>s+(st.nota??0),0) / students.length
})
const mediaAcertos = computed(() => {
  const students = resultados.value?.students??[]
  if (!students.length) return 0
  const total = students.reduce((s:number,st:any)=>s+(st.total??0),0)
  const acertos = students.reduce((s:number,st:any)=>s+(st.acertos??0),0)
  return total>0 ? Math.round(acertos/total*100) : 0
})

function statusDot(s: string) { return ({collecting:'dot-amber',review:'dot-purple',locked:'dot-blue',generated:'dot-indigo',published:'dot-emerald'}as any)[s]??'dot-gray' }
function ratingColor(nota: number) { return nota>=7?'text-emerald-600':nota>=5?'text-amber-600':'text-red-500' }
function taxaCor(pct: number) { return pct>=70?'text-emerald-600':pct>=50?'text-amber-600':'text-red-500' }

async function selecionarExam(exam: any) {
  examSelecionado.value=exam; resultados.value=null; questaoStats.value=null; activeTab.value='ranking'; loadingResultados.value=true
  try {
    const assignment = myAssignments.value[exam.id]
    if (assignment) {
      const [rRes, qRes] = await Promise.allSettled([
        get<any>(`/exams/${exam.id}/results?class_id=${assignment.class_id}`),
        get<any>(`/exams/${exam.id}/results/questions?class_id=${assignment.class_id}`),
      ])
      if (rRes.status==='fulfilled') resultados.value = rRes.value
      if (qRes.status==='fulfilled') questaoStats.value = qRes.value
    }
  } catch {} finally { loadingResultados.value=false }
}

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  const examList = await get<any[]>('/exams/').catch(()=>[])
  exams.value = examList
  const results = await Promise.allSettled(examList.map(e=>get<any>(`/exams/${e.id}/my-assignment`).catch(()=>null)))
  examList.forEach((e,i)=>{ if (results[i].status==='fulfilled'&&results[i].value) myAssignments.value[e.id]=results[i].value })
  loadingExams.value=false
  // Seleciona automaticamente o primeiro disponível
  if (examsDisponiveis.value.length) selecionarExam(examsDisponiveis.value[0])
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; }
.page-title { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub   { font-size:.8rem; color:#9ca3af; margin:0; }
.skel-card  { background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s infinite; animation-delay:calc(var(--i,0)*70ms); height:4rem; }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.empty-sub { font-size:.72rem; color:#d1d5db; }
.content-grid { display:grid; grid-template-columns:1fr; gap:1rem; }
@media(min-width:1024px) { .content-grid { grid-template-columns:240px 1fr; } }
.sidebar { display:flex; flex-direction:column; gap:.625rem; }
.section-label { font-size:.65rem; font-weight:800; text-transform:uppercase; letter-spacing:.1em; color:#9ca3af; padding:0 .25rem; }
.exam-list { display:flex; flex-direction:column; gap:.375rem; }
.exam-btn { display:flex; align-items:center; gap:.75rem; padding:.75rem 1rem; border-radius:.875rem; border:1.5px solid #e5e7eb; background:white; cursor:pointer; text-align:left; transition:all .13s; }
.exam-btn:hover { border-color:#d1d5db; }
.exam-btn--on { background:#111827; border-color:#111827; }
.exam-btn-dot { width:.45rem; height:.45rem; border-radius:50%; flex-shrink:0; }
.dot-amber   { background:#fbbf24; } .dot-purple  { background:#a78bfa; } .dot-blue    { background:#60a5fa; }
.dot-indigo  { background:#818cf8; } .dot-emerald { background:#34d399; } .dot-gray    { background:#9ca3af; }
.exam-btn-info { flex:1; min-width:0; }
.exam-btn-title { display:block; font-size:.78rem; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.exam-btn--on .exam-btn-title { color:white; }
.exam-btn:not(.exam-btn--on) .exam-btn-title { color:#111827; }
.exam-btn-meta { display:block; font-size:.65rem; margin-top:.1rem; }
.exam-btn--on .exam-btn-meta { color:rgba(255,255,255,.5); }
.exam-btn:not(.exam-btn--on) .exam-btn-meta { color:#9ca3af; }
.main-panel { display:flex; flex-direction:column; gap:.875rem; }
.kpi-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.625rem; }
.kpi-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:.875rem; display:flex; align-items:center; gap:.75rem; }
.kpi-icon  { width:2rem; height:2rem; border-radius:.5rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.kpi-value { display:block; font-size:1.35rem; font-weight:800; color:#111827; line-height:1; }
.kpi-label { display:block; font-size:.65rem; color:#9ca3af; margin-top:.15rem; }
.tabs { display:flex; gap:.25rem; background:#f3f4f6; padding:.25rem; border-radius:.875rem; width:fit-content; }
.tab  { padding:.4rem .875rem; border-radius:.625rem; font-size:.75rem; font-weight:700; cursor:pointer; border:none; background:none; color:#6b7280; transition:all .15s; }
.tab--on { background:white; color:#111827; box-shadow:0 1px 3px rgba(0,0,0,.06); }
.card { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; }
.card-header { display:flex; align-items:center; justify-content:space-between; padding:.875rem 1.25rem; border-bottom:1px solid #f9fafb; }
.card-title  { font-size:.8rem; font-weight:700; color:#111827; }
.ranking-list { list-style:none; margin:0; padding:0; }
.ranking-row  { display:flex; align-items:center; gap:.875rem; padding:.75rem 1.25rem; border-bottom:1px solid #f9fafb; }
.ranking-row:last-child { border-bottom:none; }
.rank-pos  { width:1.75rem; height:1.75rem; border-radius:9999px; background:#f3f4f6; font-size:.72rem; font-weight:800; color:#6b7280; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.rank-1 { background:#fef3c7; color:#92400e; }
.rank-2 { background:#f3f4f6; color:#374151; }
.rank-3 { background:#fef9c3; color:#713f12; }
.rank-info { width:9rem; flex-shrink:0; }
.rank-name { display:block; font-size:.8rem; font-weight:700; color:#374151; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rank-ra   { display:block; font-size:.68rem; color:#9ca3af; }
.rank-bar-wrap { flex:1; display:flex; align-items:center; gap:.625rem; }
.rank-bar  { flex:1; height:.35rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.rank-fill { height:100%; border-radius:9999px; transition:width .6s ease; }
.rank-acertos { font-size:.68rem; color:#9ca3af; flex-shrink:0; }
.rank-nota { font-size:.9rem; font-weight:800; flex-shrink:0; width:2.5rem; text-align:right; }
.disc-list { display:flex; flex-direction:column; }
.disc-row  { display:flex; align-items:center; gap:.875rem; padding:.75rem 1.25rem; border-bottom:1px solid #f9fafb; }
.disc-row:last-child { border-bottom:none; }
.disc-name  { font-size:.8rem; font-weight:600; color:#374151; min-width:8rem; }
.disc-right { display:flex; align-items:center; gap:.625rem; flex:1; }
.prog-bar   { flex:1; height:.35rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.prog-fill  { height:100%; border-radius:9999px; transition:width .6s ease; }
.disc-nota  { font-size:.8rem; font-weight:800; min-width:2rem; text-align:right; }
.q-stats-list { display:flex; flex-direction:column; }
.q-stat-row  { display:flex; align-items:center; gap:.875rem; padding:.625rem 1.25rem; border-bottom:1px solid #f9fafb; }
.q-stat-row:last-child { border-bottom:none; }
.q-stat-num { font-size:.72rem; font-weight:700; color:#9ca3af; width:2rem; flex-shrink:0; }
.q-stat-bar { flex:1; height:.35rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.q-stat-pct { font-size:.75rem; font-weight:800; width:2.5rem; text-align:right; flex-shrink:0; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
</style>