<!-- pages/dashboard/professor/index.vue -->
<template>
  <div class="space-y-6">

    <!-- Hero header -->
    <div class="bg-white border border-gray-100 rounded-2xl px-6 py-7">
      <div class="flex items-center justify-between gap-4">
        <div>
          <p class="text-orange-500 text-xs font-semibold tracking-widest uppercase mb-1">Painel do professor</p>
          <h2 class="text-2xl font-bold text-gray-900">Olá, {{ firstName }} 👋</h2>
          <p class="text-gray-400 text-sm mt-1">
            <span v-if="pendentes.length > 0" class="text-amber-500 font-semibold">
              {{ pendentes.length }} simulado{{ pendentes.length !== 1 ? 's' : '' }} aguardando suas questões.
            </span>
            <span v-else-if="collecting.length > 0" class="text-emerald-500 font-semibold">
              Todas as cotas completas 🎉
            </span>
            <span v-else>Nenhum simulado ativo no momento.</span>
          </p>
        </div>
        <NuxtLink
          to="/dashboard/professor/simulados"
          class="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-800 text-white text-sm font-bold rounded-xl transition-all duration-150">
          <Icon name="lucide:file-text" class="w-4 h-4" />
          <span class="hidden sm:inline">Meus simulados</span>
        </NuxtLink>
      </div>
    </div>

    <!-- Stats row -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div v-for="s in statCards" :key="s.label"
        class="bg-white rounded-2xl border border-gray-100 p-4 flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div class="w-8 h-8 rounded-xl flex items-center justify-center" :class="s.iconBg">
            <Icon :name="s.icon" class="w-4 h-4" :class="s.iconColor" />
          </div>
          <div class="w-1.5 h-6 rounded-full" :class="s.bar" />
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-900 leading-none">
            <span v-if="loading" class="inline-block w-8 h-6 bg-gray-100 rounded animate-pulse" />
            <span v-else>{{ s.value }}</span>
          </p>
          <p class="text-xs text-gray-400 mt-1">{{ s.label }}</p>
        </div>
      </div>
    </div>

    <!-- Dois painéis -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

      <!-- Pendentes: precisa enviar questões -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            <h3 class="text-sm font-semibold text-gray-900">Questões pendentes</h3>
          </div>
          <span class="text-[11px] font-bold px-2 py-0.5 rounded-full"
            :class="pendentes.length > 0 ? 'bg-amber-50 text-amber-600' : 'bg-gray-50 text-gray-400'">
            {{ pendentes.length }}
          </span>
        </div>

        <div v-if="loading" class="p-4 space-y-3">
          <div v-for="i in 2" :key="i" class="h-16 bg-gray-50 rounded-xl animate-pulse" />
        </div>

        <div v-else-if="pendentes.length === 0"
          class="flex flex-col items-center justify-center py-12 px-4 text-center">
          <Icon name="lucide:check-circle-2" class="w-8 h-8 text-emerald-300 mb-2" />
          <p class="text-xs text-gray-400">Nenhuma questão pendente</p>
        </div>

        <div v-else class="divide-y divide-gray-50">
          <NuxtLink
            v-for="exam in pendentes.slice(0, 4)"
            :key="exam.id"
            :to="`/dashboard/professor/simulados/${exam.id}`"
            class="flex items-center gap-3 px-5 py-3.5 hover:bg-amber-50/40 transition-colors group">
            <div class="w-7 h-7 rounded-lg bg-amber-50 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:pencil" class="w-3.5 h-3.5 text-amber-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate group-hover:text-amber-600 transition-colors">
                {{ exam.title }}
              </p>
              <div v-if="progressMap[exam.id]" class="flex items-center gap-2 mt-1.5">
                <div class="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full bg-amber-400 transition-all duration-500"
                    :style="{ width: calcProgresso(exam.id) + '%' }" />
                </div>
                <span class="text-[10px] text-gray-400 flex-shrink-0">
                  {{ progressMap[exam.id].disciplines?.[0]?.submitted ?? 0 }}/{{ progressMap[exam.id].disciplines?.[0]?.quota ?? '?' }}
                </span>
              </div>
              <p v-else class="text-[10px] text-amber-500 font-medium mt-0.5">Nenhuma questão enviada ainda</p>
            </div>
            <Icon name="lucide:chevron-right"
              class="w-3.5 h-3.5 text-gray-300 group-hover:text-amber-400 flex-shrink-0 transition-colors" />
          </NuxtLink>
        </div>
      </div>

      <!-- Concluídos / Travados -->
      <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50">
          <div class="flex items-center gap-2">
            <Icon name="lucide:lock" class="w-3.5 h-3.5 text-blue-400" />
            <h3 class="text-sm font-semibold text-gray-900">Concluídos / Travados</h3>
          </div>
          <NuxtLink to="/dashboard/professor/simulados"
            class="text-[11px] text-blue-500 hover:text-blue-600 font-semibold transition-colors">
            Ver todos →
          </NuxtLink>
        </div>

        <div v-if="loading" class="p-4 space-y-3">
          <div v-for="i in 2" :key="i" class="h-14 bg-gray-50 rounded-xl animate-pulse" />
        </div>

        <div v-else-if="concluidos.length === 0"
          class="flex flex-col items-center justify-center py-12 px-4 text-center">
          <Icon name="lucide:inbox" class="w-8 h-8 text-gray-200 mb-2" />
          <p class="text-xs text-gray-400">Nenhum simulado concluído ainda</p>
        </div>

        <div v-else class="divide-y divide-gray-50">
          <div v-for="exam in concluidos.slice(0, 4)" :key="exam.id"
            class="flex items-center gap-3 px-5 py-3.5 hover:bg-gray-50/70 transition-colors">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="exam.status === 'locked' ? 'bg-blue-50' : 'bg-emerald-50'">
              <Icon
                :name="exam.status === 'locked' ? 'lucide:lock' : 'lucide:check-circle-2'"
                class="w-3.5 h-3.5"
                :class="exam.status === 'locked' ? 'text-blue-400' : 'text-emerald-400'" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate">{{ exam.title }}</p>
              <p class="text-[10px] mt-0.5" :class="exam.status === 'locked' ? 'text-blue-400' : 'text-emerald-400'">
                {{ exam.status === 'locked' ? 'Travado pelo coordenador' : 'Publicado' }}
              </p>
            </div>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full flex-shrink-0"
              :class="statusBadge(exam.status)">
              {{ statusLabel(exam.status) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Progresso geral dos ativos -->
    <div v-if="collecting.length > 0 && !loading"
      class="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 class="text-sm font-semibold text-gray-900 mb-4">Progresso nos simulados ativos</h3>
      <div class="space-y-4">
        <div v-for="exam in collecting" :key="exam.id">
          <div class="flex items-center justify-between mb-1.5">
            <p class="text-xs font-semibold text-gray-700 truncate pr-4">{{ exam.title }}</p>
            <span class="text-xs font-bold flex-shrink-0"
              :class="calcProgresso(exam.id) === 100 ? 'text-emerald-500' : 'text-gray-400'">
              {{ calcProgresso(exam.id) }}%
            </span>
          </div>
          <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-full rounded-full transition-all duration-700"
              :class="calcProgresso(exam.id) === 100 ? 'bg-emerald-400' : 'bg-orange-400'"
              :style="{ width: calcProgresso(exam.id) + '%' }" />
          </div>
          <div class="flex items-center justify-between mt-1">
            <span class="text-[10px] text-gray-300">
              {{ progressMap[exam.id]?.disciplines?.[0]?.submitted ?? 0 }}/{{ progressMap[exam.id]?.disciplines?.[0]?.quota ?? '?' }} questões
            </span>
            <NuxtLink v-if="calcProgresso(exam.id) < 100"
              :to="`/dashboard/professor/simulados/${exam.id}`"
              class="text-[10px] font-semibold text-orange-500 hover:text-orange-600 transition-colors">
              Continuar →
            </NuxtLink>
            <span v-else class="text-[10px] font-semibold text-emerald-500 flex items-center gap-0.5">
              <Icon name="lucide:check" class="w-3 h-3" /> Completo
            </span>
          </div>
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
const loading     = ref(true)

const firstName = computed(() => user.value?.name?.split(' ')[0] ?? '')

const collecting = computed(() => exams.value.filter(e => e.status === 'collecting'))

const pendentes = computed(() =>
  collecting.value.filter(e => {
    const prog = progressMap.value[e.id]
    if (!prog) return true
    const disc = prog.disciplines?.[0]
    return !disc || disc.submitted < disc.quota
  })
)

const concluidos = computed(() =>
  exams.value.filter(e => ['locked', 'published'].includes(e.status))
)

const statCards = computed(() => [
  { label: 'Simulados atribuídos', value: exams.value.length,    icon: 'lucide:file-text',     iconBg: 'bg-gray-50',    iconColor: 'text-gray-500',    bar: 'bg-gray-200' },
  { label: 'Questões pendentes',   value: pendentes.value.length, icon: 'lucide:alert-circle',   iconBg: 'bg-amber-50',   iconColor: 'text-amber-500',   bar: 'bg-amber-400' },
  { label: 'Travados',             value: exams.value.filter(e => e.status === 'locked').length,
                                                                   icon: 'lucide:lock',           iconBg: 'bg-blue-50',    iconColor: 'text-blue-500',    bar: 'bg-blue-400' },
  { label: 'Minhas turmas',        value: classes.value.length,   icon: 'lucide:users',          iconBg: 'bg-orange-50',  iconColor: 'text-orange-500',  bar: 'bg-orange-400' },
])

function calcProgresso(id: number) {
  const prog = progressMap.value[id]
  const disc = prog?.disciplines?.[0]
  if (!disc?.quota) return 0
  return Math.min(100, Math.round(disc.submitted / disc.quota * 100))
}

function statusLabel(s: string) {
  return { collecting: 'Em coleta', locked: 'Travado', published: 'Publicado', draft: 'Rascunho' }[s] ?? s
}
function statusBadge(s: string) {
  return { collecting: 'bg-amber-50 text-amber-700', locked: 'bg-blue-50 text-blue-700', published: 'bg-emerald-50 text-emerald-700' }[s] ?? 'bg-gray-50 text-gray-500'
}

onMounted(async () => {
  const [examList, classList] = await Promise.allSettled([
    get<any[]>('/exams/'),
    get<any[]>('/school/classes'),
  ])

  if (examList.status === 'fulfilled') exams.value = examList.value
  if (classList.status === 'fulfilled') classes.value = classList.value

  loading.value = false

  // Carrega progresso dos collecting
  const col = exams.value.filter(e => e.status === 'collecting')
  const results = await Promise.allSettled(col.map(e => get<any>(`/exams/${e.id}/progress`)))
  col.forEach((e, i) => {
    const r = results[i]
    if (r.status === 'fulfilled') progressMap.value[e.id] = r.value
  })
})
</script>