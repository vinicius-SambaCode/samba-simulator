<!-- pages/dashboard/coordenador.vue -->
<template>
  <div class="space-y-8">

    <!-- Cabeçalho -->
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Olá, {{ user?.name?.split(' ')[0] }} 👋</h2>
        <p class="text-gray-500 mt-1">{{ user?.escola }}</p>
      </div>
      <NuxtLink
        to="/dashboard/coordenador/simulados/novo"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors"
      >
        <Icon name="lucide:plus" class="w-4 h-4" />
        Novo simulado
      </NuxtLink>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <DashboardStatCard v-for="stat in stats" :key="stat.label" v-bind="stat" />
    </div>

    <!-- Simulados em andamento + Professores -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">

      <!-- Simulados -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <div class="flex items-center justify-between mb-5">
          <h3 class="font-semibold text-gray-900">Simulados em andamento</h3>
          <button class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
            Ver todos <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </button>
        </div>
        <div class="space-y-3">
          <div
            v-for="simulado in simuladosAtivos"
            :key="simulado.id"
            class="p-4 rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50/30 transition-colors cursor-pointer"
          >
            <div class="flex items-start justify-between mb-2">
              <div>
                <p class="text-sm font-semibold text-gray-900">{{ simulado.titulo }}</p>
                <p class="text-xs text-gray-400">{{ simulado.professor }} · {{ simulado.turma }}</p>
              </div>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0" :class="simulado.badgeClass">
                {{ simulado.status }}
              </span>
            </div>
            <div class="mt-3">
              <div class="flex justify-between text-xs text-gray-400 mb-1">
                <span>{{ simulado.respondidos }} de {{ simulado.total }} alunos</span>
                <span>{{ Math.round((simulado.respondidos / simulado.total) * 100) }}%</span>
              </div>
              <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-blue-500 rounded-full transition-all"
                  :style="{ width: `${(simulado.respondidos / simulado.total) * 100}%` }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Professores -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <div class="flex items-center justify-between mb-5">
          <h3 class="font-semibold text-gray-900">Professores da escola</h3>
          <button class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
            Gerenciar <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </button>
        </div>
        <div class="space-y-3">
          <div
            v-for="prof in professores"
            :key="prof.id"
            class="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
          >
            <div class="w-9 h-9 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 text-sm font-bold flex-shrink-0">
              {{ prof.nome.split(' ').slice(0, 2).map((n: string) => n[0]).join('') }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ prof.nome }}</p>
              <p class="text-xs text-gray-400">{{ prof.disciplina }} · {{ prof.turmas }} turmas</p>
            </div>
            <div class="text-right flex-shrink-0">
              <p class="text-sm font-semibold text-gray-900">{{ prof.simulados }}</p>
              <p class="text-xs text-gray-400">simulados</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Desempenho por turma -->
    <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
      <div class="flex items-center justify-between mb-5">
        <h3 class="font-semibold text-gray-900">Desempenho por turma</h3>
        <button class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <Icon name="lucide:download" class="w-3 h-3" /> Relatório completo
        </button>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="turma in turmas" :key="turma.nome" class="p-4 rounded-xl bg-gray-50 border border-gray-100">
          <p class="text-sm font-semibold text-gray-900">{{ turma.nome }}</p>
          <p class="text-xs text-gray-400 mb-3">{{ turma.alunos }} alunos</p>
          <div class="flex items-end gap-1 h-12">
            <div
              v-for="(h, i) in turma.historico"
              :key="i"
              class="flex-1 bg-emerald-400 rounded-sm opacity-60 hover:opacity-100 transition-opacity"
              :style="{ height: `${h}%` }"
            />
          </div>
          <div class="flex justify-between mt-2">
            <span class="text-xs text-gray-400">média</span>
            <span class="text-sm font-bold" :class="turma.media >= 70 ? 'text-emerald-600' : 'text-red-500'">
              {{ turma.media }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })
const { user } = useAuth()

const stats = [
  { label: 'Simulados este mês', value: '8', change: '+2 vs mês anterior', changePositive: true, icon: 'lucide:file-text', iconBg: 'bg-blue-50', iconColor: 'text-blue-600' },
  { label: 'Total de alunos', value: '620', change: '12 turmas ativas', changePositive: null, icon: 'lucide:users', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-600' },
  { label: 'Média geral', value: '72%', change: '+4% vs mês anterior', changePositive: true, icon: 'lucide:trending-up', iconBg: 'bg-purple-50', iconColor: 'text-purple-600' },
]

const simuladosAtivos = [
  { id: 1, titulo: 'Matemática — Frações e Decimais', professor: 'Carlos Mendes', turma: '7º A', status: 'Em andamento', badgeClass: 'bg-blue-100 text-blue-700', respondidos: 18, total: 25 },
  { id: 2, titulo: 'Português — Interpretação de Texto', professor: 'Ana Lima', turma: '8º B', status: 'Em andamento', badgeClass: 'bg-blue-100 text-blue-700', respondidos: 22, total: 28 },
  { id: 3, titulo: 'Ciências — Sistema Solar', professor: 'Roberto Dias', turma: '6º A', status: 'Encerrado', badgeClass: 'bg-green-100 text-green-700', respondidos: 30, total: 30 },
]

const professores = [
  { id: 1, nome: 'Carlos Mendes', disciplina: 'Matemática', turmas: 4, simulados: 12 },
  { id: 2, nome: 'Ana Lima', disciplina: 'Português', turmas: 3, simulados: 9 },
  { id: 3, nome: 'Roberto Dias', disciplina: 'Ciências', turmas: 3, simulados: 7 },
  { id: 4, nome: 'Paula Ferreira', disciplina: 'História', turmas: 2, simulados: 4 },
]

const turmas = [
  { nome: '6º A', alunos: 32, media: 68, historico: [45, 60, 55, 68, 72, 68] },
  { nome: '7º A', alunos: 28, media: 74, historico: [60, 65, 70, 68, 74, 74] },
  { nome: '8º B', alunos: 30, media: 81, historico: [70, 72, 75, 78, 80, 81] },
  { nome: '9º A', alunos: 25, media: 63, historico: [50, 55, 60, 58, 62, 63] },
]
</script>