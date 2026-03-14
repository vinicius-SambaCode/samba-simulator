<template>
  <div class="coord-home">

    <!-- ── Cabeçalho ── -->
    <div class="heading" :class="{ ready: mounted }">
      <div>
        <span class="heading-label">{{ saudacao }}, {{ firstName }}</span>
        <h1 class="heading-title">Painel do coordenador</h1>
        <p class="heading-sub">{{ dataHoje }}</p>
      </div>
      <div class="heading-actions">
        <div v-if="alertas.length > 0" class="alert-pill">
          <span class="alert-dot" />
          {{ alertas.length }} pendência{{ alertas.length > 1 ? 's' : '' }}
        </div>
        <NuxtLink to="/dashboard/coordenador/simulados/novo" class="btn-primary">
          <Icon name="lucide:plus" class="w-4 h-4" />
          Novo simulado
        </NuxtLink>
      </div>
    </div>

    <!-- ── KPIs ── -->
    <div class="kpi-row" :class="{ ready: mounted }">
      <template v-if="loading">
        <div v-for="i in 4" :key="i" class="kpi-skeleton" :style="`--i:${i}`" />
      </template>
      <template v-else>
        <div v-for="(kpi, i) in kpis" :key="kpi.label" class="kpi-card" :style="`--i:${i}`">
          <div class="kpi-icon" :class="kpi.iconBg">
            <Icon :name="kpi.icon" class="w-4 h-4" :class="kpi.iconColor" />
          </div>
          <div>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ kpi.value }}</span>
              <span v-if="kpi.badge" class="kpi-badge" :class="kpi.badgeColor">{{ kpi.badge }}</span>
            </div>
            <span class="kpi-label">{{ kpi.label }}</span>
          </div>
        </div>
      </template>
    </div>

    <!-- ── Acesso rápido ── -->
    <div class="quick-section" :class="{ ready: mounted }">
      <p class="section-label">Acesso rápido</p>
      <div class="quick-grid">
        <NuxtLink v-for="(acao, i) in acoesRapidas" :key="acao.label"
          :to="acao.to" class="quick-btn" :style="`--i:${i}`">
          <div class="quick-icon" :class="acao.iconBg">
            <Icon :name="acao.icon" class="w-5 h-5" :class="acao.iconColor" />
          </div>
          <span class="quick-label">{{ acao.label }}</span>
          <span class="quick-desc">{{ acao.desc }}</span>
        </NuxtLink>
      </div>
    </div>

    <!-- ── Corpo: simulados + escola ── -->
    <div class="body-grid" :class="{ ready: mounted }">

      <!-- Simulados em andamento -->
      <section class="card col-wide">
        <header class="card-header">
          <div class="card-title">
            <div class="card-title-icon bg-blue-50">
              <Icon name="lucide:file-text" class="w-4 h-4 text-blue-500" />
            </div>
            Simulados em andamento
          </div>
          <NuxtLink to="/dashboard/coordenador/simulados" class="link-more">
            Ver todos <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </NuxtLink>
        </header>

        <div v-if="loading" class="card-loading">
          <div v-for="i in 3" :key="i" class="skeleton-row" :style="`--i:${i}`" />
        </div>

        <div v-else-if="simuladosAtivos.length === 0" class="card-empty">
          <Icon name="lucide:clipboard-list" class="w-8 h-8 text-gray-200" />
          <p>Nenhum simulado ativo</p>
          <NuxtLink to="/dashboard/coordenador/simulados/novo" class="link-more">
            Criar primeiro simulado →
          </NuxtLink>
        </div>

        <ul v-else class="item-list">
          <li v-for="exam in simuladosAtivos" :key="exam.id">
            <NuxtLink :to="`/dashboard/coordenador/simulados/${exam.id}`" class="item-link">
              <div class="item-icon" :class="statusBg(exam.status)">
                <Icon :name="statusIcon(exam.status)" class="w-4 h-4" :class="statusColor(exam.status)" />
              </div>
              <div class="item-body">
                <div class="item-title-row">
                  <span class="item-title">{{ exam.title }}</span>
                  <span class="status-badge" :class="statusBadge(exam.status)">
                    {{ statusLabel(exam.status) }}
                  </span>
                </div>
                <div class="progress-row">
                  <div class="progress-bar">
                    <div class="progress-fill bg-blue-400" :style="`width:${exam._progresso ?? 0}%`" />
                  </div>
                  <span class="progress-text">{{ exam._progresso ?? 0 }}%</span>
                </div>
              </div>
              <Icon name="lucide:chevron-right" class="item-arrow" />
            </NuxtLink>
          </li>
        </ul>
      </section>

      <!-- Sidebar direita -->
      <div class="sidebar-col">

        <!-- Escola em números -->
        <section class="card">
          <header class="card-header">
            <div class="card-title">
              <div class="card-title-icon bg-emerald-50">
                <Icon name="lucide:school" class="w-4 h-4 text-emerald-500" />
              </div>
              Escola em números
            </div>
          </header>
          <ul class="nums-list">
            <li v-for="item in escolaNumeros" :key="item.label" class="nums-item">
              <div class="nums-left">
                <Icon :name="item.icon" class="w-3.5 h-3.5 flex-shrink-0" :class="item.color" />
                <span class="nums-label">{{ item.label }}</span>
              </div>
              <span v-if="loading" class="skeleton-num" />
              <span v-else class="nums-value">{{ item.value }}</span>
            </li>
          </ul>
        </section>

        <!-- Pendências -->
        <section v-if="alertas.length > 0" class="card card-alert">
          <header class="card-header card-header-alert">
            <div class="card-title">
              <div class="card-title-icon bg-amber-100">
                <Icon name="lucide:alert-triangle" class="w-4 h-4 text-amber-600" />
              </div>
              Pendências
            </div>
          </header>
          <ul class="alert-list">
            <li v-for="a in alertas" :key="a.texto">
              <NuxtLink :to="a.to" class="alert-item">
                <span class="alert-bullet" />
                <span>{{ a.texto }}</span>
              </NuxtLink>
            </li>
          </ul>
        </section>

        <!-- Onboarding vazio -->
        <section v-if="!loading && escolaVazia" class="card card-onboard">
          <Icon name="lucide:rocket" class="w-8 h-8 text-white/80 mb-2" />
          <h3 class="onboard-title">Configure sua escola</h3>
          <p class="onboard-sub">Crie as turmas, importe alunos e cadastre os professores para começar.</p>
          <div class="onboard-steps">
            <NuxtLink v-for="step in setupSteps" :key="step.label" :to="step.to" class="onboard-step">
              {{ step.label }}
              <Icon name="lucide:arrow-right" class="w-3 h-3" />
            </NuxtLink>
          </div>
        </section>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()
const { user } = useAuth()
const BASE_URL = useRuntimeConfig().public.apiBase as string

const loading     = ref(true)
const mounted     = ref(false)
const exams       = ref<any[]>([])
const totalTurmas = ref(0)
const totalAlunos = ref(0)
const totalProfs  = ref(0)

onMounted(async () => {
  await nextTick()
  setTimeout(() => { mounted.value = true }, 30)

  try {
    const [examList, turmaList, alunoList, profList] = await Promise.allSettled([
      get<any[]>('/exams/'),
      get<any[]>('/school/classes'),
      get<any[]>('/school/students/'),
      get<any[]>('/school/teachers'),
    ])
    if (examList.status  === 'fulfilled') exams.value       = examList.value
    if (turmaList.status === 'fulfilled') totalTurmas.value = turmaList.value.length
    if (alunoList.status === 'fulfilled') totalAlunos.value = alunoList.value.length
    if (profList.status  === 'fulfilled') totalProfs.value  = profList.value.length

    // Progresso dos simulados em coleta
    await Promise.allSettled(
      exams.value.filter(e => e.status === 'collecting').map(async e => {
        try {
          const prog  = await get<any>(`/exams/${e.id}/progress`)
          const discs = prog.disciplines ?? []
          const total = discs.reduce((a: number, d: any) => a + d.quota, 0)
          const feito = discs.reduce((a: number, d: any) => a + Math.min(d.submitted, d.quota), 0)
          e._progresso = total > 0 ? Math.round(feito / total * 100) : 0
        } catch { e._progresso = 0 }
      })
    )
  } finally {
    loading.value = false
  }
})

const firstName = computed(() => user.value?.name?.split(' ')[0] ?? 'Coordenador')
const saudacao  = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Bom dia'
  if (h < 18) return 'Boa tarde'
  return 'Boa noite'
})
const dataHoje = computed(() =>
  new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })
)

const simuladosAtivos = computed(() =>
  exams.value.filter(e => ['draft','collecting','review','locked'].includes(e.status)).slice(0, 6)
)

const kpis = computed(() => [
  { label:'Turmas',             value: totalTurmas.value, icon:'lucide:users',          iconBg:'bg-blue-50',   iconColor:'text-blue-500'   },
  { label:'Alunos',             value: totalAlunos.value, icon:'lucide:graduation-cap', iconBg:'bg-emerald-50',iconColor:'text-emerald-500' },
  { label:'Professores',        value: totalProfs.value,  icon:'lucide:briefcase',      iconBg:'bg-violet-50', iconColor:'text-violet-500'  },
  {
    label:'Simulados', value: exams.value.length,
    icon:'lucide:file-text', iconBg:'bg-amber-50', iconColor:'text-amber-500',
    badge: simuladosAtivos.value.length > 0 ? `${simuladosAtivos.value.length} ativos` : undefined,
    badgeColor:'bg-amber-100 text-amber-700',
  },
])

const acoesRapidas = [
  { to:'/dashboard/coordenador/turmas',      label:'Turmas',      desc:'Gerenciar turmas',   icon:'lucide:users',       iconBg:'bg-blue-50',   iconColor:'text-blue-500'   },
  { to:'/dashboard/coordenador/professores', label:'Professores', desc:'Vínculos e acesso',  icon:'lucide:briefcase',   iconBg:'bg-violet-50', iconColor:'text-violet-500'  },
  { to:'/dashboard/coordenador/simulados',   label:'Simulados',   desc:'Todos os simulados', icon:'lucide:file-text',   iconBg:'bg-amber-50',  iconColor:'text-amber-500'   },
  { to:'/dashboard/coordenador/questoes',    label:'Questões',    desc:'Banco de questões',  icon:'lucide:help-circle', iconBg:'bg-teal-50',   iconColor:'text-teal-500'    },
  { to:'/dashboard/coordenador/disciplinas', label:'Disciplinas', desc:'Gerenciar grades',   icon:'lucide:book-open',   iconBg:'bg-indigo-50', iconColor:'text-indigo-500'  },
  { to:'/dashboard/coordenador/relatorios',  label:'Relatórios',  desc:'Exportar dados',     icon:'lucide:download',    iconBg:'bg-gray-100',  iconColor:'text-gray-500'    },
]

const escolaNumeros = computed(() => [
  { label:'Turmas cadastradas', icon:'lucide:building-2',   color:'text-blue-400',   value: totalTurmas.value },
  { label:'Alunos ativos',      icon:'lucide:users',        color:'text-emerald-400',value: totalAlunos.value },
  { label:'Professores',        icon:'lucide:briefcase',    color:'text-violet-400', value: totalProfs.value  },
  { label:'Simulados criados',  icon:'lucide:file-text',    color:'text-amber-400',  value: exams.value.length },
  { label:'Em coleta',          icon:'lucide:loader',       color:'text-blue-400',   value: exams.value.filter(e => e.status === 'collecting').length },
  { label:'Concluídos',         icon:'lucide:check-circle', color:'text-emerald-400',value: exams.value.filter(e => ['generated','published'].includes(e.status)).length },
])

const escolaVazia = computed(() => totalTurmas.value === 0)

const setupSteps = [
  { label:'1. Criar turmas',          to:'/dashboard/coordenador/turmas'       },
  { label:'2. Cadastrar professores', to:'/dashboard/coordenador/professores'  },
  { label:'3. Criar simulado',        to:'/dashboard/coordenador/simulados/novo'},
]

const alertas = computed(() => {
  const list: { texto: string; to: string }[] = []
  const locked = exams.value.filter(e => e.status === 'locked').length
  if (locked > 0)
    list.push({ texto:`${locked} simulado(s) travado(s) — gere os PDFs`, to:'/dashboard/coordenador/simulados' })
  if (totalTurmas.value > 0 && totalAlunos.value === 0)
    list.push({ texto:'Nenhum aluno cadastrado — importe via CSV', to:'/dashboard/coordenador/turmas' })
  if (totalProfs.value === 0 && totalTurmas.value > 0)
    list.push({ texto:'Nenhum professor cadastrado ainda', to:'/dashboard/coordenador/professores' })
  return list
})

function statusBg(s: string) {
  return ({ collecting:'bg-blue-50', review:'bg-amber-50', locked:'bg-gray-100', generated:'bg-purple-50', published:'bg-emerald-50', draft:'bg-gray-50' } as any)[s] ?? 'bg-gray-50'
}
function statusIcon(s: string) {
  return ({ collecting:'lucide:pencil', review:'lucide:eye', locked:'lucide:lock', generated:'lucide:file-check', published:'lucide:check-circle', draft:'lucide:file' } as any)[s] ?? 'lucide:file'
}
function statusColor(s: string) {
  return ({ collecting:'text-blue-500', review:'text-amber-500', locked:'text-gray-500', generated:'text-purple-500', published:'text-emerald-500', draft:'text-gray-400' } as any)[s] ?? 'text-gray-400'
}
function statusBadge(s: string) {
  return ({ collecting:'badge-blue', review:'badge-amber', locked:'badge-gray', generated:'badge-purple', published:'badge-emerald', draft:'badge-gray' } as any)[s] ?? 'badge-gray'
}
function statusLabel(s: string) {
  return ({ collecting:'Em coleta', review:'Em revisão', locked:'Travado', generated:'Gerado', published:'Publicado', draft:'Rascunho' } as any)[s] ?? s
}
</script>

<style scoped>
.coord-home {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 2rem;
}

/* ── Cabeçalho ── */
.heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.38s ease, transform 0.38s ease;
}
.heading.ready { opacity: 1; transform: translateY(0); }
.heading-label {
  display: block;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #3b82f6;
  margin-bottom: 0.2rem;
}
.heading-title { font-size: 1.5rem; font-weight: 800; color: #111827; margin: 0 0 0.25rem; line-height: 1.15; }
.heading-sub   { font-size: 0.8rem; color: #9ca3af; margin: 0; }
.heading-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }

.alert-pill {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 9999px; font-size: 0.75rem; font-weight: 600; color: #92400e;
}
.alert-dot {
  width: 0.45rem; height: 0.45rem; border-radius: 50%;
  background: #f59e0b; animation: blink 2s ease infinite;
}

/* ── KPIs ── */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.38s ease 0.07s, transform 0.38s ease 0.07s;
}
.kpi-row.ready { opacity: 1; transform: translateY(0); }
@media (min-width: 640px) { .kpi-row { grid-template-columns: repeat(4, 1fr); } }

.kpi-card {
  background: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  animation: card-in 0.35s ease both;
  animation-delay: calc(var(--i, 0) * 55ms + 80ms);
  cursor: default;
}
.kpi-skeleton {
  height: 5.25rem;
  background: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  animation: shimmer 1.5s ease-in-out infinite;
  animation-delay: calc(var(--i, 0) * 80ms);
}

@keyframes card-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0);   }
}

.kpi-icon {
  width: 2.25rem; height: 2.25rem;
  border-radius: 0.625rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.kpi-value-row { display: flex; align-items: center; gap: 0.4rem; }
.kpi-value { font-size: 1.5rem; font-weight: 800; color: #111827; line-height: 1; }
.kpi-label { display: block; font-size: 0.68rem; color: #9ca3af; font-weight: 500; margin-top: 0.2rem; }
.kpi-badge { font-size: 0.6rem; font-weight: 700; padding: 0.15rem 0.4rem; border-radius: 9999px; }

/* ── Quick access ── */
.quick-section {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.38s ease 0.14s, transform 0.38s ease 0.14s;
}
.quick-section.ready { opacity: 1; transform: translateY(0); }

.section-label {
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #9ca3af;
  margin: 0 0 0.6rem;
}
.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem;
}
@media (min-width: 640px) { .quick-grid { grid-template-columns: repeat(6, 1fr); } }

.quick-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  padding: 0.875rem 0.5rem;
  background: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  text-decoration: none;
  text-align: center;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
  animation: card-in 0.35s ease both;
  animation-delay: calc(var(--i, 0) * 45ms + 160ms);
}
.quick-btn:hover {
  border-color: #e5e7eb;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}
.quick-icon {
  width: 2.5rem; height: 2.5rem;
  border-radius: 0.75rem;
  display: flex; align-items: center; justify-content: center;
}
.quick-label { font-size: 0.72rem; font-weight: 700; color: #1f2937; line-height: 1.2; }
.quick-desc  { font-size: 0.62rem; color: #9ca3af; line-height: 1.3; }

/* ── Body grid ── */
.body-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.38s ease 0.21s, transform 0.38s ease 0.21s;
}
.body-grid.ready { opacity: 1; transform: translateY(0); }
@media (min-width: 1024px) { .body-grid { grid-template-columns: 1fr 280px; } }

.col-wide { min-width: 0; }
.sidebar-col { display: flex; flex-direction: column; gap: 0.75rem; }

/* ── Card ── */
.card {
  background: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  overflow: hidden;
}
.card-alert  { border-color: #fef3c7; }
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid #f9fafb;
}
.card-header-alert { border-bottom-color: #fef9c3; background: #fffbeb; }
.card-title {
  display: flex; align-items: center; gap: 0.625rem;
  font-size: 0.8rem; font-weight: 700; color: #111827;
}
.card-title-icon {
  width: 2rem; height: 2rem; border-radius: 0.5rem;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

/* ── Skeletons / empty ── */
.card-loading { padding: 0.75rem 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
.skeleton-row {
  height: 3.5rem; background: #f9fafb; border-radius: 0.75rem;
  animation: shimmer 1.5s ease-in-out infinite;
  animation-delay: calc(var(--i,0) * 120ms);
}
.skeleton-num {
  display: inline-block; width: 2.5rem; height: 1.25rem;
  background: #f3f4f6; border-radius: 0.375rem;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:0.45} }
@keyframes blink    { 0%,100%{opacity:1} 50%{opacity:0.35} }

.card-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 3rem 1rem; gap: 0.5rem; text-align: center;
}
.card-empty p { font-size: 0.78rem; color: #9ca3af; margin: 0; }

/* ── Item list ── */
.item-list { list-style: none; margin: 0; padding: 0; }
.item-list li + li { border-top: 1px solid #f9fafb; }
.item-link {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 0.8rem 1.25rem; text-decoration: none;
  transition: background 0.13s;
}
.item-link:hover { background: #fafafa; }
.item-icon {
  width: 2.25rem; height: 2.25rem; border-radius: 0.625rem;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.item-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.35rem; }
.item-title-row { display: flex; align-items: center; gap: 0.5rem; }
.item-title {
  font-size: 0.8rem; font-weight: 600; color: #111827;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;
}
.item-arrow {
  width: 0.875rem; height: 0.875rem; color: #d1d5db; flex-shrink: 0;
  transition: transform 0.13s, color 0.13s;
}
.item-link:hover .item-arrow { color: #9ca3af; transform: translateX(2px); }

/* Status badges */
.status-badge {
  font-size: 0.62rem; font-weight: 700; padding: 0.15rem 0.45rem;
  border-radius: 9999px; flex-shrink: 0;
}
.badge-blue    { background: #dbeafe; color: #1e40af; }
.badge-amber   { background: #fef3c7; color: #92400e; }
.badge-gray    { background: #f3f4f6; color: #6b7280; }
.badge-purple  { background: #ede9fe; color: #5b21b6; }
.badge-emerald { background: #d1fae5; color: #065f46; }

/* Progress */
.progress-row { display: flex; align-items: center; gap: 0.5rem; }
.progress-bar { flex: 1; height: 0.25rem; background: #f3f4f6; border-radius: 9999px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 9999px; transition: width 0.7s ease; }
.progress-text { font-size: 0.65rem; color: #9ca3af; flex-shrink: 0; }

/* Escola números */
.nums-list { list-style: none; margin: 0; padding: 0; }
.nums-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.6rem 1.25rem; border-bottom: 1px solid #f9fafb;
}
.nums-item:last-child { border-bottom: none; }
.nums-left { display: flex; align-items: center; gap: 0.625rem; }
.nums-label { font-size: 0.75rem; color: #6b7280; font-weight: 500; }
.nums-value { font-size: 0.875rem; font-weight: 800; color: #111827; }

/* Alertas */
.alert-list { list-style: none; margin: 0; padding: 0; }
.alert-item {
  display: flex; align-items: flex-start; gap: 0.625rem;
  padding: 0.625rem 1.25rem; font-size: 0.75rem; color: #6b7280;
  text-decoration: none; transition: background 0.13s;
}
.alert-item:hover { background: #fffbeb; }
.alert-bullet {
  width: 0.375rem; height: 0.375rem; border-radius: 50%;
  background: #f59e0b; flex-shrink: 0; margin-top: 0.35rem;
}

/* Onboarding */
.card-onboard {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-color: #2563eb;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.onboard-title { font-size: 0.9rem; font-weight: 800; color: white; margin: 0; }
.onboard-sub   { font-size: 0.75rem; color: rgba(255,255,255,0.75); margin: 0; line-height: 1.5; }
.onboard-steps { display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.5rem; }
.onboard-step {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: rgba(255,255,255,0.15); border-radius: 0.625rem;
  font-size: 0.75rem; font-weight: 700; color: white;
  text-decoration: none; transition: background 0.15s;
}
.onboard-step:hover { background: rgba(255,255,255,0.25); }

/* Misc */
.btn-primary {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.6rem 1.1rem;
  background: #111827; color: white;
  font-size: 0.8rem; font-weight: 700;
  border-radius: 0.75rem; text-decoration: none;
  transition: background 0.13s, transform 0.13s;
  white-space: nowrap;
}
.btn-primary:hover  { background: #1f2937; transform: translateY(-1px); }
.btn-primary:active { transform: scale(0.97); }

.link-more {
  display: inline-flex; align-items: center; gap: 0.25rem;
  font-size: 0.7rem; font-weight: 600; color: #3b82f6; text-decoration: none;
}
.link-more:hover { color: #2563eb; }
</style>