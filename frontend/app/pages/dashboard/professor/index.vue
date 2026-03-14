<template>
  <div class="prof-home">

    <!-- ── Saudação ── -->
    <div class="greeting" :class="{ ready: mounted }">
      <div class="greeting-text">
        <span class="greeting-label">{{ saudacao }},</span>
        <h1 class="greeting-name">{{ firstName }}</h1>
        <p class="greeting-sub" v-if="!loading">
          <span v-if="pendentes.length > 0">
            Você tem <strong>{{ pendentes.length }} simulado{{ pendentes.length > 1 ? 's' : '' }}</strong> aguardando questões.
          </span>
          <span v-else-if="collecting.length > 0">Todas as cotas estão completas. 🎉</span>
          <span v-else>Nenhum simulado ativo no momento.</span>
        </p>
        <span v-else class="skeleton-line" />
      </div>
      <NuxtLink to="/dashboard/professor/simulados" class="btn-primary">
        <Icon name="lucide:file-text" class="w-4 h-4" />
        Meus simulados
      </NuxtLink>
    </div>

    <!-- ── Cards de resumo ── -->
    <div class="stats-row" :class="{ ready: mounted }">
      <div v-for="(card, i) in statCards" :key="card.label"
        class="stat-card" :style="`--i:${i}`">
        <div class="stat-icon" :class="card.iconBg">
          <Icon :name="card.icon" class="w-5 h-5" :class="card.iconColor" />
        </div>
        <div class="stat-body">
          <span class="stat-value">
            <span v-if="loading" class="skeleton-num" />
            <span v-else>{{ card.value }}</span>
          </span>
          <span class="stat-label">{{ card.label }}</span>
        </div>
      </div>
    </div>

    <!-- ── Corpo principal ── -->
    <div class="main-grid" :class="{ ready: mounted }">

      <!-- Pendentes -->
      <section class="card">
        <header class="card-header">
          <div class="card-title">
            <span class="dot dot-amber" />
            Pendentes
          </div>
          <span class="badge" :class="pendentes.length > 0 ? 'badge-amber' : 'badge-gray'">
            {{ pendentes.length }}
          </span>
        </header>

        <div v-if="loading" class="card-loading">
          <div v-for="i in 2" :key="i" class="skeleton-row" :style="`--i:${i}`" />
        </div>
        <div v-else-if="pendentes.length === 0" class="card-empty">
          <Icon name="lucide:check-circle-2" class="w-8 h-8 text-emerald-300" />
          <p>Tudo em dia!</p>
        </div>
        <ul v-else class="item-list">
          <li v-for="exam in pendentes.slice(0, 5)" :key="exam.id">
            <NuxtLink :to="`/dashboard/professor/simulados/${exam.id}`" class="item-link">
              <div class="item-icon bg-amber-50">
                <Icon name="lucide:pencil" class="w-4 h-4 text-amber-500" />
              </div>
              <div class="item-body">
                <span class="item-title">{{ exam.title }}</span>
                <div v-if="progressMap[exam.id]" class="progress-row">
                  <div class="progress-bar">
                    <div class="progress-fill bg-amber-400" :style="`width:${calcProgresso(exam.id)}%`" />
                  </div>
                  <span class="progress-text">{{ somarDiscs(exam.id,'submitted') }}/{{ somarDiscs(exam.id,'quota') }}</span>
                </div>
                <span v-else class="item-hint">Nenhuma questão enviada ainda</span>
              </div>
              <Icon name="lucide:chevron-right" class="item-arrow" />
            </NuxtLink>
          </li>
        </ul>
      </section>

      <!-- Concluídos -->
      <section class="card">
        <header class="card-header">
          <div class="card-title">
            <Icon name="lucide:lock" class="w-3.5 h-3.5 text-blue-400" />
            Concluídos
          </div>
          <NuxtLink to="/dashboard/professor/simulados" class="link-more">Ver todos →</NuxtLink>
        </header>

        <div v-if="loading" class="card-loading">
          <div v-for="i in 2" :key="i" class="skeleton-row" :style="`--i:${i}`" />
        </div>
        <div v-else-if="concluidos.length === 0" class="card-empty">
          <Icon name="lucide:inbox" class="w-8 h-8 text-gray-200" />
          <p>Nenhum simulado concluído</p>
        </div>
        <ul v-else class="item-list">
          <li v-for="exam in concluidos.slice(0, 5)" :key="exam.id">
            <div class="item-link no-hover">
              <div class="item-icon" :class="exam.status === 'locked' ? 'bg-blue-50' : 'bg-emerald-50'">
                <Icon :name="exam.status === 'locked' ? 'lucide:lock' : 'lucide:check-circle-2'"
                  class="w-4 h-4" :class="exam.status === 'locked' ? 'text-blue-400' : 'text-emerald-400'" />
              </div>
              <div class="item-body">
                <span class="item-title">{{ exam.title }}</span>
                <span class="item-hint" :class="exam.status === 'locked' ? 'text-blue-400' : 'text-emerald-400'">
                  {{ statusLabel(exam.status) }}
                </span>
              </div>
            </div>
          </li>
        </ul>
      </section>
    </div>

    <!-- ── Progresso ativos ── -->
    <section class="card progress-section" :class="{ ready: mounted, hidden: !loading && collecting.length === 0 }">
      <header class="card-header">
        <div class="card-title">Progresso nos simulados ativos</div>
      </header>
      <div v-if="loading" class="card-loading">
        <div v-for="i in 2" :key="i" class="skeleton-progress" :style="`--i:${i}`" />
      </div>
      <div v-else class="progress-list">
        <div v-for="exam in collecting" :key="exam.id" class="progress-item">
          <div class="progress-item-top">
            <span class="progress-item-title">{{ exam.title }}</span>
            <span class="progress-pct" :class="calcProgresso(exam.id) === 100 ? 'text-emerald-600' : 'text-gray-500'">
              {{ calcProgresso(exam.id) }}%
            </span>
          </div>
          <div class="progress-bar thick">
            <div class="progress-fill"
              :class="calcProgresso(exam.id) === 100 ? 'bg-emerald-400' : 'bg-blue-400'"
              :style="`width:${calcProgresso(exam.id)}%`" />
          </div>
          <div class="progress-item-bottom">
            <span>{{ somarDiscs(exam.id,'submitted') }}/{{ somarDiscs(exam.id,'quota') }} questões</span>
            <NuxtLink v-if="calcProgresso(exam.id) < 100" :to="`/dashboard/professor/simulados/${exam.id}`" class="link-more">
              Continuar →
            </NuxtLink>
            <span v-else class="complete-label">
              <Icon name="lucide:check" class="w-3 h-3" /> Completo
            </span>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { user } = useAuth()
const { get }  = useApi()

const exams       = ref<any[]>([])
const classes     = ref<any[]>([])
const progressMap = ref<Record<number, any>>({})
const loading     = ref(true)
const mounted     = ref(false)

onMounted(async () => {
  await nextTick()
  setTimeout(() => { mounted.value = true }, 30)

  const [examList, classList] = await Promise.allSettled([
    get<any[]>('/exams/'),
    get<any[]>('/school/my-subjects'),
  ])
  if (examList.status  === 'fulfilled') exams.value   = examList.value
  if (classList.status === 'fulfilled') classes.value = classList.value
  loading.value = false

  const col = exams.value.filter(e => e.status === 'collecting')
  const results = await Promise.allSettled(col.map(e => get<any>(`/exams/${e.id}/progress`)))
  col.forEach((e, i) => {
    const r = results[i]
    if (r.status === 'fulfilled') progressMap.value[e.id] = r.value
  })
})

const firstName = computed(() => user.value?.name?.split(' ')[0] ?? '')
const saudacao  = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Bom dia'
  if (h < 18) return 'Boa tarde'
  return 'Boa noite'
})

const collecting = computed(() => exams.value.filter(e => e.status === 'collecting'))
const concluidos = computed(() => exams.value.filter(e => ['locked','generated','published'].includes(e.status)))
const pendentes  = computed(() =>
  collecting.value.filter(e => {
    const discs = progressMap.value[e.id]?.disciplines ?? []
    if (!discs.length) return true
    const quota = discs.reduce((s: number, d: any) => s + (d.quota ?? 0), 0)
    const done  = discs.reduce((s: number, d: any) => s + (d.submitted ?? 0), 0)
    return done < quota
  })
)

const statCards = computed(() => [
  { label: 'Simulados atribuídos', value: exams.value.length,     icon: 'lucide:file-text',   iconBg: 'bg-gray-50',   iconColor: 'text-gray-500'   },
  { label: 'Aguardando questões',  value: pendentes.value.length, icon: 'lucide:alert-circle', iconBg: 'bg-amber-50',  iconColor: 'text-amber-500'  },
  { label: 'Simulados travados',   value: exams.value.filter(e => e.status === 'locked').length, icon: 'lucide:lock', iconBg: 'bg-blue-50', iconColor: 'text-blue-500' },
  { label: 'Minhas turmas',        value: classes.value.length,   icon: 'lucide:users',        iconBg: 'bg-violet-50', iconColor: 'text-violet-500' },
])

function somarDiscs(id: number, field: 'submitted' | 'quota') {
  return (progressMap.value[id]?.disciplines ?? []).reduce((s: number, d: any) => s + (d[field] ?? 0), 0)
}
function calcProgresso(id: number) {
  const quota = somarDiscs(id, 'quota')
  if (!quota) return 0
  return Math.min(100, Math.round(somarDiscs(id, 'submitted') / quota * 100))
}
function statusLabel(s: string) {
  return ({ collecting:'Em coleta', locked:'Travado', generated:'Cadernos gerados', published:'Publicado' } as any)[s] ?? s
}
</script>

<style scoped>
.prof-home {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 2rem;
}

/* Saudação */
.greeting {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.38s ease, transform 0.38s ease;
}
.greeting.ready { opacity: 1; transform: translateY(0); }
.greeting-label {
  display: block;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #f97316;
  margin-bottom: 0.15rem;
}
.greeting-name {
  font-size: 1.75rem;
  font-weight: 800;
  color: #111827;
  line-height: 1.1;
  margin: 0 0 0.35rem;
}
.greeting-sub { font-size: 0.875rem; color: #6b7280; margin: 0; }
.greeting-sub strong { color: #111827; font-weight: 700; }

/* Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.38s ease 0.07s, transform 0.38s ease 0.07s;
}
.stats-row.ready { opacity: 1; transform: translateY(0); }
@media (min-width: 640px) { .stats-row { grid-template-columns: repeat(4, 1fr); } }

.stat-card {
  background: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  animation: card-in 0.35s ease both;
  animation-delay: calc(var(--i, 0) * 55ms + 80ms);
}
@keyframes card-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0);   }
}
.stat-icon {
  width: 2.5rem; height: 2.5rem;
  border-radius: 0.75rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-value { display: block; font-size: 1.5rem; font-weight: 800; color: #111827; line-height: 1; }
.stat-label { display: block; font-size: 0.7rem; color: #9ca3af; font-weight: 500; margin-top: 0.2rem; line-height: 1.3; }

/* Main grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.38s ease 0.14s, transform 0.38s ease 0.14s;
}
.main-grid.ready { opacity: 1; transform: translateY(0); }
@media (min-width: 768px) { .main-grid { grid-template-columns: 1fr 1fr; } }

/* Card */
.card {
  background: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  overflow: hidden;
}
.progress-section {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.38s ease 0.21s, transform 0.38s ease 0.21s;
}
.progress-section.ready  { opacity: 1; transform: translateY(0); }
.progress-section.hidden { display: none; }

.skeleton-progress {
  height: 3rem; background: #f9fafb; border-radius: 0.75rem;
  animation: shimmer 1.5s ease-in-out infinite;
  animation-delay: calc(var(--i,0) * 120ms);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid #f9fafb;
}
.card-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.8rem; font-weight: 700; color: #111827;
}

/* Dot */
.dot { width: 0.45rem; height: 0.45rem; border-radius: 50%; }
.dot-amber { background: #fbbf24; animation: blink 2s ease infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }

/* Badge */
.badge { font-size: 0.65rem; font-weight: 700; padding: 0.18rem 0.45rem; border-radius: 9999px; }
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-gray  { background: #f3f4f6; color: #9ca3af; }

/* Skeletons */
.card-loading { padding: 0.75rem 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
.skeleton-row {
  height: 3.25rem; background: #f9fafb; border-radius: 0.75rem;
  animation: shimmer 1.5s ease-in-out infinite;
  animation-delay: calc(var(--i,0) * 120ms);
}
.skeleton-line {
  display: inline-block; width: 55%; height: 0.875rem;
  background: #f3f4f6; border-radius: 0.375rem;
  animation: shimmer 1.5s ease-in-out infinite;
}
.skeleton-num {
  display: inline-block; width: 2rem; height: 1.5rem;
  background: #f3f4f6; border-radius: 0.375rem;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:0.45} }

.card-empty {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 2.5rem 1rem; gap: 0.5rem;
}
.card-empty p { font-size: 0.78rem; color: #9ca3af; margin: 0; }

/* Item list */
.item-list { list-style: none; margin: 0; padding: 0; }
.item-list li + li { border-top: 1px solid #f9fafb; }

.item-link {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 0.8rem 1.25rem;
  text-decoration: none;
  transition: background 0.13s;
}
.item-link:not(.no-hover):hover { background: #fafafa; }

.item-icon {
  width: 2rem; height: 2rem; border-radius: 0.625rem;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.item-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.25rem; }
.item-title {
  font-size: 0.8rem; font-weight: 600; color: #111827;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.item-hint { font-size: 0.7rem; color: #9ca3af; }
.item-arrow {
  width: 0.875rem; height: 0.875rem; color: #d1d5db; flex-shrink: 0;
  transition: transform 0.13s, color 0.13s;
}
.item-link:hover .item-arrow { color: #9ca3af; transform: translateX(2px); }

/* Progress */
.progress-row { display: flex; align-items: center; gap: 0.5rem; }
.progress-bar { flex: 1; height: 0.25rem; background: #f3f4f6; border-radius: 9999px; overflow: hidden; }
.progress-bar.thick { height: 0.45rem; }
.progress-fill { height: 100%; border-radius: 9999px; transition: width 0.7s ease; }
.progress-text { font-size: 0.65rem; color: #9ca3af; flex-shrink: 0; }

.progress-list { padding: 0.875rem 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.progress-item { display: flex; flex-direction: column; gap: 0.4rem; }
.progress-item-top  { display: flex; justify-content: space-between; align-items: center; }
.progress-item-bottom { display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; color: #9ca3af; }
.progress-item-title { font-size: 0.8rem; font-weight: 600; color: #374151; }
.progress-pct { font-size: 0.8rem; font-weight: 700; }

.complete-label { display: flex; align-items: center; gap: 0.25rem; color: #10b981; font-weight: 600; font-size: 0.7rem; }

/* Buttons / links */
.btn-primary {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.6rem 1.1rem;
  background: #111827; color: white;
  font-size: 0.8rem; font-weight: 700;
  border-radius: 0.75rem; text-decoration: none;
  transition: background 0.13s, transform 0.13s;
  flex-shrink: 0; white-space: nowrap;
}
.btn-primary:hover  { background: #1f2937; transform: translateY(-1px); }
.btn-primary:active { transform: scale(0.97); }

.link-more { font-size: 0.7rem; font-weight: 600; color: #3b82f6; text-decoration: none; }
.link-more:hover { color: #2563eb; }
</style>