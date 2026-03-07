<!-- layouts/dashboard.vue -->
<template>
  <div class="min-h-screen bg-gray-50 font-sans flex">

    <!-- Overlay mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/40 z-20 md:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      class="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-100 shadow-sm z-30 flex flex-col transition-transform duration-300"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <!-- Logo -->
      <div class="px-6 py-5 border-b border-gray-100">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Icon name="lucide:book-open" class="text-white w-4 h-4" />
          </div>
          <div>
            <p class="text-sm font-bold text-gray-900 leading-tight">SimuladoSP</p>
            <p class="text-xs text-gray-400">SME · São Paulo</p>
          </div>
        </div>
      </div>

      <!-- Usuário -->
      <div class="px-4 py-4 border-b border-gray-100">
        <div class="flex items-center gap-3 p-3 rounded-xl bg-gray-50">
          <div
            class="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
            :class="roleColor"
          >
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-gray-900 truncate">{{ user?.name }}</p>
            <span
              class="inline-block text-xs font-medium px-2 py-0.5 rounded-full"
              :class="roleBadge"
            >
              {{ roleLabel }}
            </span>
          </div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Menu</p>
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
          :class="$route.path === item.to
            ? 'bg-blue-50 text-blue-700'
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'"
        >
          <Icon :name="item.icon" class="w-4 h-4 flex-shrink-0" />
          {{ item.label }}
        </NuxtLink>
      </nav>

      <!-- Logout -->
      <div class="px-3 py-4 border-t border-gray-100">
        <button
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors"
          @click="logout"
        >
          <Icon name="lucide:log-out" class="w-4 h-4" />
          Sair
        </button>
      </div>
    </aside>

    <!-- Conteúdo principal -->
    <div class="flex-1 md:ml-64 flex flex-col min-h-screen">

      <!-- Topbar -->
      <header class="sticky top-0 z-10 bg-white border-b border-gray-100 px-4 md:px-8 h-16 flex items-center gap-4">
        <button
          class="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100"
          @click="sidebarOpen = !sidebarOpen"
        >
          <Icon name="lucide:menu" class="w-5 h-5" />
        </button>

        <div class="flex-1">
          <h1 class="text-base font-semibold text-gray-900">{{ pageTitle }}</h1>
          <p v-if="user?.escola" class="text-xs text-gray-400">{{ user.escola }}</p>
        </div>

        <button class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors">
          <Icon name="lucide:bell" class="w-5 h-5" />
        </button>
      </header>

      <!-- Slot -->
      <main class="flex-1 p-4 md:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const { user, logout } = useAuth()
const route = useRoute()

const sidebarOpen = ref(false)

const roleConfig = computed(() => {
  const configs = {
    root: {
      color: 'bg-purple-600',
      badge: 'bg-purple-100 text-purple-700',
      label: 'Root',
      nav: [
        { to: '/dashboard/root', icon: 'lucide:layout-dashboard', label: 'Painel' },
        { to: '/dashboard/root/escolas', icon: 'lucide:school', label: 'Escolas' },
        { to: '/dashboard/root/usuarios', icon: 'lucide:users', label: 'Usuários' },
        { to: '/dashboard/root/simulados', icon: 'lucide:file-text', label: 'Simulados' },
        { to: '/dashboard/root/relatorios', icon: 'lucide:bar-chart-2', label: 'Relatórios' },
        { to: '/dashboard/root/configuracoes', icon: 'lucide:settings', label: 'Configurações' },
      ],
    },
    coordenador: {
      color: 'bg-emerald-600',
      badge: 'bg-emerald-100 text-emerald-700',
      label: 'Coordenador',
      nav: [
        { to: '/dashboard/coordenador', icon: 'lucide:layout-dashboard', label: 'Painel' },
        { to: '/dashboard/coordenador/turmas', icon: 'lucide:users', label: 'Turmas' },
        { to: '/dashboard/coordenador/simulados', icon: 'lucide:file-text', label: 'Simulados' },
        { to: '/dashboard/coordenador/professores', icon: 'lucide:user-check', label: 'Professores' },
        { to: '/dashboard/coordenador/relatorios', icon: 'lucide:bar-chart-2', label: 'Relatórios' },
      ],
    },
    professor: {
      color: 'bg-orange-500',
      badge: 'bg-orange-100 text-orange-700',
      label: 'Professor',
      nav: [
        { to: '/dashboard/professor', icon: 'lucide:layout-dashboard', label: 'Painel' },
        { to: '/dashboard/professor/minhas-turmas', icon: 'lucide:users', label: 'Minhas Turmas' },
        { to: '/dashboard/professor/simulados', icon: 'lucide:file-text', label: 'Simulados' },
        { to: '/dashboard/professor/questoes', icon: 'lucide:help-circle', label: 'Questões' },
        { to: '/dashboard/professor/resultados', icon: 'lucide:bar-chart-2', label: 'Resultados' },
      ],
    },
  }
  return configs[user.value?.role ?? 'professor']
})

const roleColor = computed(() => roleConfig.value.color)
const roleBadge = computed(() => roleConfig.value.badge)
const roleLabel = computed(() => roleConfig.value.label)
const navItems = computed(() => roleConfig.value.nav)

const userInitials = computed(() =>
  user.value?.name.split(' ').slice(0, 2).map(n => n[0]).join('') ?? '?'
)

const pageTitle = computed(() => {
  const current = navItems.value.find(i => i.to === route.path)
  return current?.label ?? 'Painel'
})
</script>