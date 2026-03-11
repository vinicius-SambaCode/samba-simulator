<!-- pages/dashboard/coordenador/questoes.vue -->
<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="animate-fade-in">
      <h2 class="text-xl font-black text-gray-900 tracking-tight">Questões</h2>
      <p class="text-sm text-gray-400 mt-0.5">
        <span v-if="!loading">{{ questoesFiltradas.length }} {{ questoesFiltradas.length !== 1 ? 'questões encontradas' : 'questão encontrada' }}</span>
        <span v-else class="inline-block w-40 h-4 bg-gray-100 rounded animate-pulse" />
      </p>
    </div>

    <!-- Filtros -->
    <div class="bg-white rounded-2xl border border-gray-100 p-4 space-y-3 animate-fade-up" style="animation-delay:40ms">
      <!-- Busca -->
      <div class="relative">
        <Icon name="lucide:search" class="w-4 h-4 text-gray-300 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input v-model="busca"
          class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all"
          placeholder="Buscar no enunciado..." />
        <button v-if="busca" class="absolute right-3 top-1/2 -translate-y-1/2" @click="busca = ''">
          <Icon name="lucide:x" class="w-3.5 h-3.5 text-gray-300 hover:text-gray-500" />
        </button>
      </div>

      <!-- Linha de filtros -->
      <div class="flex flex-wrap gap-2">
        <select v-model="filtroExam"
          class="text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600">
          <option value="">Todos os simulados</option>
          <option v-for="e in exams" :key="e.id" :value="e.id">{{ e.title }}</option>
        </select>

        <select v-model="filtroDisc"
          class="text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600">
          <option value="">Todas as disciplinas</option>
          <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>

        <select v-model="filtroState"
          class="text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600">
          <option value="">Todos os estados</option>
          <option value="submitted">Enviada</option>
          <option value="approved">Aprovada</option>
          <option value="draft">Rascunho</option>
          <option value="rejected">Rejeitada</option>
        </select>

        <select v-model="filtroGabarito"
          class="text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600">
          <option value="">Com e sem gabarito</option>
          <option value="com">Com gabarito</option>
          <option value="sem">Sem gabarito</option>
        </select>

        <!-- Limpar filtros -->
        <button v-if="filtroAtivo"
          class="flex items-center gap-1.5 text-xs font-bold text-gray-400 hover:text-gray-600 px-3 py-2 rounded-xl hover:bg-gray-50 border border-gray-200 transition-all"
          @click="limparFiltros">
          <Icon name="lucide:x" class="w-3 h-3" />
          Limpar
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i"
        class="bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="`height:160px; animation-delay:${i*50}ms`" />
    </div>

    <!-- Empty -->
    <div v-else-if="!questoesFiltradas.length"
      class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-in">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:file-x" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">
        {{ filtroAtivo ? 'Nenhuma questão com esses filtros' : 'Nenhuma questão enviada ainda' }}
      </p>
      <button v-if="filtroAtivo" class="text-xs font-bold text-blue-500 hover:text-blue-600 mt-1"
        @click="limparFiltros">Limpar filtros</button>
    </div>

    <!-- Lista -->
    <div v-else class="space-y-3">
      <div v-for="(q, idx) in questoesFiltradas" :key="q.id"
        class="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:border-gray-200 hover:shadow-sm transition-all duration-200 animate-fade-up"
        :style="`animation-delay:${Math.min(idx, 8) * 40}ms`">

        <!-- Meta linha -->
        <div class="flex items-center gap-2 px-5 py-3 border-b border-gray-50 flex-wrap">
          <!-- Número -->
          <span class="text-[11px] font-black text-gray-300 tabular-nums w-6">#{{ q.id }}</span>

          <!-- Simulado -->
          <NuxtLink :to="`/dashboard/coordenador/simulados/${q.exam_id}`"
            class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-gray-50 text-gray-500 hover:bg-gray-100 transition-colors flex items-center gap-1">
            <Icon name="lucide:file-text" class="w-3 h-3" />
            {{ examTitle(q.exam_id) }}
          </NuxtLink>

          <!-- Disciplina -->
          <span class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
            {{ disciplineName(q.discipline_id) }}
          </span>

          <!-- Turma -->
          <span class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-violet-50 text-violet-700">
            {{ className(q.class_id) }}
          </span>

          <!-- Estado -->
          <span class="text-[11px] font-bold px-2.5 py-1 rounded-full" :class="stateBadge(q.state)">
            {{ stateLabel(q.state) }}
          </span>

          <!-- Gabarito -->
          <span v-if="q.correct_label"
            class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 flex items-center gap-1">
            <Icon name="lucide:check" class="w-3 h-3" />
            Gabarito: {{ q.correct_label }}
          </span>
          <span v-else class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-amber-50 text-amber-600">
            Sem gabarito
          </span>

          <!-- Autor -->
          <span class="text-[11px] text-gray-400 ml-auto">
            {{ authorName(q.author_user_id) }}
          </span>
        </div>

        <!-- Enunciado -->
        <div class="px-5 py-4">
          <p class="text-sm text-gray-800 font-medium leading-relaxed mb-4">
            <span v-if="busca" v-html="highlight(q.stem, busca)" />
            <span v-else>{{ q.stem }}</span>
          </p>

          <!-- Alternativas -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            <div v-for="opt in q.options" :key="opt.label"
              class="flex items-start gap-2 px-3 py-2 rounded-xl text-xs border transition-colors"
              :class="q.correct_label === opt.label
                ? 'bg-emerald-50 border-emerald-100'
                : 'bg-gray-50 border-gray-100'">
              <span class="font-black flex-shrink-0 mt-0.5"
                :class="q.correct_label === opt.label ? 'text-emerald-600' : 'text-gray-400'">
                {{ opt.label }})
              </span>
              <span :class="q.correct_label === opt.label ? 'text-emerald-700' : 'text-gray-600'">
                {{ opt.text }}
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get } = useApi()

const exams       = ref<any[]>([])
const disciplines = ref<any[]>([])
const allClasses  = ref<any[]>([])
const teachers    = ref<any[]>([])
const allQuestions = ref<any[]>([])
const loading     = ref(true)

// Filtros
const busca         = ref('')
const filtroExam    = ref<number | ''>('')
const filtroDisc    = ref<number | ''>('')
const filtroState   = ref('')
const filtroGabarito = ref('')

const filtroAtivo = computed(() =>
  !!busca.value || filtroExam.value !== '' || filtroDisc.value !== '' || filtroState.value || filtroGabarito.value
)

function limparFiltros() {
  busca.value = ''
  filtroExam.value = ''
  filtroDisc.value = ''
  filtroState.value = ''
  filtroGabarito.value = ''
}

const questoesFiltradas = computed(() => {
  let lista = allQuestions.value

  if (filtroExam.value !== '')    lista = lista.filter(q => q.exam_id === filtroExam.value)
  if (filtroDisc.value !== '')    lista = lista.filter(q => q.discipline_id === filtroDisc.value)
  if (filtroState.value)          lista = lista.filter(q => q.state === filtroState.value)
  if (filtroGabarito.value === 'com') lista = lista.filter(q => !!q.correct_label)
  if (filtroGabarito.value === 'sem') lista = lista.filter(q => !q.correct_label)
  if (busca.value) {
    const q = busca.value.toLowerCase()
    lista = lista.filter(r => r.stem.toLowerCase().includes(q))
  }

  return lista
})

// Lookup helpers
function examTitle(id: number)      { return exams.value.find(e => e.id === id)?.title ?? `Simulado #${id}` }
function disciplineName(id: number) { return disciplines.value.find(d => d.id === id)?.name ?? `Disc. #${id}` }
function className(id: number)      { return allClasses.value.find(c => c.id === id)?.name ?? `Turma #${id}` }
function authorName(id: number)     { return teachers.value.find(t => t.id === id)?.name ?? `Prof. #${id}` }

function stateLabel(s: string) {
  return ({ submitted: 'Enviada', approved: 'Aprovada', draft: 'Rascunho', rejected: 'Rejeitada' } as any)[s] ?? s
}
function stateBadge(s: string) {
  return ({
    submitted: 'bg-amber-50 text-amber-700',
    approved:  'bg-emerald-50 text-emerald-700',
    draft:     'bg-gray-50 text-gray-500',
    rejected:  'bg-red-50 text-red-600',
  } as any)[s] ?? 'bg-gray-50 text-gray-500'
}

function highlight(text: string, query: string) {
  if (!query) return text
  const esc = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${esc})`, 'gi'),
    '<mark class="bg-yellow-100 text-yellow-800 rounded px-0.5">$1</mark>')
}

onMounted(async () => {
  const [examsRes, discRes, classesRes, teachersRes] = await Promise.allSettled([
    get<any[]>('/exams/'),
    get<any[]>('/disciplines/'),
    get<any[]>('/school/classes'),
    get<any[]>('/school/teachers'),
  ])

  if (examsRes.status === 'fulfilled')    exams.value       = examsRes.value
  if (discRes.status === 'fulfilled')     disciplines.value = discRes.value
  if (classesRes.status === 'fulfilled')  allClasses.value  = classesRes.value
  if (teachersRes.status === 'fulfilled') teachers.value    = teachersRes.value

  // Busca questões de todos os simulados em paralelo
  if (examsRes.status === 'fulfilled') {
    const results = await Promise.allSettled(
      examsRes.value.map((e: any) => get<any[]>(`/exams/${e.id}/questions`))
    )
    const todas: any[] = []
    for (const r of results) {
      if (r.status === 'fulfilled') todas.push(...r.value)
    }
    // Ordena: mais recentes primeiro (id desc)
    allQuestions.value = todas.sort((a, b) => b.id - a.id)
  }

  loading.value = false
})
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }
</style>