<!-- pages/dashboard/professor/simulados/index.vue -->
<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Meus simulados</h2>
        <p class="text-sm text-gray-500 mt-0.5">Simulados em que você foi atribuído</p>
      </div>
      <!-- Indicador de atualização -->
      <button
        class="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600 transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-50"
        :class="{ 'pointer-events-none': loading }"
        @click="recarregar">
        <Icon :name="loading ? 'lucide:loader-2' : 'lucide:refresh-cw'"
          class="w-3.5 h-3.5 transition-transform"
          :class="loading ? 'animate-spin' : 'group-hover:rotate-180'" />
        Atualizar
      </button>
    </div>

    <!-- Filtros -->
    <div class="flex items-center gap-2 flex-wrap">
      <button
        v-for="f in filtros" :key="f.value"
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150"
        :class="filtroAtivo === f.value
          ? 'bg-gray-900 text-white shadow-sm'
          : 'bg-white border border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-700'"
        @click="filtroAtivo = f.value">
        {{ f.label }}
        <span class="ml-1.5 tabular-nums"
          :class="filtroAtivo === f.value ? 'opacity-60' : 'text-gray-400'">
          {{ contarFiltro(f.value) }}
        </span>
      </button>
    </div>

    <!-- Loading skeletons -->
    <Transition name="fade">
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 3" :key="i"
          class="h-20 bg-white rounded-2xl border border-gray-100 animate-pulse"
          :style="{ animationDelay: `${i * 80}ms` }" />
      </div>
    </Transition>

    <!-- Empty state -->
    <Transition name="fade">
      <div v-if="!loading && listaFiltrada.length === 0"
        class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-dashed border-gray-200">
        <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
          <Icon name="lucide:clipboard-list" class="w-7 h-7 text-gray-300" />
        </div>
        <p class="text-sm font-medium text-gray-400">Nenhum simulado encontrado</p>
        <p class="text-xs text-gray-300 mt-1">
          {{ filtroAtivo === 'todos' ? 'Aguarde ser atribuído pelo coordenador' : 'Tente outro filtro' }}
        </p>
      </div>
    </Transition>

    <!-- Lista de simulados -->
    <TransitionGroup v-if="!loading" name="list" tag="div" class="space-y-3">
      <NuxtLink
        v-for="item in listaFiltrada"
        :key="item.exam.id"
        :to="item.exam.status === 'collecting' ? `/dashboard/professor/simulados/${item.exam.id}` : '#'"
        class="flex items-center gap-4 bg-white rounded-2xl border border-gray-100 px-5 py-4 transition-all duration-200 group block"
        :class="item.exam.status === 'collecting'
          ? 'hover:border-gray-200 hover:shadow-md hover:-translate-y-0.5 cursor-pointer'
          : 'cursor-default'">

        <!-- Ícone de status -->
        <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200"
          :class="iconBg(item.exam.status, item.progresso)">
          <Icon :name="iconName(item.exam.status, item.progresso)"
            class="w-5 h-5 transition-colors"
            :class="[iconColor(item.exam.status, item.progresso), item.progresso > 0 && item.progresso < 100 ? 'animate-pulse' : '']" />
        </div>

        <!-- Conteúdo -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1.5">
            <p class="text-sm font-semibold text-gray-900 truncate">{{ item.exam.title }}</p>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full flex-shrink-0"
              :class="statusBadge(item.exam.status)">
              {{ statusLabel(item.exam.status) }}
            </span>
          </div>

          <!-- Barra de progresso (apenas quando collecting) -->
          <template v-if="item.exam.status === 'collecting' && item.progressInfo">
            <div class="flex items-center gap-2.5">
              <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-700 ease-out"
                  :class="item.progresso === 100 ? 'bg-emerald-400' : 'bg-blue-400'"
                  :style="{ width: item.progresso + '%' }" />
              </div>
              <span class="text-[11px] font-medium flex-shrink-0 tabular-nums"
                :class="item.progresso === 100 ? 'text-emerald-600' : 'text-gray-400'">
                {{ item.progressInfo.submitted }}/{{ item.progressInfo.quota }}
              </span>
              <!-- Faltam X -->
              <span v-if="item.progresso < 100"
                class="text-[10px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded-full font-medium flex-shrink-0">
                faltam {{ item.progressInfo.quota - item.progressInfo.submitted }}
              </span>
            </div>
          </template>

          <!-- Info simples para outros status -->
          <p v-else class="text-xs text-gray-400">
            {{ item.exam.options_count }} alternativas
            <template v-if="item.progressInfo">
              · {{ item.progressInfo.submitted }} questão(ões) adicionada(s)
            </template>
          </p>
        </div>

        <!-- Seta de navegação -->
        <Icon v-if="item.exam.status === 'collecting'"
          name="lucide:chevron-right"
          class="w-4 h-4 text-gray-300 group-hover:text-gray-500 group-hover:translate-x-0.5 transition-all flex-shrink-0" />

        <!-- Lock para outros status -->
        <Icon v-else
          name="lucide:lock"
          class="w-3.5 h-3.5 text-gray-200 flex-shrink-0" />
      </NuxtLink>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()
const items = ref<any[]>([])
const loading = ref(true)
const filtroAtivo = ref('todos')

const filtros = [
  { value: 'todos',      label: 'Todos' },
  { value: 'collecting', label: 'Em coleta' },
  { value: 'concluido',  label: 'Concluídos' },
  { value: 'outros',     label: 'Aguardando' },
]

// Ordena: collecting primeiro, depois por progresso decrescente
const listaOrdenada = computed(() =>
  [...items.value].sort((a, b) => {
    if (a.exam.status === 'collecting' && b.exam.status !== 'collecting') return -1
    if (a.exam.status !== 'collecting' && b.exam.status === 'collecting') return 1
    return b.progresso - a.progresso
  })
)

const listaFiltrada = computed(() => {
  if (filtroAtivo.value === 'todos') return listaOrdenada.value
  if (filtroAtivo.value === 'collecting') return listaOrdenada.value.filter(i => i.exam.status === 'collecting')
  if (filtroAtivo.value === 'concluido') return listaOrdenada.value.filter(i => i.progresso === 100)
  // 'outros' = locked, published, etc
  return listaOrdenada.value.filter(i => i.exam.status !== 'collecting')
})

function contarFiltro(v: string) {
  if (v === 'todos') return items.value.length
  if (v === 'collecting') return items.value.filter(i => i.exam.status === 'collecting').length
  if (v === 'concluido') return items.value.filter(i => i.progresso === 100).length
  return items.value.filter(i => i.exam.status !== 'collecting').length
}

function statusLabel(s: string) {
  const map: Record<string, string> = {
    collecting: 'Em coleta',
    locked: 'Aguardando',
    published: 'Publicado',
    generated: 'Resultados',
    draft: 'Rascunho',
  }
  return map[s] ?? s
}

function statusBadge(s: string) {
  const map: Record<string, string> = {
    collecting: 'bg-amber-50 text-amber-700',
    locked: 'bg-blue-50 text-blue-600',
    published: 'bg-emerald-50 text-emerald-700',
    generated: 'bg-purple-50 text-purple-700',
    draft: 'bg-gray-50 text-gray-500',
  }
  return map[s] ?? 'bg-gray-50 text-gray-500'
}

function iconName(status: string, progresso: number) {
  if (status === 'published' || status === 'generated') return 'lucide:check-circle-2'
  if (status !== 'collecting') return 'lucide:clock'
  if (progresso === 100) return 'lucide:check-circle-2'
  if (progresso > 0) return 'lucide:circle-dot'
  return 'lucide:clipboard-list'
}

function iconBg(status: string, progresso: number) {
  if (status === 'published' || status === 'generated') return 'bg-emerald-50'
  if (status !== 'collecting') return 'bg-blue-50'
  if (progresso === 100) return 'bg-emerald-50'
  if (progresso > 0) return 'bg-amber-50'
  return 'bg-gray-50'
}

function iconColor(status: string, progresso: number) {
  if (status === 'published' || status === 'generated') return 'text-emerald-500'
  if (status !== 'collecting') return 'text-blue-400'
  if (progresso === 100) return 'text-emerald-500'
  if (progresso > 0) return 'text-amber-500'
  return 'text-gray-400'
}

async function carregarDados() {
  loading.value = true
  try {
    const exams = await get<any[]>('/exams/')

    // Busca progresso de todos os simulados com atribuição, não só collecting
    const progressResults = await Promise.allSettled(
      exams.map(e => get<any>(`/exams/${e.id}/progress`))
    )
    const assignmentResults = await Promise.allSettled(
      exams.map(e => get<any>(`/exams/${e.id}/my-assignment`))
    )

    items.value = exams.map((exam, i) => {
      const progRes = progressResults[i]
      const assRes  = assignmentResults[i]

      const prog = progRes.status === 'fulfilled' ? progRes.value : null
      const myAssignment = assRes.status === 'fulfilled' ? assRes.value : null

      let progressInfo: any = null
      let progresso = 0

      if (prog?.disciplines?.length) {
        const discId = myAssignment?.discipline_id
        const myDisc = discId
          ? prog.disciplines.find((d: any) => d.discipline_id === discId) ?? prog.disciplines[0]
          : prog.disciplines[0]

        progressInfo = {
          submitted: myDisc.submitted ?? 0,
          quota: myDisc.quota ?? 0,
        }
        if (progressInfo.quota > 0) {
          progresso = Math.min(100, Math.round((progressInfo.submitted / progressInfo.quota) * 100))
        }
      }

      return { exam, progressInfo, progresso }
    })
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function recarregar() {
  await carregarDados()
}

onMounted(carregarDados)

// Recarrega ao voltar para a página (ex: após editar questões)
onActivated(carregarDados)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.list-enter-active {
  transition: all 0.25s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
.list-move {
  transition: transform 0.3s ease;
}
</style>