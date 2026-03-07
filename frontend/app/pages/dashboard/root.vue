<!-- pages/dashboard/root.vue -->
<template>
  <div class="space-y-8">

    <!-- Cabeçalho -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900">Olá, {{ user?.name?.split(' ')[0] }} 👋</h2>
      <p class="text-gray-500 mt-1">Visão geral de toda a rede municipal</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <DashboardStatCard v-for="stat in stats" :key="stat.label" v-bind="stat" />
    </div>

    <!-- Gráfico placeholder + Atividade -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="xl:col-span-2 bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="font-semibold text-gray-900">Simulados por escola</h3>
            <p class="text-sm text-gray-400">Últimos 30 dias</p>
          </div>
          <button class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
            Ver tudo <Icon name="lucide:arrow-right" class="w-3 h-3" />
          </button>
        </div>
        <div class="h-48 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
          <div class="text-center">
            <Icon name="lucide:bar-chart-2" class="w-10 h-10 text-blue-300 mx-auto mb-2" />
            <p class="text-sm text-blue-400">Gráfico — integre com Chart.js ou ApexCharts</p>
          </div>
        </div>
      </div>

      <!-- Atividade recente -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <h3 class="font-semibold text-gray-900 mb-4">Atividade recente</h3>
        <div class="space-y-4">
          <div v-for="activity in recentActivity" :key="activity.id" class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" :class="activity.iconBg">
              <Icon :name="activity.icon" class="w-4 h-4" :class="activity.iconColor" />
            </div>
            <div>
              <p class="text-sm text-gray-700">{{ activity.message }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ activity.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabela de escolas -->
    <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-gray-900">Escolas — status de simulados</h3>
        <NuxtLink to="/dashboard/root/escolas" class="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          Gerenciar <Icon name="lucide:arrow-right" class="w-3 h-3" />
        </NuxtLink>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-gray-100">
              <th class="pb-3 font-medium">Escola</th>
              <th class="pb-3 font-medium">Simulados</th>
              <th class="pb-3 font-medium">Alunos</th>
              <th class="pb-3 font-medium">Último simulado</th>
              <th class="pb-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="escola in escolas" :key="escola.id" class="hover:bg-gray-50">
              <td class="py-3 font-medium text-gray-900">{{ escola.nome }}</td>
              <td class="py-3 text-gray-600">{{ escola.simulados }}</td>
              <td class="py-3 text-gray-600">{{ escola.alunos }}</td>
              <td class="py-3 text-gray-400">{{ escola.ultimoSimulado }}</td>
              <td class="py-3">
                <span class="inline-block text-xs font-medium px-2 py-0.5 rounded-full" :class="escola.badgeClass">
                  {{ escola.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })
const { user } = useAuth()

const stats = [
  { label: 'Total de escolas', value: '142', change: '+3 este mês', changePositive: true, icon: 'lucide:school', iconBg: 'bg-blue-50', iconColor: 'text-blue-600' },
  { label: 'Simulados ativos', value: '38', change: '+12 esta semana', changePositive: true, icon: 'lucide:file-text', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-600' },
  { label: 'Total de alunos', value: '84.201', change: 'Rede municipal', changePositive: null, icon: 'lucide:users', iconBg: 'bg-purple-50', iconColor: 'text-purple-600' },
  { label: 'Questões cadastradas', value: '2.847', change: '+94 este mês', changePositive: true, icon: 'lucide:help-circle', iconBg: 'bg-orange-50', iconColor: 'text-orange-500' },
]

const recentActivity = [
  { id: 1, icon: 'lucide:file-plus', iconBg: 'bg-blue-50', iconColor: 'text-blue-600', message: 'Novo simulado criado na EMEF João Pessoa', time: 'há 2 horas' },
  { id: 2, icon: 'lucide:user-plus', iconBg: 'bg-emerald-50', iconColor: 'text-emerald-600', message: '3 professores cadastrados na rede', time: 'há 5 horas' },
  { id: 3, icon: 'lucide:alert-circle', iconBg: 'bg-amber-50', iconColor: 'text-amber-600', message: 'EMEF Santana sem simulados este mês', time: 'há 1 dia' },
  { id: 4, icon: 'lucide:check-circle', iconBg: 'bg-green-50', iconColor: 'text-green-600', message: 'Relatório mensal gerado com sucesso', time: 'há 2 dias' },
]

const escolas = [
  { id: 1, nome: 'EMEF Prof. João Pessoa', simulados: 8, alunos: 620, ultimoSimulado: '02/03/2026', status: 'Ativo', badgeClass: 'bg-green-100 text-green-700' },
  { id: 2, nome: 'EMEF Santana', simulados: 2, alunos: 480, ultimoSimulado: '10/01/2026', status: 'Inativo', badgeClass: 'bg-red-100 text-red-700' },
  { id: 3, nome: 'EMEF Maria Clara', simulados: 5, alunos: 530, ultimoSimulado: '28/02/2026', status: 'Ativo', badgeClass: 'bg-green-100 text-green-700' },
  { id: 4, nome: 'EMEF Dom Pedro II', simulados: 3, alunos: 390, ultimoSimulado: '15/02/2026', status: 'Pendente', badgeClass: 'bg-yellow-100 text-yellow-700' },
]
</script>