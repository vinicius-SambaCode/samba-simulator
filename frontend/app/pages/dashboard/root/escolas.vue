<!-- pages/dashboard/root/escolas.vue -->
<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Escolas</h2>
        <p class="text-sm text-gray-500 mt-0.5">Unidades escolares cadastradas na rede</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <div class="bg-white rounded-2xl border border-gray-100 p-4">
        <p class="text-2xl font-bold text-gray-900">{{ turmas.length }}</p>
        <p class="text-xs text-gray-400 mt-0.5">Turmas ativas</p>
        <div class="w-6 h-1 rounded-full mt-2 bg-blue-400" />
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 p-4">
        <p class="text-2xl font-bold text-gray-900">{{ disciplinas.length }}</p>
        <p class="text-xs text-gray-400 mt-0.5">Disciplinas</p>
        <div class="w-6 h-1 rounded-full mt-2 bg-emerald-400" />
      </div>
      <div class="bg-white rounded-2xl border border-gray-100 p-4 col-span-2 sm:col-span-1">
        <p class="text-2xl font-bold text-gray-900">—</p>
        <p class="text-xs text-gray-400 mt-0.5">Escolas cadastradas</p>
        <div class="w-6 h-1 rounded-full mt-2 bg-purple-400" />
      </div>
    </div>

    <!-- Turmas -->
    <div>
      <h3 class="text-sm font-semibold text-gray-700 mb-3">Turmas</h3>
      <div v-if="loading" class="space-y-2">
        <div v-for="i in 4" :key="i" class="h-12 bg-white rounded-xl border border-gray-100 animate-pulse" />
      </div>
      <div v-else class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-50">
              <th class="text-left text-[11px] font-semibold text-gray-400 px-5 py-3 uppercase tracking-wider">Turma</th>
              <th class="text-left text-[11px] font-semibold text-gray-400 px-4 py-3 uppercase tracking-wider hidden sm:table-cell">ID</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-if="turmas.length === 0">
              <td colspan="2" class="text-center py-10 text-sm text-gray-400">Nenhuma turma encontrada</td>
            </tr>
            <tr v-for="t in turmas" :key="t.id" class="hover:bg-gray-50/50">
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <div class="w-7 h-7 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Icon name="lucide:users" class="w-3.5 h-3.5 text-blue-500" />
                  </div>
                  <p class="text-sm font-medium text-gray-900">{{ t.name }}</p>
                </div>
              </td>
              <td class="px-4 py-3.5 hidden sm:table-cell">
                <p class="text-xs text-gray-400 font-mono">#{{ t.id }}</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Disciplinas -->
    <div>
      <h3 class="text-sm font-semibold text-gray-700 mb-3">Disciplinas</h3>
      <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div v-for="i in 8" :key="i" class="h-12 bg-white rounded-xl border border-gray-100 animate-pulse" />
      </div>
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        <div v-for="d in disciplinas" :key="d.id"
          class="bg-white rounded-xl border border-gray-100 px-4 py-3 flex items-center gap-2.5">
          <div class="w-6 h-6 rounded-lg bg-emerald-50 flex items-center justify-center flex-shrink-0">
            <Icon name="lucide:book" class="w-3 h-3 text-emerald-500" />
          </div>
          <p class="text-xs font-medium text-gray-700 truncate">{{ d.name }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()

const turmas = ref<any[]>([])
const disciplinas = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [t, d] = await Promise.all([
      get<any[]>('/school/classes'),
      get<any[]>('/disciplines'),
    ])
    turmas.value = t
    disciplinas.value = d
  } catch {
    turmas.value = []
    disciplinas.value = []
  } finally {
    loading.value = false
  }
})
</script>