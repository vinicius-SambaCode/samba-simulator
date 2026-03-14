<template>
  <div class="page">

    <div class="page-header fade-in" :class="{ ready: mounted }">
      <div>
        <h1 class="page-title">Painel Root</h1>
        <p class="page-sub">Acesso total ao sistema — EE Prof. Christino Cabral</p>
      </div>
      <span class="root-badge">
        <Icon name="lucide:shield" class="w-3.5 h-3.5" /> Administrador
      </span>
    </div>

    <!-- KPIs -->
    <div class="kpi-grid fade-in" :class="{ ready: mounted }" style="--d:.06s">
      <div v-for="k in kpis" :key="k.label" class="kpi-card">
        <div class="kpi-icon" :class="k.iconBg">
          <Icon :name="k.icon" class="w-4 h-4" :class="k.iconColor" />
        </div>
        <div>
          <div v-if="loading" class="skel-val" />
          <p v-else class="kpi-val">{{ k.value }}</p>
          <p class="kpi-label">{{ k.label }}</p>
        </div>
      </div>
    </div>

    <!-- Acesso rápido a todas as áreas -->
    <div class="section-title fade-in" :class="{ ready: mounted }" style="--d:.1s">Acesso rápido</div>

    <div class="shortcuts-grid fade-in" :class="{ ready: mounted }" style="--d:.12s">
      <NuxtLink v-for="s in shortcuts" :key="s.to" :to="s.to" class="shortcut-card">
        <div class="shortcut-icon" :class="s.iconBg">
          <Icon :name="s.icon" class="w-5 h-5" :class="s.iconColor" />
        </div>
        <div class="shortcut-info">
          <p class="shortcut-label">{{ s.label }}</p>
          <p class="shortcut-sub">{{ s.sub }}</p>
        </div>
        <Icon name="lucide:arrow-right" class="shortcut-arrow" />
      </NuxtLink>
    </div>

    <!-- Simulados recentes -->
    <div class="section-title fade-in" :class="{ ready: mounted }" style="--d:.16s">Simulados recentes</div>
    <div v-if="loading" class="list fade-in" :class="{ ready: mounted }" style="--d:.18s">
      <div v-for="i in 3" :key="i" class="skel-row" :style="`--i:${i}`" />
    </div>
    <div v-else-if="!exams.length" class="empty-card fade-in" :class="{ ready: mounted }" style="--d:.18s">
      <Icon name="lucide:file-text" class="w-8 h-8 text-gray-200" />
      <p>Nenhum simulado cadastrado</p>
    </div>
    <div v-else class="list fade-in" :class="{ ready: mounted }" style="--d:.18s">
      <NuxtLink v-for="e in exams.slice(0,5)" :key="e.id"
        :to="`/dashboard/coordenador/simulados/${e.id}`"
        class="exam-row">
        <span class="status-badge" :class="statusBadge(e.status)">{{ statusLabel(e.status) }}</span>
        <span class="exam-title">{{ e.title }}</span>
        <Icon name="lucide:arrow-right" class="exam-arrow" />
      </NuxtLink>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()
const mounted = ref(false)
const loading  = ref(true)

const totalUsers    = ref(0)
const totalClasses  = ref(0)
const totalStudents = ref(0)
const exams         = ref<any[]>([])

const kpis = computed(() => [
  { label:'Usuários',  value:totalUsers.value,    icon:'lucide:users',      iconBg:'bg-violet-50', iconColor:'text-violet-500' },
  { label:'Turmas',    value:totalClasses.value,  icon:'lucide:school',     iconBg:'bg-blue-50',   iconColor:'text-blue-500'   },
  { label:'Alunos',    value:totalStudents.value, icon:'lucide:graduation-cap',iconBg:'bg-emerald-50',iconColor:'text-emerald-500'},
  { label:'Simulados', value:exams.value.length,  icon:'lucide:file-text',  iconBg:'bg-amber-50',  iconColor:'text-amber-500'  },
])

const shortcuts = [
  { to:'/dashboard/coordenador/turmas',       label:'Turmas',        sub:'Gerenciar turmas e alunos',         icon:'lucide:users',          iconBg:'bg-blue-50',   iconColor:'text-blue-500'   },
  { to:'/dashboard/coordenador/simulados',    label:'Simulados',     sub:'Criar e acompanhar simulados',      icon:'lucide:file-text',      iconBg:'bg-indigo-50', iconColor:'text-indigo-500' },
  { to:'/dashboard/coordenador/professores',  label:'Professores',   sub:'Cadastro e vínculos',               icon:'lucide:user-check',     iconBg:'bg-emerald-50',iconColor:'text-emerald-500'},
  { to:'/dashboard/coordenador/disciplinas',  label:'Disciplinas',   sub:'Matriz curricular',                 icon:'lucide:book-open',      iconBg:'bg-teal-50',   iconColor:'text-teal-500'   },
  { to:'/dashboard/coordenador/questoes',     label:'Questões',      sub:'Banco de questões',                 icon:'lucide:help-circle',    iconBg:'bg-amber-50',  iconColor:'text-amber-500'  },
  { to:'/dashboard/coordenador/relatorios',   label:'Relatórios',    sub:'Resultados e progresso',            icon:'lucide:bar-chart-2',    iconBg:'bg-rose-50',   iconColor:'text-rose-500'   },
]

function statusLabel(s: string) { return ({collecting:'Em coleta',review:'Em revisão',locked:'Travado',generated:'Gerado',published:'Publicado',draft:'Rascunho'} as any)[s]??s }
function statusBadge(s: string) { return ({collecting:'sb-amber',review:'sb-purple',locked:'sb-blue',generated:'sb-indigo',published:'sb-emerald',draft:'sb-gray'} as any)[s]??'sb-gray' }

onMounted(async () => {
  await nextTick(); setTimeout(() => { mounted.value = true }, 30)
  const [usersRes, classesRes, studentsRes, examsRes] = await Promise.allSettled([
    get<any[]>('/school/teachers').then(r => r.length),
    get<any[]>('/school/classes').then(r => r.length),
    get<any[]>('/school/students/').then(r => r.length),
    get<any[]>('/exams/'),
  ])
  if (usersRes.status==='fulfilled')   totalUsers.value    = usersRes.value as number
  if (classesRes.status==='fulfilled') totalClasses.value  = classesRes.value as number
  if (studentsRes.status==='fulfilled')totalStudents.value = studentsRes.value as number
  if (examsRes.status==='fulfilled')   exams.value         = examsRes.value as any[]
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
.root-badge  { display:inline-flex; align-items:center; gap:.4rem; padding:.35rem .875rem; background:#f3e8ff; border:1px solid #e9d5ff; border-radius:9999px; font-size:.72rem; font-weight:700; color:#7c3aed; flex-shrink:0; }
.kpi-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:.75rem; }
@media(min-width:640px) { .kpi-grid { grid-template-columns:repeat(4,1fr); } }
.kpi-card { background:white; border:1px solid #f3f4f6; border-radius:1rem; padding:1rem; display:flex; align-items:center; gap:.875rem; }
.kpi-icon  { width:2.25rem; height:2.25rem; border-radius:.625rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.kpi-val   { font-size:1.5rem; font-weight:800; color:#111827; line-height:1; }
.kpi-label { font-size:.68rem; color:#9ca3af; margin-top:.2rem; }
.skel-val  { width:3rem; height:1.5rem; background:#f3f4f6; border-radius:.375rem; animation:shimmer 1.5s infinite; margin-bottom:.2rem; }
.section-title { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:#9ca3af; }
.shortcuts-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:.625rem; }
.shortcut-card { display:flex; align-items:center; gap:.875rem; padding:.875rem 1rem; background:white; border:1px solid #f3f4f6; border-radius:1rem; text-decoration:none; transition:all .13s; }
.shortcut-card:hover { border-color:#e5e7eb; box-shadow:0 2px 8px rgba(0,0,0,.05); transform:translateY(-1px); }
.shortcut-icon { width:2.5rem; height:2.5rem; border-radius:.75rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.shortcut-info { flex:1; min-width:0; }
.shortcut-label { font-size:.8rem; font-weight:700; color:#111827; }
.shortcut-sub   { font-size:.68rem; color:#9ca3af; margin-top:.1rem; }
.shortcut-arrow { width:.875rem; height:.875rem; color:#d1d5db; flex-shrink:0; transition:transform .13s, color .13s; }
.shortcut-card:hover .shortcut-arrow { color:#9ca3af; transform:translateX(2px); }
.list { display:flex; flex-direction:column; gap:.5rem; }
.skel-row { height:3rem; background:white; border:1px solid #f3f4f6; border-radius:.875rem; animation:shimmer 1.5s infinite; animation-delay:calc(var(--i,0)*80ms); }
.empty-card { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:3rem 1rem; background:white; border:2px dashed #f3f4f6; border-radius:1rem; }
.empty-card p { font-size:.8rem; color:#9ca3af; margin:0; }
.exam-row { display:flex; align-items:center; gap:.75rem; padding:.75rem 1rem; background:white; border:1px solid #f3f4f6; border-radius:.875rem; text-decoration:none; transition:all .13s; }
.exam-row:hover { border-color:#e5e7eb; transform:translateX(2px); }
.exam-title { flex:1; font-size:.8rem; font-weight:600; color:#374151; }
.exam-arrow { width:.875rem; height:.875rem; color:#d1d5db; }
.status-badge { font-size:.62rem; font-weight:700; padding:.15rem .45rem; border-radius:9999px; flex-shrink:0; }
.sb-amber   { background:#fef3c7; color:#92400e; }
.sb-purple  { background:#ede9fe; color:#5b21b6; }
.sb-blue    { background:#dbeafe; color:#1e40af; }
.sb-indigo  { background:#e0e7ff; color:#3730a3; }
.sb-emerald { background:#d1fae5; color:#065f46; }
.sb-gray    { background:#f3f4f6; color:#6b7280; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:.45} }
</style>