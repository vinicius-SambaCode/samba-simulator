<!-- pages/dashboard/professor/index.vue -->
<template>
  <div class="space-y-8">

    <!-- Cabeçalho -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900">Olá, {{ user?.name?.split(' ')[0] }} 👋</h2>
      <p class="text-gray-500 mt-1">{{ user?.escola }}</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <DashboardStatCard v-for="stat in stats" :key="stat.label" v-bind="stat" />
    </div>

    <!-- Simulados pendentes com destaque -->
    <div v-if="simuladosPendentes.length > 0" class="bg-amber-50 border border-amber-200 rounded-2xl p-5">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        <h3 class="font-semibold text-amber-800">Aguardando suas questões ({{ simuladosPendentes.length }})</h3>
      </div>
      <div class="space-y-3">
        <div
          v-for="s in simuladosPendentes"
          :key="s.id"
          class="bg-white rounded-xl border border-amber-200 p-4 flex items-center justify-between gap-4"
        >
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" :class="s.cor">
              <Icon :name="s.icon" class="w-4 h-4 text-white" />
            </div>
            <div>
              <p class="text-sm font-semibold text-gray-900">{{ s.nome }}</p>
              <p class="text-xs text-gray-500">{{ s.disciplina }} · {{ s.questoes }} questões · prazo <span class="text-amber-600 font-medium">{{ s.prazo }}</span></p>
            </div>
          </div>
          <NuxtLink
            :to="`/dashboard/professor/simulados/${s.id}`"
            class="flex items-center gap-1.5 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold rounded-lg transition-colors flex-shrink-0"
          >
            <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
            Cadastrar questões
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Turmas + Simulados recentes -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">

      <!-- Turmas -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <div class="flex items-center justify-between mb-5">
          <h3 class="font-semibold text-gray-900">Minhas turmas</h3>
          <NuxtLink to="/dashboard/professor/minhas-turmas" class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
            Ver todas <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </NuxtLink>
        </div>
        <div class="space-y-3">
          <div
            v-for="turma in turmas"
            :key="turma.id"
            class="flex items-center gap-4 p-3 rounded-xl border border-gray-100 hover:border-orange-200 hover:bg-orange-50/30 transition-colors cursor-pointer"
          >
            <div class="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center flex-shrink-0">
              <span class="text-xs font-bold text-orange-600">{{ turma.nome }}</span>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">{{ turma.descricao }}</p>
              <p class="text-xs text-gray-400">{{ turma.alunos }} alunos</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-bold" :class="turma.media >= 70 ? 'text-emerald-600' : 'text-red-500'">
                {{ turma.media }}%
              </p>
              <p class="text-xs text-gray-400">média</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Simulados recentes -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <div class="flex items-center justify-between mb-5">
          <h3 class="font-semibold text-gray-900">Histórico de simulados</h3>
          <NuxtLink to="/dashboard/professor/simulados" class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
            Ver todos <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </NuxtLink>
        </div>
        <div class="space-y-3">
          <div
            v-for="simulado in simulados"
            :key="simulado.id"
            class="p-4 rounded-xl border border-gray-100 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between mb-1">
              <p class="text-sm font-semibold text-gray-900 pr-2">{{ simulado.titulo }}</p>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0" :class="simulado.badgeClass">
                {{ simulado.status }}
              </span>
            </div>
            <p class="text-xs text-gray-400">{{ simulado.disciplina }} · {{ simulado.questoes }} questões · {{ simulado.data }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Prazos -->
    <div class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
      <h4 class="font-semibold text-gray-900 mb-3">Próximos prazos</h4>
      <div class="space-y-3">
        <div v-for="prazo in prazos" :key="prazo.id" class="flex items-center gap-3">
          <div class="w-2 h-2 rounded-full flex-shrink-0" :class="prazo.cor" />
          <div class="flex-1">
            <p class="text-xs font-medium text-gray-700">{{ prazo.titulo }}</p>
            <p class="text-xs text-gray-400">{{ prazo.data }}</p>
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
  { label: 'Questões cadastradas', value: '7', change: 'de 15 no simulado atual', changePositive: null, icon: 'lucide:help-circle', iconBg: 'bg-orange-50', iconColor: 'text-orange-500' },
  { label: 'Total de alunos', value: '112', change: '4 turmas ativas', changePositive: null, icon: 'lucide:users', iconBg: 'bg-blue-50', iconColor: 'text-blue-600' },
  { label: 'Simulados concluídos', value: '3', change: '+1 este mês', changePositive: true, icon: 'lucide:check-circle', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-600' },
]

const simuladosPendentes = [
  { id: '1', nome: 'Simulado Bimestral — 1º Bimestre 2026', disciplina: 'Matemática', questoes: 10, prazo: '10/03/2026', cor: 'bg-purple-500', icon: 'lucide:calculator' },
  { id: '2', nome: 'Simulado de Recuperação — Fev/2026', disciplina: 'Matemática', questoes: 5, prazo: '08/03/2026', cor: 'bg-purple-500', icon: 'lucide:calculator' },
]

const turmas = [
  { id: 1, nome: '7ºA', descricao: '7º Ano A — Manhã', alunos: 28, media: 74 },
  { id: 2, nome: '7ºB', descricao: '7º Ano B — Tarde', alunos: 30, media: 68 },
  { id: 3, nome: '8ºA', descricao: '8º Ano A — Manhã', alunos: 27, media: 81 },
  { id: 4, nome: '9ºA', descricao: '9º Ano A — Tarde', alunos: 27, media: 59 },
]

const simulados = [
  { id: 1, titulo: 'Frações e Decimais', disciplina: 'Matemática', questoes: 10, data: '28/02/2026', status: 'Enviado', badgeClass: 'bg-green-100 text-green-700' },
  { id: 2, titulo: 'Equações do 1º Grau', disciplina: 'Matemática', questoes: 8, data: '20/02/2026', status: 'Enviado', badgeClass: 'bg-green-100 text-green-700' },
  { id: 3, titulo: 'Diagnóstico Janeiro', disciplina: 'Matemática', questoes: 5, data: '10/01/2026', status: 'Enviado', badgeClass: 'bg-green-100 text-green-700' },
]

const prazos = [
  { id: 1, titulo: 'Simulado Bimestral — prazo questões', data: '08/03/2026', cor: 'bg-red-400' },
  { id: 2, titulo: 'Simulado Recuperação — prazo questões', data: '10/03/2026', cor: 'bg-amber-400' },
  { id: 3, titulo: 'Reunião pedagógica', data: '20/03/2026', cor: 'bg-blue-400' },
]
</script>