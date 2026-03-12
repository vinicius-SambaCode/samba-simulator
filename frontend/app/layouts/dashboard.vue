<!-- layouts/dashboard.vue -->
<template>
  <div class="min-h-screen bg-gray-50 font-sans flex" :class="{ 'sidebar-collapsed': !expanded }">

    <!-- Overlay mobile -->
    <Transition name="overlay">
      <div v-if="mobileOpen"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-20 md:hidden"
        @click="mobileOpen = false" />
    </Transition>

    <!-- ================================================ -->
    <!-- SIDEBAR                                          -->
    <!-- ================================================ -->
    <!-- Sidebar wrapper (handles toggle button overflow) -->
    <div class="sidebar-wrapper fixed left-0 top-0 h-full z-30"
      :class="[expanded ? 'sidebar-wide' : 'sidebar-thin', mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0']">

      <!-- Toggle button — desktop, centro vertical -->
      <button
        class="toggle-btn hidden md:flex absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 items-center justify-center bg-white hover:bg-gray-50 text-gray-400 hover:text-gray-700 transition-all duration-200 rounded-full border border-gray-200 shadow-sm z-40"
        @click="expanded = !expanded">
        <Icon :name="expanded ? 'lucide:chevron-left' : 'lucide:chevron-right'" class="w-3 h-3 transition-transform duration-300" />
      </button>

    <aside
      class="sidebar h-full w-full bg-white border-r border-gray-100 flex flex-col overflow-hidden">

      <!-- Logo area -->
      <div class="logo-area flex items-center h-16 px-4 border-b border-gray-100 flex-shrink-0 relative">
        <!-- Logo collapsed: ícone pequeno -->
        <div v-if="!expanded" class="logo-icon w-8 h-8 rounded-xl overflow-hidden flex-shrink-0">
          <img src="/svg/edvance-logo2.svg" alt="Edvance" class="w-full h-full object-contain" />
        </div>

        <!-- Logo expanded: logo completa -->
        <Transition name="fade-slide">
          <div v-if="expanded" class="overflow-hidden flex items-center">
            <img src="/svg/edvance-logotipo.svg" alt="SAMBA Edvance" class="h-8 w-auto object-contain" />
          </div>
        </Transition>
      </div>

      <!-- User card -->
      <div class="border-b border-gray-100 flex-shrink-0 h-[60px] flex items-center"
        :class="expanded ? 'px-3' : 'justify-center'">
        <div class="flex items-center gap-3 h-10 rounded-xl hover:bg-gray-50 transition-colors cursor-default overflow-hidden"
          :class="expanded ? 'px-2 w-full' : 'px-0 w-10 justify-center'">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
            :class="roleColor">
            {{ userInitials }}
          </div>
          <Transition name="fade-slide">
            <div v-if="expanded" class="flex-1 min-w-0 overflow-hidden">
              <p class="text-gray-800 text-xs font-semibold truncate leading-tight">{{ user?.name }}</p>
              <span class="text-[10px] font-medium px-1.5 py-0.5 rounded-md inline-block mt-0.5" :class="roleBadge">
                {{ roleLabel }}
              </span>
            </div>
          </Transition>
        </div>
      </div>

      <!-- Nav items -->
      <nav class="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto overflow-x-hidden scrollbar-none">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 relative overflow-hidden"
          :class="isActive(item.to)
            ? 'bg-blue-50 text-blue-600 active-item'
            : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'"
          :title="!expanded ? item.label : undefined"
          @click="mobileOpen = false">

          <!-- Active indicator -->
          <div v-if="isActive(item.to)"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-blue-500 rounded-r-full" />

          <Icon :name="item.icon" class="w-4 h-4 flex-shrink-0 transition-transform duration-150 group-hover:scale-110" />

          <Transition name="fade-slide">
            <span v-if="expanded" class="truncate">{{ item.label }}</span>
          </Transition>

          <!-- Tooltip quando collapsed -->
          <Transition name="tooltip">
            <div v-if="!expanded"
              class="tooltip-label pointer-events-none absolute left-full ml-3 px-2.5 py-1.5 bg-gray-900 text-white text-xs font-medium rounded-lg whitespace-nowrap shadow-xl border border-white/10 z-50 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
              {{ item.label }}
              <div class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 rotate-45 border-l border-b border-white/10" />
            </div>
          </Transition>
        </NuxtLink>
      </nav>

      <!-- Footer: logout -->
      <div class="px-2 py-3 border-t border-gray-100 flex-shrink-0">
        <button
          class="group w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-500 hover:bg-red-50 hover:text-red-600 transition-all duration-150"
          :title="!expanded ? 'Sair' : undefined"
          @click="logout">
          <Icon name="lucide:log-out" class="w-4 h-4 flex-shrink-0 transition-transform duration-150 group-hover:-translate-x-0.5" />
          <Transition name="fade-slide">
            <span v-if="expanded">Sair</span>
          </Transition>
        </button>
      </div>
    </aside>
    </div><!-- /sidebar-wrapper -->

    <!-- ================================================ -->
    <!-- MAIN CONTENT                                     -->
    <!-- ================================================ -->
    <div class="main-content flex-1 flex flex-col min-h-screen transition-all duration-300"
      :class="expanded ? 'md:ml-60' : 'md:ml-16'">

      <!-- Topbar -->
      <header class="sticky top-0 z-10 h-16 flex items-center gap-3 px-4 md:px-6 bg-white border-b border-gray-100">

        <!-- Mobile toggle -->
        <button class="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors flex-shrink-0"
          @click="mobileOpen = !mobileOpen">
          <Icon name="lucide:menu" class="w-5 h-5" />
        </button>

        <!-- Page title -->
        <div class="flex items-center gap-2.5 flex-1 min-w-0">
          <div class="flex items-center gap-1.5">
            <span class="text-gray-300 text-sm">/</span>
            <span class="text-xs font-medium text-gray-400">{{ roleLabel }}</span>
            <span class="text-gray-300 text-sm">/</span>
          </div>
          <h1 class="text-sm font-semibold text-gray-900 truncate">{{ pageTitle }}</h1>
        </div>

        <!-- Right actions -->
        <div class="flex items-center gap-1 flex-shrink-0">

          <!-- Divider -->
          <div class="w-px h-5 bg-gray-100 mx-1 hidden sm:block" />

          <!-- Notificações -->
          <div class="relative" ref="notifRef">
            <button
              class="relative p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-all duration-150"
              @click="toggleNotif">
              <Icon name="lucide:bell" class="w-4 h-4" />
              <span v-if="unread > 0"
                class="absolute top-1 right-1 min-w-[16px] h-4 px-1 rounded-full bg-blue-500 ring-1 ring-white flex items-center justify-center text-[9px] font-bold text-white">
                {{ unread > 9 ? '9+' : unread }}
              </span>
            </button>

            <!-- Dropdown -->
            <Transition name="notif-drop">
              <div v-if="notifOpen"
                class="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden z-50">

                <!-- Header -->
                <div class="flex items-center justify-between px-4 py-3 border-b border-gray-50">
                  <span class="text-sm font-semibold text-gray-900">Notificações</span>
                  <button v-if="unread > 0"
                    class="text-[11px] text-blue-500 hover:text-blue-600 font-medium transition-colors"
                    @click="marcarTodasLidas">
                    Marcar todas como lidas
                  </button>
                </div>

                <!-- Loading -->
                <div v-if="notifLoading" class="flex items-center justify-center py-10">
                  <Icon name="lucide:loader-2" class="w-5 h-5 text-gray-300 animate-spin" />
                </div>

                <!-- Empty -->
                <div v-else-if="notifs.length === 0" class="flex flex-col items-center justify-center py-10 px-4">
                  <div class="w-10 h-10 rounded-2xl bg-gray-50 flex items-center justify-center mb-3">
                    <Icon name="lucide:bell-off" class="w-5 h-5 text-gray-300" />
                  </div>
                  <p class="text-sm font-medium text-gray-400">Nenhuma notificação</p>
                </div>

                <!-- List -->
                <div v-else class="max-h-80 overflow-y-auto">
                  <div v-for="n in notifs" :key="n.id"
                    class="flex items-start gap-3 px-4 py-3 border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors cursor-pointer"
                    :class="!n.read ? 'bg-blue-50/40' : ''"
                    @click="clicarNotif(n)">
                    <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
                      :class="notifIconBg(n.type)">
                      <Icon :name="notifIcon(n.type)" class="w-4 h-4" :class="notifIconColor(n.type)" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs font-semibold text-gray-900 leading-snug">{{ n.title }}</p>
                      <p class="text-[11px] text-gray-500 mt-0.5 leading-snug">{{ n.body }}</p>
                    </div>
                    <div v-if="!n.read" class="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Avatar com nome -->
          <div class="flex items-center gap-2 pl-1 pr-2 py-1 rounded-lg hover:bg-gray-50 transition-colors cursor-default ml-1">
            <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-[11px] font-bold flex-shrink-0"
              :class="roleColor">
              {{ userInitials }}
            </div>
            <div class="hidden md:block">
              <p class="text-xs font-semibold text-gray-800 leading-tight">{{ user?.name?.split(' ')[0] }}</p>
              <p class="text-[10px] text-gray-400 leading-tight">{{ roleLabel }}</p>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 md:p-6 lg:p-8">
        <slot />
      </main>
    </div>

    <!-- ================================================ -->
    <!-- TOAST POPOUTS                                    -->
    <!-- ================================================ -->
    <Teleport to="body">
      <div class="fixed bottom-5 right-5 z-[100] flex flex-col gap-2 items-end pointer-events-none">
        <TransitionGroup name="toast">
          <div
            v-for="t in toasts"
            :key="t.id"
            class="pointer-events-auto flex items-start gap-3 w-80 bg-white rounded-2xl shadow-2xl border p-4 cursor-pointer"
            :class="toastBorder(t.type)"
            @click="clicarToast(t)">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
              :class="notifIconBg(t.type)">
              <Icon :name="notifIcon(t.type)" class="w-4 h-4" :class="notifIconColor(t.type)" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-gray-900 leading-snug">{{ t.title }}</p>
              <p class="text-[11px] text-gray-500 mt-0.5 leading-snug">{{ t.body }}</p>
            </div>
            <button class="text-gray-300 hover:text-gray-500 transition-colors flex-shrink-0 mt-0.5"
              @click.stop="fecharToast(t.id)">
              <Icon name="lucide:x" class="w-3.5 h-3.5" />
            </button>
          </div>
        </TransitionGroup>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
const { user, logout } = useAuth()
const route = useRoute()
const { get } = useApi()

const expanded = ref(true)
const mobileOpen = ref(false)

// Persiste estado do sidebar no localStorage
onMounted(() => {
  const saved = localStorage.getItem('samba_sidebar')
  if (saved !== null) expanded.value = saved === 'true'
  carregarNotifs()
})

watch(expanded, val => {
  localStorage.setItem('samba_sidebar', String(val))
})

function isActive(path: string) {
  return route.path === path || (path !== '/dashboard/' + route.path.split('/')[2] && route.path.startsWith(path + '/'))
}

// -----------------------------------------------
// Notificações — polling + popout + som
// -----------------------------------------------
interface Notif {
  id: string
  type: 'assigned' | 'submitted' | 'ready_to_lock'
  title: string
  body: string
  link?: string
  read: boolean
}

const notifOpen    = ref(false)
const notifLoading = ref(false)
const notifRef     = ref<HTMLElement | null>(null)
const notifs       = ref<Notif[]>([])
const readIds      = ref<Set<string>>(new Set())
const toasts       = ref<Notif[]>([])
const knownIds     = ref<Set<string>>(new Set())
let   pollTimer: ReturnType<typeof setInterval> | null = null

const unread = computed(() => notifs.value.filter(n => !n.read).length)

function toggleNotif() {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) carregarNotifs()
}

function tocarSom() {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.type = 'sine'
    osc.frequency.setValueAtTime(880, ctx.currentTime)
    osc.frequency.exponentialRampToValueAtTime(660, ctx.currentTime + 0.15)
    gain.gain.setValueAtTime(0.15, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4)
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + 0.4)
  } catch {}
}

function mostrarToast(n: Notif) {
  toasts.value.push(n)
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== n.id)
  }, 5000)
}

async function carregarNotifs(silent = false) {
  if (!silent) notifLoading.value = true
  try {
    const data = await get<Notif[]>('/notifications')
    const novos = data.filter(n => !knownIds.value.has(n.id))
    const isFirstLoad = knownIds.value.size === 0 && notifs.value.length === 0
    data.forEach(n => knownIds.value.add(n.id))
    notifs.value = data.map(n => ({ ...n, read: readIds.value.has(n.id) }))
    if (!isFirstLoad && novos.length > 0) {
      tocarSom()
      novos.forEach(n => mostrarToast({ ...n, read: false }))
    }
  } catch {
    notifs.value = []
  } finally {
    notifLoading.value = false
  }
}

function marcarTodasLidas() {
  notifs.value.forEach(n => readIds.value.add(n.id))
  notifs.value = notifs.value.map(n => ({ ...n, read: true }))
}

function clicarNotif(n: Notif) {
  readIds.value.add(n.id)
  n.read = true
  if (n.link) navigateTo(n.link)
  notifOpen.value = false
}

function clicarToast(n: Notif) {
  toasts.value = toasts.value.filter(t => t.id !== n.id)
  readIds.value.add(n.id)
  if (n.link) navigateTo(n.link)
}

function fecharToast(id: string) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

function notifIcon(type: string) {
  if (type === 'assigned') return 'lucide:clipboard-list'
  if (type === 'submitted') return 'lucide:send'
  if (type === 'ready_to_lock') return 'lucide:lock'
  return 'lucide:bell'
}
function notifIconBg(type: string) {
  if (type === 'assigned') return 'bg-blue-50'
  if (type === 'submitted') return 'bg-emerald-50'
  if (type === 'ready_to_lock') return 'bg-amber-50'
  return 'bg-gray-50'
}
function notifIconColor(type: string) {
  if (type === 'assigned') return 'text-blue-500'
  if (type === 'submitted') return 'text-emerald-500'
  if (type === 'ready_to_lock') return 'text-amber-500'
  return 'text-gray-400'
}
function toastBorder(type: string) {
  if (type === 'assigned') return 'border-blue-200'
  if (type === 'submitted') return 'border-emerald-200'
  if (type === 'ready_to_lock') return 'border-amber-200'
  return 'border-gray-200'
}

onMounted(() => {
  document.addEventListener('click', (e) => {
    if (notifRef.value && !notifRef.value.contains(e.target as Node)) {
      notifOpen.value = false
    }
  })
  carregarNotifs()
  pollTimer = setInterval(() => carregarNotifs(true), 30_000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

const roleConfig = computed(() => {
  const configs: Record<string, any> = {
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
        { to: '/dashboard/coordenador',            icon: 'lucide:layout-dashboard', label: 'Painel' },
        { to: '/dashboard/coordenador/turmas',       icon: 'lucide:users',            label: 'Turmas' },
        { to: '/dashboard/coordenador/disciplinas', icon: 'lucide:book-open',        label: 'Disciplinas' },
        { to: '/dashboard/coordenador/simulados',   icon: 'lucide:file-text',        label: 'Simulados' },
        { to: '/dashboard/coordenador/questoes',    icon: 'lucide:help-circle',      label: 'Questões' },
        { to: '/dashboard/coordenador/professores', icon: 'lucide:user-check',       label: 'Professores' },
        { to: '/dashboard/coordenador/alunos',      icon: 'lucide:graduation-cap',   label: 'Alunos' },
        { to: '/dashboard/coordenador/relatorios',  icon: 'lucide:bar-chart-2',      label: 'Relatórios' },
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
  return configs[user.value?.role ?? 'professor'] ?? configs.professor
})

const roleColor    = computed(() => roleConfig.value.color)
const roleBadge    = computed(() => roleConfig.value.badge)
const roleLabel    = computed(() => roleConfig.value.label)
const navItems     = computed(() => roleConfig.value.nav)

const userInitials = computed(() =>
  user.value?.name?.split(' ').slice(0, 2).map((n: string) => n[0]).join('') ?? '?'
)

const pageTitle = computed(() => {
  const all = navItems.value
  const exact = all.find((i: any) => i.to === route.path)
  if (exact) return exact.label
  const parent = all.find((i: any) => route.path.startsWith(i.to + '/') && i.to !== '/dashboard/' + route.path.split('/')[2])
  return parent?.label ?? 'Painel'
})
</script>

<style scoped>
/* Sidebar widths */
.sidebar-wrapper {
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: width;
}
.sidebar-wide  { width: 15rem; }
.sidebar-thin  { width: 4rem;  }

.sidebar { }

/* Scrollbar none */
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }

/* Fade + slide for text labels */
.fade-slide-enter-active {
  transition: opacity 0.2s ease 0.05s, transform 0.2s ease 0.05s;
}
.fade-slide-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-6px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-4px);
}

/* Overlay transition */
.overlay-enter-active, .overlay-leave-active { transition: opacity 0.2s ease; }
.overlay-enter-from, .overlay-leave-to { opacity: 0; }

/* Active nav glow */
.active-item {
  box-shadow: inset 0 0 16px rgba(59, 130, 246, 0.06);
}

.nav-item { will-change: background-color, color; }

.tooltip-label { transition: opacity 0.15s ease; }

/* Toast popout */
.toast-enter-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.98);
}
.toast-move { transition: transform 0.3s ease; }

/* Notification dropdown */
.notif-drop-enter-active {
  transition: opacity 0.18s ease, transform 0.18s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.notif-drop-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.notif-drop-enter-from {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}
.notif-drop-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
</style>