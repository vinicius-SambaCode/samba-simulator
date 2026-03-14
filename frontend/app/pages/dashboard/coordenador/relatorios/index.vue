<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Relatórios</h1>
        <p class="page-sub">Progresso de coleta e resultados dos simulados</p>
      </div>
    </div>

    <!-- Seletor de simulado -->
    <div class="fade-in" :class="{ ready: mounted }" style="--d:.05s">
      <div v-if="loadingExams" class="flex gap-2">
        <div v-for="i in 3" :key="i" class="skel-pill" :style="`--i:${i}`" />
      </div>
      <div v-else class="exam-tabs">
        <button v-for="exam in exams" :key="exam.id"
          class="exam-tab" :class="selectedExamId===exam.id?'exam-tab--on':''"
          @click="selectExam(exam.id)">
          <span class="exam-dot" :class="statusDot(exam.status)" />
          {{ exam.title }}
        </button>
      </div>
    </div>

    <div v-if="!selectedExamId" class="empty-state fade-in" :class="{ ready: mounted }" style="--d:.08s">
      <Icon name="lucide:bar-chart-2" class="w-10 h-10 text-gray-200" />
      <p>Selecione um simulado para ver os relatórios</p>
    </div>

    <template v-else>

      <div class="tabs fade-in" :class="{ ready: mounted }" style="--d:.08s">
        <button v-for="t in tabs" :key="t.id" class="tab" :class="activeTab===t.id?'tab-active':''" @click="activeTab=t.id">
          {{ t.label }}
        </button>
      </div>

      <!-- PROGRESSO -->
      <template v-if="activeTab==='progresso'">
        <div v-if="loadingProgress" class="grid-3 fade-in" :class="{ ready: mounted }" style="--d:.1s">
          <div v-for="i in 3" :key="i" class="skel-kpi" :style="`--i:${i}`" />
        </div>
        <template v-else-if="progress">
          <div class="grid-3 fade-in" :class="{ ready: mounted }" style="--d:.1s">
            <div v-for="k in progressKpis" :key="k.label" class="kpi-card">
              <div class="kpi-icon" :class="k.iconBg"><Icon :name="k.icon" class="w-4 h-4" :class="k.iconColor" /></div>
              <div><p class="kpi-value">{{ k.value }}</p><p class="kpi-label">{{ k.label }}</p></div>
            </div>
          </div>
          <div class="card fade-in" :class="{ ready: mounted }" style="--d:.14s">
            <div class="card-header">
              <div class="card-title"><Icon name="lucide:briefcase" class="w-4 h-4 text-gray-400" /> Por professor</div>
            </div>
            <div v-if="!byTeacher.length" class="card-empty"><p>Nenhum professor atribuído</p></div>
            <div v-else class="teacher-list">
              <div v-for="t in byTeacher" :key="`${t.teacher_id}_${t.class_id}`" class="teacher-row">
                <div class="teacher-info">
                  <span class="teacher-name">{{ t.teacher_name }}</span>
                  <span class="teacher-meta">{{ t.discipline_name }} · {{ t.class_name }}</span>
                </div>
                <div class="teacher-prog">
                  <div class="prog-bar">
                    <div class="prog-fill" :class="t.status==='COMPLETE'?'bg-emerald-400':'bg-blue-400'"
                      :style="`width:${t.quota>0?Math.min(100,t.submitted/t.quota*100):0}%`" />
                  </div>
                  <span class="prog-text">{{ t.submitted }}/{{ t.quota }}</span>
                  <span class="status-dot-sm"
                    :class="t.status==='COMPLETE'?'bg-emerald-400':t.status==='PARTIAL'?'bg-amber-400':'bg-gray-300'" />
                </div>
              </div>
            </div>
          </div>
        </template>
      </template>

      <!-- RESULTADOS -->
      <template v-if="activeTab==='resultados'">
        <div class="results-layout fade-in" :class="{ ready: mounted }" style="--d:.1s">
          <div class="card">
            <div class="card-header"><div class="card-title"><Icon name="lucide:users" class="w-4 h-4 text-gray-400" /> Turmas</div></div>
            <div v-if="loadingClasses" class="card-loading">
              <div v-for="i in 3" :key="i" class="skel-row" :style="`--i:${i}`" />
            </div>
            <ul v-else class="class-list">
              <li v-for="cls in examClasses" :key="cls.class_id">
                <button class="class-btn" :class="selectedClassId===cls.class_id?'class-btn--on':''" @click="selectClass(cls.class_id)">
                  <Icon name="lucide:users" class="w-3.5 h-3.5" /> {{ cls.class_name }}
                </button>
              </li>
            </ul>
          </div>
          <div class="results-panel">
            <div v-if="!selectedClassId" class="card card-empty-full">
              <Icon name="lucide:mouse-pointer" class="w-8 h-8 text-gray-200" /><p>Selecione uma turma</p>
            </div>
            <div v-else-if="loadingResultados" class="card card-loading">
              <div v-for="i in 5" :key="i" class="skel-row" :style="`--i:${i}`" />
            </div>
            <template v-else-if="resultados">
              <div class="grid-3">
                <div v-for="k in resultadoKpis" :key="k.label" class="kpi-card">
                  <div class="kpi-icon" :class="k.iconBg"><Icon :name="k.icon" class="w-4 h-4" :class="k.iconColor" /></div>
                  <div><p class="kpi-value">{{ k.value }}</p><p class="kpi-label">{{ k.label }}</p></div>
                </div>
              </div>
              <div class="card">
                <div class="card-header">
                  <div class="card-title"><Icon name="lucide:trophy" class="w-4 h-4 text-amber-400" /> Ranking</div>
                  <button class="btn-sm-outline" :disabled="downloadingXlsx" @click="exportXlsx">
                    <Icon name="lucide:download" class="w-3.5 h-3.5" /> XLSX
                  </button>
                </div>
                <ul class="ranking-list">
                  <li v-for="(student, i) in resultados.students" :key="student.student_id" class="ranking-row">
                    <span class="rank-pos" :class="i===0?'rank-1':i===1?'rank-2':i===2?'rank-3':''">{{ i+1 }}</span>
                    <span class="rank-name">{{ student.student_name }}</span>
                    <span class="rank-score" :class="student.nota>=7?'text-emerald-600':student.nota>=5?'text-amber-600':'text-red-500'">
                      {{ student.nota?.toFixed(1) }}
                    </span>
                    <span class="rank-hits">{{ student.acertos }}/{{ resultados.total_questoes }}</span>
                  </li>
                </ul>
              </div>
            </template>
          </div>
        </div>
      </template>

      <!-- DEVOLUTIVA -->
      <template v-if="activeTab==='devolutiva'">
        <div class="card fade-in" :class="{ ready: mounted }" style="--d:.1s">
          <div class="card-header"><div class="card-title"><Icon name="lucide:file-text" class="w-4 h-4 text-gray-400" /> Relatório individual</div></div>
          <div class="devol-section">
            <div class="field-row">
              <select v-model="devolvClass" class="filter-select" @change="loadStudentsForDevol">
                <option value="">Selecione a turma...</option>
                <option v-for="cls in examClasses" :key="cls.class_id" :value="cls.class_id">{{ cls.class_name }}</option>
              </select>
              <select v-if="devolvStudents.length" v-model="devolvStudent" class="filter-select">
                <option value="">Selecione o aluno...</option>
                <option v-for="s in devolvStudents" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <button class="btn-primary" :disabled="!devolvStudent||downloadingReport" @click="exportReport">
                <Icon name="lucide:file-down" class="w-4 h-4" />
                {{ downloadingReport ? 'Gerando...' : 'Baixar PDF' }}
              </button>
            </div>
            <p v-if="exportError" class="error-msg">{{ exportError }}</p>
          </div>
        </div>
      </template>

    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()
const BASE_URL = useRuntimeConfig().public.apiBase as string
const mounted   = ref(false)
const activeTab = ref('progresso')
const tabs = [
  { id:'progresso',  label:'Progresso de coleta'  },
  { id:'resultados', label:'Resultados'            },
  { id:'devolutiva', label:'Devolutiva individual' },
]

const exams            = ref<any[]>([])
const examClasses      = ref<any[]>([])
const progress         = ref<any>(null)
const byTeacher        = ref<any[]>([])
const resultados       = ref<any>(null)
const devolvStudents   = ref<any[]>([])
const loadingExams     = ref(true)
const loadingProgress  = ref(false)
const loadingClasses   = ref(false)
const loadingResultados= ref(false)
const selectedExamId   = ref<number|null>(null)
const selectedClassId  = ref<number|null>(null)
const devolvClass      = ref<number|''>('')
const devolvStudent    = ref<number|''>('')
const downloadingXlsx  = ref(false)
const downloadingReport= ref(false)
const exportError      = ref('')

function statusDot(s: string) {
  return ({collecting:'bg-amber-400',review:'bg-purple-400',locked:'bg-blue-400',generated:'bg-indigo-400',published:'bg-emerald-400'}as any)[s]??'bg-gray-300'
}

const progressKpis = computed(() => {
  if (!progress.value) return []
  const discs = progress.value.disciplines ?? []
  const totalQ = discs.reduce((s:number,d:any)=>s+d.quota,0)
  const doneQ  = discs.reduce((s:number,d:any)=>s+Math.min(d.submitted,d.quota),0)
  return [
    { label:'Total esperado', value:totalQ,     icon:'lucide:target',    iconBg:'bg-blue-50',   iconColor:'text-blue-500'   },
    { label:'Enviadas',       value:doneQ,       icon:'lucide:check',     iconBg:'bg-emerald-50',iconColor:'text-emerald-500' },
    { label:'Disciplinas',    value:discs.length,icon:'lucide:book-open', iconBg:'bg-violet-50', iconColor:'text-violet-500'  },
  ]
})

const resultadoKpis = computed(() => {
  if (!resultados.value) return []
  const students = resultados.value.students ?? []
  const avg = students.length ? students.reduce((s:number,st:any)=>s+(st.nota??0),0)/students.length : 0
  return [
    { label:'Alunos',         value:students.length, icon:'lucide:users',       iconBg:'bg-blue-50',  iconColor:'text-blue-500'  },
    { label:'Média da turma', value:avg.toFixed(1),  icon:'lucide:bar-chart-2', iconBg:'bg-amber-50', iconColor:'text-amber-500' },
    { label:'Questões',       value:resultados.value.total_questoes??0, icon:'lucide:help-circle', iconBg:'bg-gray-50', iconColor:'text-gray-500' },
  ]
})

async function selectExam(id: number) {
  selectedExamId.value=id; selectedClassId.value=null; resultados.value=null; progress.value=null; byTeacher.value=[]
  loadingProgress.value=true; loadingClasses.value=true
  const [pRes,btRes,clsRes] = await Promise.allSettled([
    get<any>(`/exams/${id}/progress`),
    get<any>(`/exams/${id}/dashboard/by-teacher`),
    get<any[]>(`/exams/${id}/classes`),
  ])
  if (pRes.status==='fulfilled')   progress.value    = pRes.value
  if (btRes.status==='fulfilled') {
    const bt = btRes.value as any
    // flatten: backend retorna lista de professores com sub-items por turma/disc
    const flat: any[] = []
    for (const t of (bt.teachers ?? bt ?? [])) {
      for (const item of (t.assignments ?? [t])) {
        flat.push({ teacher_id:t.teacher_id, teacher_name:t.teacher_name, ...item })
      }
    }
    byTeacher.value = flat.length ? flat : (bt.teachers ?? bt ?? [])
  }
  if (clsRes.status==='fulfilled') examClasses.value = clsRes.value
  loadingProgress.value=false; loadingClasses.value=false
}

async function selectClass(classId: number) {
  selectedClassId.value=classId; resultados.value=null; loadingResultados.value=true
  try { resultados.value=await get<any>(`/exams/${selectedExamId.value}/results?class_id=${classId}`) }
  catch { resultados.value=null } finally { loadingResultados.value=false }
}

async function loadStudentsForDevol() {
  if (!devolvClass.value) { devolvStudents.value=[]; return }
  devolvStudents.value=await get<any[]>(`/school/students?class_id=${devolvClass.value}`).catch(()=>[])
}

async function _fetchBlob(path: string): Promise<Blob> {
  const token = import.meta.client ? localStorage.getItem('samba_token') : null
  const res = await fetch(`${BASE_URL}${path}`, { headers:token?{Authorization:`Bearer ${token}`}:{}, credentials:'include' })
  if (!res.ok) throw new Error(`Erro ${res.status}`)
  return res.blob()
}
async function _triggerDownload(blob: Blob, filename: string) {
  const url=URL.createObjectURL(blob); const a=document.createElement('a')
  a.href=url; a.download=filename; document.body.appendChild(a); a.click()
  document.body.removeChild(a); setTimeout(()=>URL.revokeObjectURL(url),1000)
}
async function exportXlsx() {
  if (!selectedClassId.value) return
  downloadingXlsx.value=true; exportError.value=''
  try { const blob=await _fetchBlob(`/exams/${selectedExamId.value}/results/export?class_id=${selectedClassId.value}`); _triggerDownload(blob,`resultados_exam${selectedExamId.value}.xlsx`) }
  catch (e:any) { exportError.value=e?.message??'Erro ao exportar.' } finally { downloadingXlsx.value=false }
}
async function exportReport() {
  if (!devolvStudent.value) return
  downloadingReport.value=true; exportError.value=''
  try { const blob=await _fetchBlob(`/exams/${selectedExamId.value}/results/report/${devolvStudent.value}`); _triggerDownload(blob,`devolutiva_aluno${devolvStudent.value}.pdf`) }
  catch (e:any) { exportError.value=e?.message??'Erro ao gerar.' } finally { downloadingReport.value=false }
}

onMounted(async () => {
  await nextTick(); setTimeout(()=>{mounted.value=true},30)
  try { exams.value=await get<any[]>('/exams/') } catch { exams.value=[] } finally { loadingExams.value=false }
})
</script>

<style scoped>
.page { display:flex; flex-direction:column; gap:1.25rem; padding-bottom:2rem; }
.fade-in { opacity:0; transform:translateY(10px); transition:opacity .35s ease var(--d,.0s), transform .35s ease var(--d,.0s); }
.fade-in.ready { opacity:1; transform:translateY(0); }
.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
.page-title  { font-size:1.35rem; font-weight:800; color:#111827; margin:0 0 .2rem; }
.page-sub    { font-size:.8rem; color:#9ca3af; margin:0; }
.skel-pill   { height:2.25rem; width:8rem; background:white; border:1px solid #f3f4f6; border-radius:9999px; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*80ms); }
.exam-tabs   { display:flex; gap:.4rem; flex-wrap:wrap; }
.exam-tab    { display:inline-flex; align-items:center; gap:.5rem; padding:.4rem .875rem; border-radius:9999px; font-size:.75rem; font-weight:700; border:1.5px solid #e5e7eb; background:white; color:#6b7280; cursor:pointer; transition:all .13s; }
.exam-tab:hover { border-color:#d1d5db; }
.exam-tab--on   { border-color:#111827; background:#111827; color:white; }
.exam-dot    { width:.4rem; height:.4rem; border-radius:50%; }
.empty-state { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:4rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; text-align:center; }
.empty-state p { font-size:.8rem; color:#9ca3af; margin:0; }
.tabs { display:flex; gap:.25rem; background:#f3f4f6; padding:.25rem; border-radius:.875rem; width:fit-content; }
.tab { padding:.4rem 1rem; border-radius:.625rem; font-size:.78rem; font-weight:700; border:none; background:none; cursor:pointer; color:#6b7280; transition:all .13s; }
.tab-active { background:white; color:#111827; box-shadow:0 1px 4px rgba(0,0,0,.06); }
.grid-3 { display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:.75rem; }
.kpi-card  { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem; display:flex; align-items:center; gap:.875rem; animation:card-in .35s ease both; }
@keyframes card-in { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.kpi-icon  { width:2.25rem; height:2.25rem; border-radius:.625rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.kpi-value { font-size:1.5rem; font-weight:800; color:#111827; line-height:1; }
.kpi-label { font-size:.68rem; color:#9ca3af; margin-top:.15rem; }
.skel-kpi  { height:5.5rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*80ms); }
.card { background:white; border:1px solid #f3f4f6; border-radius:1rem; overflow:hidden; }
.card-header { display:flex; align-items:center; justify-content:space-between; padding:.875rem 1.25rem; border-bottom:1px solid #f9fafb; }
.card-title  { display:flex; align-items:center; gap:.5rem; font-size:.8rem; font-weight:700; color:#111827; }
.card-loading { padding:.75rem 1rem; display:flex; flex-direction:column; gap:.5rem; }
.skel-row { height:2.75rem; background:#f9fafb; border-radius:.625rem; animation:shimmer 1.5s ease-in-out infinite; animation-delay:calc(var(--i,0)*100ms); }
.card-empty { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:2.5rem 1rem; }
.card-empty p { font-size:.78rem; color:#9ca3af; margin:0; }
.card-empty-full { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:4rem 1rem; gap:.5rem; }
.teacher-list { display:flex; flex-direction:column; }
.teacher-row  { display:flex; align-items:center; gap:1rem; padding:.75rem 1.25rem; border-bottom:1px solid #f9fafb; }
.teacher-row:last-child { border-bottom:none; }
.teacher-info { flex:1; min-width:0; }
.teacher-name { display:block; font-size:.8rem; font-weight:700; color:#374151; }
.teacher-meta { display:block; font-size:.68rem; color:#9ca3af; }
.teacher-prog { display:flex; align-items:center; gap:.5rem; flex-shrink:0; min-width:10rem; }
.prog-bar     { flex:1; height:.25rem; background:#f3f4f6; border-radius:9999px; overflow:hidden; }
.prog-fill    { height:100%; border-radius:9999px; transition:width .7s ease; }
.prog-text    { font-size:.68rem; color:#9ca3af; white-space:nowrap; }
.status-dot-sm { width:.5rem; height:.5rem; border-radius:50%; flex-shrink:0; }
.results-layout { display:grid; grid-template-columns:1fr; gap:.75rem; }
@media(min-width:768px) { .results-layout { grid-template-columns:200px 1fr; align-items:start; } }
.results-panel { display:flex; flex-direction:column; gap:.75rem; }
.class-list { list-style:none; margin:0; padding:.5rem; }
.class-btn  { width:100%; display:flex; align-items:center; gap:.625rem; padding:.6rem .875rem; border-radius:.625rem; font-size:.78rem; font-weight:600; color:#374151; background:none; border:none; cursor:pointer; transition:all .13s; }
.class-btn:hover { background:#f9fafb; }
.class-btn--on   { background:#111827; color:white; }
.ranking-list { list-style:none; margin:0; padding:0; }
.ranking-row  { display:flex; align-items:center; gap:.875rem; padding:.625rem 1.25rem; border-bottom:1px solid #f9fafb; }
.ranking-row:last-child { border-bottom:none; }
.rank-pos  { width:1.5rem; font-size:.75rem; font-weight:800; color:#9ca3af; flex-shrink:0; text-align:center; }
.rank-1 { color:#f59e0b; } .rank-2 { color:#94a3b8; } .rank-3 { color:#b45309; }
.rank-name  { flex:1; font-size:.8rem; font-weight:600; color:#374151; }
.rank-score { font-size:.875rem; font-weight:800; }
.rank-hits  { font-size:.68rem; color:#9ca3af; flex-shrink:0; }
.devol-section { padding:1.25rem; }
.field-row  { display:flex; gap:.5rem; flex-wrap:wrap; align-items:flex-end; }
.filter-select { padding:.5rem .75rem; border:1px solid #e5e7eb; border-radius:.625rem; font-size:.8rem; color:#374151; background:white; outline:none; }
.btn-primary,.btn-sm-outline { display:inline-flex; align-items:center; gap:.4rem; padding:.5rem .875rem; font-size:.75rem; font-weight:700; border-radius:.625rem; cursor:pointer; white-space:nowrap; transition:all .13s; border:none; }
.btn-primary { background:#111827; color:white; } .btn-primary:hover:not(:disabled) { background:#1f2937; } .btn-primary:disabled { opacity:.5; cursor:not-allowed; }
.btn-sm-outline { background:white; color:#374151; border:1px solid #e5e7eb; } .btn-sm-outline:hover:not(:disabled) { background:#f9fafb; } .btn-sm-outline:disabled { opacity:.5; cursor:not-allowed; }
.error-msg { font-size:.72rem; color:#ef4444; font-weight:600; margin-top:.5rem; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
</style>