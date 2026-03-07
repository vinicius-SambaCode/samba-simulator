<!-- pages/dashboard/professor/simulados/index.vue -->
<template>
  <div class="max-w-3xl mx-auto space-y-6">

    <div>
      <h2 class="text-2xl font-bold text-gray-900">Meus simulados</h2>
      <p class="text-gray-500 text-sm mt-1">Simulados atribuídos pelo coordenador</p>
    </div>

    <!-- Pendentes -->
    <div v-if="pendentes.length > 0">
      <div class="flex items-center gap-2 mb-3">
        <div class="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        <p class="text-sm font-semibold text-gray-700">Aguardando suas questões ({{ pendentes.length }})</p>
      </div>
      <div class="space-y-3">
        <div
          v-for="s in pendentes"
          :key="s.id"
          class="bg-white rounded-2xl border border-amber-200 p-5 shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" :class="s.cor">
                <Icon :name="s.icon" class="w-5 h-5 text-white" />
              </div>
              <div>
                <p class="text-sm font-bold text-gray-900">{{ s.nome }}</p>
                <p class="text-xs text-gray-500 mt-0.5">{{ s.disciplina }} · {{ s.questoes }} questões para criar</p>
                <div class="flex items-center gap-1.5 mt-2">
                  <Icon name="lucide:clock" class="w-3.5 h-3.5 text-amber-500" />
                  <p class="text-xs text-amber-600 font-medium">Prazo: {{ s.prazo }}</p>
                </div>
              </div>
            </div>
            <NuxtLink
              :to="`/dashboard/professor/simulados/${s.id}`"
              class="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors flex-shrink-0"
            >
              <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
              Criar questões
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Concluídos -->
    <div v-if="concluidos.length > 0">
      <p class="text-sm font-semibold text-gray-700 mb-3">Concluídos</p>
      <div class="space-y-3">
        <div
          v-for="s in concluidos"
          :key="s.id"
          class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm opacity-75"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" :class="s.cor">
                <Icon :name="s.icon" class="w-5 h-5 text-white" />
              </div>
              <div>
                <p class="text-sm font-bold text-gray-900">{{ s.nome }}</p>
                <p class="text-xs text-gray-500 mt-0.5">{{ s.disciplina }} · {{ s.questoes }} questões enviadas</p>
              </div>
            </div>
            <span class="flex items-center gap-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-full">
              <Icon name="lucide:check-circle" class="w-3.5 h-3.5" />
              Enviado
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pendentes.length === 0 && concluidos.length === 0" class="bg-white rounded-2xl border border-dashed border-gray-200 p-12 text-center">
      <Icon name="lucide:inbox" class="w-10 h-10 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-400 text-sm">Nenhum simulado atribuído ainda</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const pendentes = [
  { id: '1', nome: 'Simulado Bimestral — 1º Bimestre 2026', disciplina: 'Matemática', questoes: 10, prazo: '10/03/2026', cor: 'bg-purple-500', icon: 'lucide:calculator' },
  { id: '2', nome: 'Simulado de Recuperação — Fev/2026', disciplina: 'Matemática', questoes: 5, prazo: '08/03/2026', cor: 'bg-purple-500', icon: 'lucide:calculator' },
]

const concluidos = [
  { id: '3', nome: 'Simulado Diagnóstico — Jan/2026', disciplina: 'Matemática', questoes: 8, cor: 'bg-purple-500', icon: 'lucide:calculator' },
]
</script>