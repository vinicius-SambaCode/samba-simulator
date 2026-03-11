<!-- pages/dashboard/root/usuarios.vue -->
<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Usuários</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gestão de professores e coordenadores</p>
      </div>
    </div>

    <!-- Busca + filtro -->
    <div class="flex items-center gap-3">
      <div class="relative flex-1 max-w-xs">
        <Icon name="lucide:search" class="w-4 h-4 text-gray-300 absolute left-3 top-1/2 -translate-y-1/2" />
        <input v-model="busca"
          class="w-full pl-9 pr-4 py-2 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
          placeholder="Buscar por nome..." />
      </div>
      <div class="flex items-center gap-1.5">
        <button v-for="f in filtros" :key="f.value"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
          :class="filtroAtivo === f.value ? 'bg-gray-900 text-white' : 'bg-white border border-gray-200 text-gray-500 hover:border-gray-300'"
          @click="filtroAtivo = f.value">
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-2">
      <div v-for="i in 5" :key="i" class="h-14 bg-white rounded-xl border border-gray-100 animate-pulse" />
    </div>

    <!-- Lista -->
    <div v-else class="bg-white rounded-2xl border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-50">
              <th class="text-left text-[11px] font-semibold text-gray-400 px-5 py-3 uppercase tracking-wider">Nome</th>
              <th class="text-left text-[11px] font-semibold text-gray-400 px-4 py-3 uppercase tracking-wider hidden sm:table-cell">Email</th>
              <th class="text-left text-[11px] font-semibold text-gray-400 px-4 py-3 uppercase tracking-wider">Perfil</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-if="listaFiltrada.length === 0">
              <td colspan="3" class="text-center py-12 text-sm text-gray-400">Nenhum usuário encontrado</td>
            </tr>
            <tr v-for="u in listaFiltrada" :key="u.id" class="hover:bg-gray-50/50 transition-colors">
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                    :class="roleBg(u.roles)">
                    {{ iniciais(u.name) }}
                  </div>
                  <p class="text-sm font-medium text-gray-900">{{ u.name }}</p>
                </div>
              </td>
              <td class="px-4 py-3.5 hidden sm:table-cell">
                <p class="text-sm text-gray-400">{{ u.email }}</p>
              </td>
              <td class="px-4 py-3.5">
                <div class="flex gap-1 flex-wrap">
                  <span v-for="r in u.roles" :key="r"
                    class="text-[10px] font-semibold px-2 py-0.5 rounded-full" :class="roleBadge(r)">
                    {{ roleLabel(r) }}
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
const { get } = useApi()

const usuarios = ref<any[]>([])
const loading = ref(true)
const busca = ref('')
const filtroAtivo = ref('todos')

const filtros = [
  { value: 'todos', label: 'Todos' },
  { value: 'TEACHER', label: 'Professores' },
  { value: 'COORDINATOR', label: 'Coordenadores' },
]

const listaFiltrada = computed(() => {
  let lista = usuarios.value
  if (filtroAtivo.value !== 'todos')
    lista = lista.filter(u => u.roles?.includes(filtroAtivo.value))
  if (busca.value.trim())
    lista = lista.filter(u => u.name.toLowerCase().includes(busca.value.toLowerCase()))
  return lista
})

function iniciais(name: string) {
  return name.split(' ').slice(0, 2).map(n => n[0]).join('')
}
function roleLabel(r: string) {
  return { TEACHER: 'Professor', COORDINATOR: 'Coordenador', ADMIN: 'Admin' }[r] ?? r
}
function roleBadge(r: string) {
  return { TEACHER: 'bg-orange-100 text-orange-700', COORDINATOR: 'bg-emerald-100 text-emerald-700', ADMIN: 'bg-purple-100 text-purple-700' }[r] ?? 'bg-gray-100 text-gray-500'
}
function roleBg(roles: string[]) {
  if (roles?.includes('ADMIN')) return 'bg-purple-500'
  if (roles?.includes('COORDINATOR')) return 'bg-emerald-500'
  return 'bg-orange-500'
}

onMounted(async () => {
  try {
    // /users/teachers retorna só teachers — para root precisamos de todos
    // Usamos o endpoint de professores e depois de coordenadores
    const teachers = await get<any[]>('/users/teachers').catch(() => [])
    // Sem endpoint de all users ainda, exibe o que tiver
    usuarios.value = teachers
  } catch {
    usuarios.value = []
  } finally {
    loading.value = false
  }
})
</script>