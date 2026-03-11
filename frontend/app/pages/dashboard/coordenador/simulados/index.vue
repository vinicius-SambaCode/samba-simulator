<!-- pages/dashboard/coordenador/simulados/index.vue -->
<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between animate-fade-in">
      <div>
        <h2 class="text-xl font-black text-gray-900 tracking-tight">Simulados</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ exams.length }} simulado{{ exams.length !== 1 ? 's' : '' }} cadastrado{{ exams.length !== 1 ? 's' : '' }}</p>
      </div>
      <NuxtLink
        to="/dashboard/coordenador/simulados/novo"
        class="flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-700 text-white text-sm font-bold rounded-xl transition-all duration-200 hover:scale-[1.02] active:scale-95">
        <Icon name="lucide:plus" class="w-4 h-4" />
        Novo simulado
      </NuxtLink>
    </div>

    <!-- Busca + filtros -->
    <div class="flex flex-col sm:flex-row gap-3 animate-fade-up" style="animation-delay:40ms">
      <!-- Busca -->
      <div class="relative flex-1">
        <Icon name="lucide:search" class="w-4 h-4 text-gray-300 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          v-model="busca"
          class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all bg-white"
          placeholder="Buscar por título ou área..." />
        <button v-if="busca" class="absolute right-3 top-1/2 -translate-y-1/2" @click="busca = ''">
          <Icon name="lucide:x" class="w-3.5 h-3.5 text-gray-300 hover:text-gray-500 transition-colors" />
        </button>
      </div>

      <!-- Filtros de status -->
      <div class="flex items-center gap-1.5">
        <button
          v-for="f in filtros" :key="f.value"
          class="px-3 py-2 rounded-xl text-xs font-bold border-2 transition-all duration-150 whitespace-nowrap"
          :class="filtroAtivo === f.value
            ? 'border-gray-900 bg-gray-900 text-white'
            : 'border-gray-100 bg-white text-gray-500 hover:border-gray-300'"
          @click="filtroAtivo = filtroAtivo === f.value ? '' : f.value">
          {{ f.label }}
          <span v-if="contagemStatus[f.value]"
            class="ml-1 px-1.5 py-0.5 rounded-full text-[10px]"
            :class="filtroAtivo === f.value ? 'bg-white/20' : 'bg-gray-100'">
            {{ contagemStatus[f.value] }}
          </span>
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <div v-for="i in 6" :key="i"
        class="h-40 bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="`animation-delay:${i*50}ms`" />
    </div>

    <!-- Empty -->
    <div v-else-if="examsFiltrados.length === 0"
      class="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-in">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:file-x" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">
        {{ busca || filtroAtivo ? 'Nenhum resultado encontrado' : 'Nenhum simulado cadastrado' }}
      </p>
      <p class="text-xs text-gray-300 mt-1">
        {{ busca || filtroAtivo ? 'Tente outros filtros' : 'Clique em "Novo simulado" para começar' }}
      </p>
    </div>

    <!-- Grid de cards -->
    <div v-else class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <NuxtLink
        v-for="(exam, idx) in examsFiltrados" :key="exam.id"
        :to="`/dashboard/coordenador/simulados/${exam.id}`"
        class="group bg-white rounded-2xl border border-gray-100 p-5 flex flex-col gap-4 hover:border-gray-300 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 animate-fade-up cursor-pointer"
        :style="`animation-delay:${idx*40}ms`">

        <!-- Topo: status + data -->
        <div class="flex items-center justify-between">
          <span class="inline-flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-1 rounded-full"
            :class="statusBadge(exam.status)">
            <span class="w-1.5 h-1.5 rounded-full" :class="statusDot(exam.status)" />
            {{ statusLabel(exam.status) }}
          </span>
          <span class="text-[11px] text-gray-400 font-medium">{{ formatDate(exam.created_at) }}</span>
        </div>

        <!-- Título + área -->
        <div class="flex-1">
          <p class="text-base font-black text-gray-900 group-hover:text-blue-600 transition-colors leading-tight">
            {{ exam.title }}
          </p>
          <p v-if="exam.area" class="text-xs text-gray-400 mt-1 font-medium">{{ exam.area }}</p>
          <p v-else class="text-xs text-gray-300 mt-1 italic">Sem área definida</p>
        </div>

        <!-- Divisor -->
        <div class="h-px bg-gray-50" />

        <!-- Footer: metadados -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1.5">
              <Icon name="lucide:list-ordered" class="w-3.5 h-3.5 text-gray-300" />
              <span class="text-xs font-semibold text-gray-500">{{ exam.options_count }} opções</span>
            </div>
            <div class="flex items-center gap-1.5">
              <Icon name="lucide:users" class="w-3.5 h-3.5 text-gray-300" />
              <span class="text-xs font-semibold text-gray-500">{{ answerSourceLabel(exam.answer_source) }}</span>
            </div>
          </div>
          <Icon name="lucide:arrow-right"
            class="w-4 h-4 text-gray-200 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
        </div>

      </NuxtLink>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()

const exams   = ref<any[]>([])
const loading = ref(true)
const busca   = ref('')
const filtroAtivo = ref('')

const filtros = [
  { value: 'collecting', label: 'Em coleta' },
  { value: 'locked',     label: 'Travado'   },
  { value: 'published',  label: 'Publicado' },
  { value: 'draft',      label: 'Rascunho'  },
]

const contagemStatus = computed(() => {
  const map: Record<string, number> = {}
  for (const e of exams.value) {
    map[e.status] = (map[e.status] ?? 0) + 1
  }
  return map
})

const examsFiltrados = computed(() => {
  let list = exams.value
  if (filtroAtivo.value) list = list.filter(e => e.status === filtroAtivo.value)
  if (busca.value) {
    const q = busca.value.toLowerCase()
    list = list.filter(e =>
      e.title.toLowerCase().includes(q) ||
      (e.area ?? '').toLowerCase().includes(q)
    )
  }
  return list
})

function statusLabel(s: string) {
  return ({ collecting: 'Em coleta', locked: 'Travado', published: 'Publicado', draft: 'Rascunho' } as any)[s] ?? s
}
function statusBadge(s: string) {
  return ({
    collecting: 'bg-amber-50 text-amber-700',
    locked:     'bg-blue-50 text-blue-700',
    published:  'bg-emerald-50 text-emerald-700',
    draft:      'bg-gray-50 text-gray-500',
  } as any)[s] ?? 'bg-gray-50 text-gray-500'
}
function statusDot(s: string) {
  return ({
    collecting: 'bg-amber-400',
    locked:     'bg-blue-400',
    published:  'bg-emerald-400',
    draft:      'bg-gray-300',
  } as any)[s] ?? 'bg-gray-300'
}
function answerSourceLabel(s: string) {
  return ({ teachers: 'Professores', coordinator: 'Coordenador' } as any)[s] ?? s
}
function formatDate(d: string) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    exams.value = await get<any[]>('/exams/')
  } catch {
    exams.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }

.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }
</style>