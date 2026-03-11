<!-- pages/dashboard/coordenador/alunos.vue -->
<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between animate-fade-in">
      <div>
        <h2 class="text-xl font-black text-gray-900 tracking-tight">Alunos</h2>
        <p class="text-sm text-gray-400 mt-0.5">
          <span v-if="!loading">{{ totalAlunos }} aluno{{ totalAlunos !== 1 ? 's' : '' }} em {{ turmasComAlunos.length }} turma{{ turmasComAlunos.length !== 1 ? 's' : '' }}</span>
          <span v-else class="inline-block w-40 h-4 bg-gray-100 rounded animate-pulse" />
        </p>
      </div>
    </div>

    <!-- Busca + filtro -->
    <div class="flex gap-2 animate-fade-up" style="animation-delay:40ms">
      <div class="relative flex-1">
        <Icon name="lucide:search" class="w-4 h-4 text-gray-300 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input v-model="busca"
          class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all bg-white"
          placeholder="Buscar por nome ou RA..." />
        <button v-if="busca" class="absolute right-3 top-1/2 -translate-y-1/2" @click="busca = ''">
          <Icon name="lucide:x" class="w-3.5 h-3.5 text-gray-300 hover:text-gray-500 transition-colors" />
        </button>
      </div>
      <select v-model="turmaFiltro"
        class="text-sm border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600 min-w-[160px]">
        <option value="">Todas as turmas</option>
        <option v-for="t in allClasses" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i"
        class="bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="`height:${80 + i * 40}px; animation-delay:${i*50}ms`" />
    </div>

    <!-- Empty busca -->
    <div v-else-if="!turmasVisiveis.length"
      class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-in">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:users" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">
        {{ busca ? 'Nenhum aluno encontrado' : 'Nenhuma turma com alunos' }}
      </p>
      <button v-if="busca || turmaFiltro" class="text-xs font-bold text-blue-500 hover:text-blue-600 mt-1"
        @click="busca = ''; turmaFiltro = ''">Limpar filtros</button>
    </div>

    <!-- Turmas -->
    <div v-else class="space-y-4">
      <div v-for="(turma, idx) in turmasVisiveis" :key="turma.id"
        class="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-fade-up hover:border-gray-200 transition-all duration-200"
        :style="`animation-delay:${idx * 50}ms`">

        <!-- Header turma -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50 cursor-pointer select-none"
          @click="toggleTurma(turma.id)">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:users" class="w-4 h-4 text-blue-500" />
            </div>
            <div>
              <p class="text-sm font-black text-gray-900">{{ turma.name }}</p>
              <p class="text-[11px] text-gray-400 mt-0.5">
                {{ turma.grade?.level === 'fundamental' ? 'Ensino Fundamental' : 'Ensino Médio' }}
                <span v-if="turma.grade?.year"> · {{ turma.grade.year }}º ano</span>
              </p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700">
              {{ alunosDaTurma(turma.id, busca).length }} aluno{{ alunosDaTurma(turma.id, busca).length !== 1 ? 's' : '' }}
            </span>
            <Icon
              :name="expanded.has(turma.id) ? 'lucide:chevron-up' : 'lucide:chevron-down'"
              class="w-4 h-4 text-gray-300" />
          </div>
        </div>

        <!-- Tabela de alunos -->
        <div v-if="expanded.has(turma.id)">
          <div class="grid grid-cols-[auto_1fr_auto] text-[11px] font-black text-gray-400 uppercase tracking-wider px-5 py-2.5 bg-gray-50/60 border-b border-gray-50">
            <span class="w-8">#</span>
            <span>Nome</span>
            <span class="text-right">RA</span>
          </div>
          <div class="divide-y divide-gray-50">
            <div v-for="(aluno, i) in alunosDaTurma(turma.id, busca)" :key="aluno.id"
              class="grid grid-cols-[auto_1fr_auto] items-center px-5 py-3 hover:bg-gray-50/50 transition-colors group">
              <span class="w-8 text-xs font-black text-gray-300 tabular-nums">{{ i + 1 }}</span>
              <div class="flex items-center gap-2.5 min-w-0">
                <!-- Inicial avatar -->
                <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-[10px] font-black"
                  :style="`background-color:${avatarColor(aluno.name)}18; color:${avatarColor(aluno.name)}`">
                  {{ aluno.name.trim()[0] }}
                </div>
                <p class="text-sm font-semibold text-gray-800 truncate">
                  <!-- Highlight busca -->
                  <span v-if="busca" v-html="highlight(aluno.name, busca)" />
                  <span v-else>{{ aluno.name }}</span>
                </p>
              </div>
              <span class="text-[11px] font-mono text-gray-400 ml-4 tabular-nums">
                <span v-if="busca" v-html="highlight(aluno.ra, busca)" />
                <span v-else>{{ aluno.ra }}</span>
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

const students   = ref<any[]>([])
const allClasses = ref<any[]>([])
const loading    = ref(true)
const busca      = ref('')
const turmaFiltro = ref<number | ''>('')
const expanded   = ref(new Set<number>())

// Alunos por turma (com filtro de busca)
function alunosDaTurma(classId: number, query: string) {
  const lista = students.value.filter(s => s.class_id === classId)
  if (!query) return lista
  const q = query.toLowerCase()
  return lista.filter(s =>
    s.name.toLowerCase().includes(q) || s.ra.toLowerCase().includes(q)
  )
}

// Turmas que têm alunos (sem filtro)
const turmasComAlunos = computed(() => {
  const ids = new Set(students.value.map(s => s.class_id))
  return allClasses.value.filter(c => ids.has(c.id))
})

const totalAlunos = computed(() => students.value.length)

// Turmas visíveis com filtros aplicados
const turmasVisiveis = computed(() => {
  let lista = turmasComAlunos.value
  if (turmaFiltro.value !== '') {
    lista = lista.filter(c => c.id === turmaFiltro.value)
  }
  if (busca.value) {
    // Mostra só turmas que têm alunos correspondentes à busca
    lista = lista.filter(c => alunosDaTurma(c.id, busca.value).length > 0)
  }
  return lista
})

// Highlight texto buscado
function highlight(text: string, query: string) {
  if (!query) return text
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${escaped})`, 'gi'),
    '<mark class="bg-yellow-100 text-yellow-800 rounded px-0.5">$1</mark>')
}

// Avatar color baseado no nome
const COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#06b6d4','#ec4899','#f97316']
function avatarColor(name: string) {
  let hash = 0
  for (const c of name) hash = (hash * 31 + c.charCodeAt(0)) & 0xffff
  return COLORS[hash % COLORS.length]
}

function toggleTurma(id: number) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
}

onMounted(async () => {
  const [studentsRes, classesRes] = await Promise.allSettled([
    get<any[]>('/school/students'),
    get<any[]>('/school/classes'),
  ])

  if (studentsRes.status === 'fulfilled') students.value   = studentsRes.value
  if (classesRes.status === 'fulfilled')  allClasses.value = classesRes.value

  // Expande a primeira turma com alunos por padrão
  const primeira = allClasses.value.find(c =>
    students.value.some(s => s.class_id === c.id)
  )
  if (primeira) expanded.value.add(primeira.id)

  loading.value = false
})
</script>

<style scoped>
@keyframes fade-in { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes fade-up { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
.animate-fade-in { animation: fade-in 0.3s ease both }
.animate-fade-up { animation: fade-up 0.38s ease both }
</style>