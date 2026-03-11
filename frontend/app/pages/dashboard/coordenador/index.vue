<!-- pages/dashboard/coordenador/index.vue -->
<template>
  <div class="space-y-5">

    <!-- Hero -->
    <div class="bg-white border border-gray-100 rounded-2xl px-6 py-6 flex items-center justify-between gap-4 animate-fade-in">
      <div>
        <p class="text-[11px] font-bold text-blue-500 tracking-[0.15em] uppercase mb-1">Coordenação pedagógica</p>
        <h2 class="text-2xl font-black text-gray-900 tracking-tight">
          Olá, {{ firstName }} <span class="animate-wave inline-block origin-bottom-right">👋</span>
        </h2>
        <p class="text-sm mt-1">
          <span v-if="stats.pendentes > 0" class="text-amber-500 font-semibold">
            {{ stats.pendentes }} simulado{{ stats.pendentes !== 1 ? 's' : '' }} aguardando professores
          </span>
          <span v-else-if="stats.collecting > 0" class="text-emerald-500 font-semibold">Tudo em andamento 🎉</span>
          <span v-else class="text-gray-400">Nenhum simulado ativo no momento</span>
        </p>
      </div>
      <NuxtLink
        to="/dashboard/coordenador/simulados/novo"
        class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-700 text-white text-sm font-bold rounded-xl transition-all duration-200 hover:scale-[1.03] active:scale-95 shadow-sm">
        <Icon name="lucide:plus" class="w-4 h-4" />
        <span class="hidden sm:inline">Novo simulado</span>
      </NuxtLink>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div
        v-for="(s, i) in statCards" :key="s.label"
        class="bg-white rounded-2xl border border-gray-100 p-4 flex flex-col gap-3 hover:border-gray-200 hover:shadow-sm transition-all duration-200"
        :style="`animation-delay: ${i * 60}ms`"
        :class="'animate-fade-up'">
        <div class="flex items-center justify-between">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center" :class="s.iconBg">
            <Icon :name="s.icon" class="w-4 h-4" :class="s.iconColor" />
          </div>
          <div class="h-1.5 w-12 rounded-full overflow-hidden bg-gray-100">
            <div class="h-full rounded-full transition-all duration-700" :class="s.bar"
              :style="{ width: loadingExams ? '0%' : '100%' }" />
          </div>
        </div>
        <div>
          <p class="text-[28px] font-black text-gray-900 leading-none tabular-nums">
            <span v-if="loadingExams" class="inline-block w-10 h-7 bg-gray-100 rounded-lg animate-pulse" />
            <span v-else>{{ s.value }}</span>
          </p>
          <p class="text-[11px] text-gray-400 mt-1 font-medium">{{ s.label }}</p>
        </div>
      </div>
    </div>

    <!-- Painéis principais -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

      <!-- Em coleta -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:120ms">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse block" />
            <h3 class="text-sm font-bold text-gray-900">Em coleta</h3>
            <span class="text-[11px] font-bold px-1.5 py-0.5 rounded-md bg-amber-50 text-amber-600">
              {{ collecting.length }}
            </span>
          </div>
          <NuxtLink to="/dashboard/coordenador/simulados"
            class="text-[11px] text-blue-500 hover:text-blue-600 font-bold transition-colors flex items-center gap-0.5">
            Ver todos <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </NuxtLink>
        </div>

        <!-- Skeleton -->
        <div v-if="loadingExams" class="p-4 space-y-2.5">
          <div v-for="i in 3" :key="i" class="h-14 bg-gray-50 rounded-xl animate-pulse" :style="`animation-delay:${i*80}ms`" />
        </div>

        <!-- Empty -->
        <div v-else-if="collecting.length === 0" class="flex flex-col items-center justify-center py-14">
          <div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center mb-3">
            <Icon name="lucide:inbox" class="w-5 h-5 text-gray-300" />
          </div>
          <p class="text-xs text-gray-400 font-medium">Nenhum simulado em coleta</p>
        </div>

        <!-- Lista -->
        <TransitionGroup name="list" tag="div" class="divide-y divide-gray-50">
          <NuxtLink
            v-for="exam in collecting.slice(0,4)"
            :key="exam.id"
            :to="`/dashboard/coordenador/simulados/${exam.id}`"
            class="flex items-center gap-3 px-5 py-3.5 hover:bg-amber-50/30 transition-colors group">
            <div class="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center flex-shrink-0 group-hover:bg-amber-100 transition-colors">
              <Icon name="lucide:file-text" class="w-3.5 h-3.5 text-amber-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate group-hover:text-amber-700 transition-colors">
                {{ exam.title }}
              </p>
              <div v-if="progressMap[exam.id]" class="flex items-center gap-2 mt-1">
                <div class="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full bg-amber-400 transition-all duration-700"
                    :style="{ width: calcProgresso(exam.id) + '%' }" />
                </div>
                <span class="text-[10px] text-gray-400 tabular-nums flex-shrink-0">
                  {{ progressMap[exam.id].total_submitted }}/{{ progressMap[exam.id].total_quota }}
                </span>
              </div>
            </div>
            <Icon name="lucide:chevron-right" class="w-3.5 h-3.5 text-gray-200 group-hover:text-amber-400 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
          </NuxtLink>
        </TransitionGroup>
      </div>

      <!-- Prontos para travar -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up" style="animation-delay:180ms">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <Icon name="lucide:lock" class="w-3.5 h-3.5 text-blue-500" />
            <h3 class="text-sm font-bold text-gray-900">Prontos para travar</h3>
          </div>
          <span class="text-[11px] font-bold px-1.5 py-0.5 rounded-md"
            :class="prontos.length > 0 ? 'bg-blue-50 text-blue-600' : 'bg-gray-50 text-gray-400'">
            {{ prontos.length }}
          </span>
        </div>

        <div v-if="loadingExams" class="p-4 space-y-2.5">
          <div v-for="i in 2" :key="i" class="h-14 bg-gray-50 rounded-xl animate-pulse" />
        </div>

        <div v-else-if="prontos.length === 0" class="flex flex-col items-center justify-center py-14">
          <div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center mb-3">
            <Icon name="lucide:check-circle-2" class="w-5 h-5 text-gray-300" />
          </div>
          <p class="text-xs text-gray-400 font-medium">Nenhum simulado completo ainda</p>
        </div>

        <TransitionGroup name="list" tag="div" class="divide-y divide-gray-50">
          <NuxtLink
            v-for="exam in prontos"
            :key="exam.id"
            :to="`/dashboard/coordenador/simulados/${exam.id}`"
            class="flex items-center gap-3 px-5 py-3.5 hover:bg-blue-50/30 transition-colors group">
            <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
              <Icon name="lucide:lock" class="w-3.5 h-3.5 text-blue-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate group-hover:text-blue-700 transition-colors">
                {{ exam.title }}
              </p>
              <p class="text-[10px] text-emerald-500 font-semibold mt-0.5 flex items-center gap-1">
                <Icon name="lucide:check" class="w-3 h-3" /> 100% das questões recebidas
              </p>
            </div>
            <Icon name="lucide:chevron-right" class="w-3.5 h-3.5 text-gray-200 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
          </NuxtLink>
        </TransitionGroup>
      </div>
    </div>

    <!-- Turmas + atividade recente -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

      <!-- Turmas (2/3) -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-gray-100 p-5 animate-fade-up" style="animation-delay:240ms">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-gray-900">Turmas ativas</h3>
          <NuxtLink to="/dashboard/coordenador/turmas"
            class="text-[11px] text-blue-500 hover:text-blue-600 font-bold transition-colors flex items-center gap-0.5">
            Gerenciar <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </NuxtLink>
        </div>

        <div v-if="loadingClasses" class="flex flex-wrap gap-2">
          <div v-for="i in 5" :key="i" class="h-8 rounded-lg bg-gray-100 animate-pulse" :style="`width:${48+i*12}px`" />
        </div>
        <div v-else-if="classes.length === 0" class="text-xs text-gray-400">Nenhuma turma cadastrada.</div>
        <div v-else class="flex flex-wrap gap-2">
          <NuxtLink
            v-for="cls in classes" :key="cls.id"
            to="/dashboard/coordenador/turmas"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-50 border border-gray-100 text-xs font-semibold text-gray-600 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-all duration-150">
            <Icon name="lucide:users" class="w-3 h-3" />
            {{ cls.name }}
          </NuxtLink>
        </div>
      </div>

      <!-- Acesso rápido (1/3) -->
      <div class="bg-white rounded-2xl border border-gray-100 p-5 animate-fade-up" style="animation-delay:300ms">
        <h3 class="text-sm font-bold text-gray-900 mb-4">Acesso rápido</h3>
        <div class="space-y-2">
          <NuxtLink v-for="link in quickLinks" :key="link.to" :to="link.to"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-50 transition-colors group">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" :class="link.iconBg">
              <Icon :name="link.icon" class="w-3.5 h-3.5" :class="link.iconColor" />
            </div>
            <span class="text-xs font-semibold text-gray-600 group-hover:text-gray-900 transition-colors">{{ link.label }}</span>
            <Icon name="lucide:chevron-right" class="w-3 h-3 text-gray-200 group-hover:text-gray-400 ml-auto transition-colors" />
          </NuxtLink>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { user } = useAuth()
const { get }  = useApi()

const exams       = ref<any[]>([])
const classes     = ref<any[]>([])
const progressMap = ref<Record<number, any>>({})
const loadingExams   = ref(true)
const loadingClasses = ref(true)

const firstName  = computed(() => user.value?.name?.split(' ')[0] ?? '')
const collecting = computed(() => exams.value.filter(e => e.status === 'collecting'))
const prontos    = computed(() =>
  collecting.value.filter(e => {
    const p = progressMap.value[e.id]
    return p && p.total_quota > 0 && p.total_remaining === 0
  })
)
const stats = computed(() => ({
  total:      exams.value.length,
  collecting: collecting.value.length,
  locked:     exams.value.filter(e => e.status === 'locked').length,
  published:  exams.value.filter(e => e.status === 'published').length,
  pendentes:  collecting.value.filter(e => {
    const p = progressMap.value[e.id]
    return !p || p.total_remaining > 0
  }).length,
}))

const statCards = computed(() => [
  { label: 'Total',       value: stats.value.total,      icon: 'lucide:file-text',      iconBg: 'bg-gray-50',    iconColor: 'text-gray-400',    bar: 'bg-gray-300' },
  { label: 'Em coleta',   value: stats.value.collecting,  icon: 'lucide:refresh-cw',     iconBg: 'bg-amber-50',   iconColor: 'text-amber-500',   bar: 'bg-amber-400' },
  { label: 'Travados',    value: stats.value.locked,      icon: 'lucide:lock',           iconBg: 'bg-blue-50',    iconColor: 'text-blue-500',    bar: 'bg-blue-400' },
  { label: 'Publicados',  value: stats.value.published,   icon: 'lucide:check-circle-2', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-500', bar: 'bg-emerald-400' },
])

const quickLinks = [
  { to: '/dashboard/coordenador/simulados/novo', label: 'Novo simulado',   icon: 'lucide:plus-circle',  iconBg: 'bg-blue-50',    iconColor: 'text-blue-500' },
  { to: '/dashboard/coordenador/professores',    label: 'Professores',     icon: 'lucide:user-check',   iconBg: 'bg-indigo-50',  iconColor: 'text-indigo-500' },
  { to: '/dashboard/coordenador/alunos',         label: 'Alunos',          icon: 'lucide:graduation-cap', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-500' },
  { to: '/dashboard/coordenador/relatorios',     label: 'Relatórios',      icon: 'lucide:bar-chart-2',  iconBg: 'bg-purple-50',  iconColor: 'text-purple-500' },
  { to: '/dashboard/coordenador/questoes',       label: 'Questões',        icon: 'lucide:list-checks',  iconBg: 'bg-orange-50',  iconColor: 'text-orange-500' },
]

function calcProgresso(id: number) {
  const p = progressMap.value[id]
  if (!p?.total_quota) return 0
  return Math.min(100, Math.round(p.total_submitted / p.total_quota * 100))
}

onMounted(async () => {
  const [examList, classList] = await Promise.allSettled([
    get<any[]>('/exams/'),
    get<any[]>('/school/classes'),
  ])
  if (examList.status === 'fulfilled') exams.value = examList.value
  if (classList.status === 'fulfilled') classes.value = classList.value
  loadingExams.value   = false
  loadingClasses.value = false

  const col = exams.value.filter(e => e.status === 'collecting')
  const results = await Promise.allSettled(col.map(e => get<any>(`/exams/${e.id}/dashboard`)))
  col.forEach((e, i) => {
    if (results[i].status === 'fulfilled') progressMap.value[e.id] = results[i].value
  })
})
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  20%       { transform: rotate(-10deg); }
  40%       { transform: rotate(14deg); }
  60%       { transform: rotate(-8deg); }
  80%       { transform: rotate(10deg); }
}
.animate-fade-in  { animation: fade-in  0.35s ease both; }
.animate-fade-up  { animation: fade-up  0.4s ease both; }
.animate-wave     { animation: wave 1.2s ease 0.4s both; }

.list-enter-active { transition: all 0.25s ease; }
.list-leave-active { transition: all 0.2s ease; }
.list-enter-from   { opacity: 0; transform: translateX(-8px); }
.list-leave-to     { opacity: 0; transform: translateX(8px); }
</style>