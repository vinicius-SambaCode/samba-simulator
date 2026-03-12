<!-- pages/dashboard/coordenador/disciplinas/index.vue -->
<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between animate-fade-in">
      <div>
        <h2 class="text-xl font-black text-gray-900 tracking-tight">Disciplinas</h2>
        <p class="text-sm text-gray-400 mt-0.5">
          {{ disciplines.length }} disciplina{{ disciplines.length !== 1 ? 's' : '' }} cadastrada{{ disciplines.length !== 1 ? 's' : '' }}
        </p>
      </div>
      <button
        class="flex items-center gap-2 px-4 py-2.5 bg-gray-900 hover:bg-gray-700 text-white text-sm font-bold rounded-xl transition-all duration-200 hover:scale-[1.02] active:scale-95"
        @click="abrirModalCriar">
        <Icon name="lucide:plus" class="w-4 h-4" />
        Nova disciplina
      </button>
    </div>

    <!-- Busca -->
    <div class="relative animate-fade-up" style="animation-delay:40ms">
      <Icon name="lucide:search" class="w-4 h-4 text-gray-300 absolute left-3.5 top-1/2 -translate-y-1/2" />
      <input v-model="busca"
        class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition-all bg-white"
        placeholder="Buscar disciplina..." />
      <button v-if="busca" class="absolute right-3 top-1/2 -translate-y-1/2" @click="busca = ''">
        <Icon name="lucide:x" class="w-3.5 h-3.5 text-gray-300 hover:text-gray-500 transition-colors" />
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div v-for="i in 8" :key="i"
        class="h-24 bg-white rounded-2xl border border-gray-100 animate-pulse"
        :style="`animation-delay:${i * 40}ms`" />
    </div>

    <!-- Empty -->
    <div v-else-if="disciplinasFiltradas.length === 0"
      class="flex flex-col items-center justify-center py-28 bg-white rounded-2xl border-2 border-dashed border-gray-100 animate-fade-in">
      <div class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
        <Icon name="lucide:book-open" class="w-6 h-6 text-gray-200" />
      </div>
      <p class="text-sm font-bold text-gray-400">
        {{ busca ? 'Nenhuma disciplina encontrada' : 'Nenhuma disciplina cadastrada' }}
      </p>
      <p class="text-xs text-gray-300 mt-1">
        {{ busca ? 'Tente outro termo' : 'Crie a primeira disciplina' }}
      </p>
      <button v-if="!busca"
        class="mt-4 flex items-center gap-2 px-4 py-2 bg-gray-900 text-white text-sm font-bold rounded-xl hover:bg-gray-700 transition-all"
        @click="abrirModalCriar">
        <Icon name="lucide:plus" class="w-4 h-4" />
        Nova disciplina
      </button>
    </div>

    <!-- Grid de disciplinas -->
    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 animate-fade-up" style="animation-delay:60ms">
      <div
        v-for="(disc, idx) in disciplinasFiltradas" :key="disc.id"
        class="group bg-white rounded-2xl border border-gray-100 p-5 flex flex-col gap-4 hover:border-gray-200 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 animate-fade-up"
        :style="`animation-delay:${80 + idx * 30}ms`">

        <!-- Ícone + nome -->
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 text-white font-black text-sm shadow-sm"
              :style="`background-color: ${corDisciplina(idx)}`">
              {{ iniciais(disc.name) }}
            </div>
            <div class="min-w-0">
              <p class="text-sm font-black text-gray-900 truncate leading-tight">{{ disc.name }}</p>
              <p class="text-[10px] text-gray-400 mt-0.5">#{{ disc.id }}</p>
            </div>
          </div>

          <!-- Menu de ações -->
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150 flex-shrink-0">
            <button
              class="p-1.5 rounded-lg text-gray-300 hover:text-blue-500 hover:bg-blue-50 transition-colors"
              title="Editar"
              @click="abrirModalEditar(disc)">
              <Icon name="lucide:pencil" class="w-3.5 h-3.5" />
            </button>
            <button
              class="p-1.5 rounded-lg transition-colors"
              :class="confirmandoId === disc.id
                ? 'text-red-600 bg-red-50'
                : 'text-gray-300 hover:text-red-500 hover:bg-red-50'"
              :title="confirmandoId === disc.id ? 'Confirmar exclusão' : 'Excluir'"
              @click="clicarExcluir(disc.id)">
              <Icon name="lucide:trash-2" class="w-3.5 h-3.5" />
            </button>
            <button v-if="confirmandoId === disc.id"
              class="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              title="Cancelar"
              @click.stop="confirmandoId = null">
              <Icon name="lucide:x" class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <!-- Confirmação de exclusão -->
        <Transition name="slide-down">
          <div v-if="confirmandoId === disc.id"
            class="px-3 py-2 bg-red-50 border border-red-200 rounded-xl flex items-center justify-between">
            <span class="text-xs text-red-700 font-medium">Confirmar exclusão?</span>
            <div class="flex items-center gap-2">
              <button class="text-xs font-bold text-red-600 hover:text-red-700 transition-colors"
                @click="excluirDisciplina(disc.id)">Excluir</button>
              <button class="text-xs text-gray-400 hover:text-gray-600 transition-colors"
                @click="confirmandoId = null">Cancelar</button>
            </div>
          </div>
        </Transition>

      </div>
    </div>

    <!-- ================================================ -->
    <!-- MODAL: Criar / Editar disciplina                 -->
    <!-- ================================================ -->
    <Transition name="modal">
      <div v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="fecharModal">

        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">

          <!-- Header do modal -->
          <div class="flex items-center gap-3 px-6 py-5 border-b border-gray-100">
            <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              :class="editandoId ? 'bg-blue-50' : 'bg-emerald-50'">
              <Icon :name="editandoId ? 'lucide:pencil' : 'lucide:plus-circle'"
                class="w-4 h-4"
                :class="editandoId ? 'text-blue-600' : 'text-emerald-600'" />
            </div>
            <div class="flex-1">
              <h3 class="font-black text-gray-900 text-sm">
                {{ editandoId ? 'Editar disciplina' : 'Nova disciplina' }}
              </h3>
              <p class="text-xs text-gray-400 mt-0.5">
                {{ editandoId ? 'Altere o nome da disciplina' : 'Preencha o nome da disciplina' }}
              </p>
            </div>
            <button
              class="p-2 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              @click="fecharModal">
              <Icon name="lucide:x" class="w-4 h-4" />
            </button>
          </div>

          <!-- Formulário -->
          <div class="px-6 py-5 space-y-4">
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">
                Nome da disciplina <span class="text-red-400">*</span>
              </label>
              <input
                ref="inputNome"
                v-model="form.name"
                type="text"
                placeholder="Ex: Matemática, Física, Programação..."
                class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                :class="{ 'border-red-300 focus:ring-red-400': erro }"
                @keyup.enter="salvar"
                @input="erro = ''" />
              <Transition name="slide-down">
                <p v-if="erro" class="mt-1.5 text-xs text-red-500 flex items-center gap-1">
                  <Icon name="lucide:alert-circle" class="w-3 h-3" />
                  {{ erro }}
                </p>
              </Transition>
            </div>

            <!-- Exemplos rápidos (só na criação) -->
            <div v-if="!editandoId">
              <p class="text-xs text-gray-400 mb-2">Sugestões rápidas:</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="sugestao in sugestoes.filter(s => !disciplines.some(d => d.name === s))"
                  :key="sugestao"
                  class="px-2.5 py-1 rounded-lg bg-gray-50 border border-gray-200 text-xs text-gray-600 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-all"
                  @click="form.name = sugestao; erro = ''">
                  {{ sugestao }}
                </button>
              </div>
            </div>
          </div>

          <!-- Rodapé -->
          <div class="px-6 pb-5 flex items-center justify-end gap-3">
            <button
              class="px-4 py-2.5 text-sm font-bold text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all"
              @click="fecharModal">
              Cancelar
            </button>
            <button
              :disabled="!form.name.trim() || salvando"
              class="flex items-center gap-2 px-5 py-2.5 text-sm font-bold rounded-xl transition-all duration-150 active:scale-95"
              :class="form.name.trim() && !salvando
                ? editandoId
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                  : 'bg-gray-900 hover:bg-gray-700 text-white shadow-sm'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
              @click="salvar">
              <Icon v-if="salvando" name="lucide:loader-2" class="w-4 h-4 animate-spin" />
              <Icon v-else :name="editandoId ? 'lucide:check' : 'lucide:plus'" class="w-4 h-4" />
              {{ salvando ? 'Salvando...' : editandoId ? 'Salvar alterações' : 'Criar disciplina' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.show"
        class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-lg text-sm font-medium min-w-[220px]"
        :class="toast.type === 'success' ? 'bg-gray-900 text-white'
          : toast.type === 'error' ? 'bg-red-600 text-white'
          : 'bg-blue-600 text-white'">
        <Icon
          :name="toast.type === 'success' ? 'lucide:check-circle-2'
            : toast.type === 'error' ? 'lucide:alert-circle' : 'lucide:info'"
          class="w-4 h-4 flex-shrink-0" />
        {{ toast.message }}
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const { get, post, put, delete: deleteReq } = useApi()

// ── Estado ──
const disciplines  = ref<any[]>([])
const loading      = ref(true)
const busca        = ref('')
const confirmandoId = ref<number | null>(null)
const showModal    = ref(false)
const editandoId   = ref<number | null>(null)
const salvando     = ref(false)
const erro         = ref('')
const inputNome    = ref<HTMLInputElement | null>(null)

const form = reactive({ name: '' })

const toast = reactive({ show: false, message: '', type: 'success' as 'success' | 'error' | 'info' })
let toastTimer: ReturnType<typeof setTimeout> | null = null

// Sugestões de disciplinas comuns
const sugestoes = [
  'Matemática', 'Física', 'Química', 'Biologia',
  'Língua Portuguesa', 'História', 'Geografia',
  'Filosofia', 'Sociologia', 'Inglês',
  'Educação Física', 'Arte', 'Programação',
  'Redação',
]

// Paleta de cores para os cards
const cores = [
  '#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B',
  '#10B981', '#EF4444', '#06B6D4', '#6366F1',
  '#F97316', '#14B8A6', '#84CC16', '#A855F7',
]

function corDisciplina(idx: number): string {
  return cores[idx % cores.length]
}

function iniciais(nome: string): string {
  return nome.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

const disciplinasFiltradas = computed(() => {
  if (!busca.value.trim()) return disciplines.value
  const q = busca.value.toLowerCase()
  return disciplines.value.filter(d => d.name.toLowerCase().includes(q))
})

// ── Toast ──
function showToast(message: string, type: 'success' | 'error' | 'info' = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toast.message = message
  toast.type    = type
  toast.show    = true
  toastTimer = setTimeout(() => { toast.show = false }, 3000)
}

// ── Fetch ──
onMounted(async () => {
  try {
    disciplines.value = await get<any[]>('/disciplines/')
  } catch {
    showToast('Erro ao carregar disciplinas', 'error')
  } finally {
    loading.value = false
  }
})

// ── Modal ──
function abrirModalCriar() {
  editandoId.value = null
  form.name        = ''
  erro.value       = ''
  showModal.value  = true
  nextTick(() => inputNome.value?.focus())
}

function abrirModalEditar(disc: any) {
  editandoId.value = disc.id
  form.name        = disc.name
  erro.value       = ''
  showModal.value  = true
  nextTick(() => inputNome.value?.focus())
}

function fecharModal() {
  showModal.value  = false
  editandoId.value = null
  form.name        = ''
  erro.value       = ''
}

// ── CRUD ──
async function salvar() {
  if (!form.name.trim() || salvando.value) return
  salvando.value = true
  erro.value     = ''

  try {
    if (editandoId.value) {
      const updated = await put<any>(`/disciplines/${editandoId.value}/`, { name: form.name.trim() })
      const idx = disciplines.value.findIndex(d => d.id === editandoId.value)
      if (idx !== -1) disciplines.value[idx] = updated
      showToast('Disciplina atualizada!')
    } else {
      const created = await post<any>('/disciplines/', { name: form.name.trim() })
      disciplines.value = [...disciplines.value, created]
      showToast('Disciplina criada!')
    }
    fecharModal()
  } catch (e: any) {
    const msg = e?.data?.detail ?? e?.message ?? 'Erro ao salvar'
    erro.value = msg.includes('já existe') ? 'Já existe uma disciplina com esse nome.' : msg
  } finally {
    salvando.value = false
  }
}

function clicarExcluir(id: number) {
  if (confirmandoId.value === id) {
    excluirDisciplina(id)
  } else {
    confirmandoId.value = id
    setTimeout(() => {
      if (confirmandoId.value === id) confirmandoId.value = null
    }, 3000)
  }
}

async function excluirDisciplina(id: number) {
  confirmandoId.value = null
  try {
    await deleteReq(`/disciplines/${id}/`)
    disciplines.value = disciplines.value.filter(d => d.id !== id)
    showToast('Disciplina excluída.')
  } catch (e: any) {
    const msg = e?.data?.detail ?? e?.message ?? 'Erro ao excluir'
    showToast(msg.includes('foreign') || msg.includes('violat')
      ? 'Não é possível excluir: disciplina em uso por professores ou simulados.'
      : msg, 'error')
  }
}
</script>

<style scoped>
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-in  { animation: fadeIn  0.3s ease both; }
.animate-fade-up  { animation: fadeUp  0.3s ease both; }

/* Modal */
.modal-enter-active { transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.modal-leave-active { transition: all 0.15s ease; }
.modal-enter-from   { opacity: 0; transform: scale(0.92); }
.modal-leave-to     { opacity: 0; transform: scale(0.96); }

/* Slide down */
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.2s ease; overflow: hidden; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; max-height: 0; }
.slide-down-enter-to, .slide-down-leave-from { max-height: 80px; }

/* Toast */
.toast-enter-active { transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from   { opacity: 0; transform: translateY(16px) scale(0.95); }
.toast-leave-to     { opacity: 0; transform: translateY(8px); }
</style>
