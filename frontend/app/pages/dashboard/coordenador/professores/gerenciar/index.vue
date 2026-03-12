<!-- pages/dashboard/coordenador/professores/gerenciar/index.vue -->
<template>
  <div class="h-[calc(100vh-4rem)] flex flex-col gap-4 overflow-hidden">

    <!-- Header compacto -->
    <div class="flex items-center justify-between gap-4 flex-shrink-0">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/coordenador/professores"
          class="w-8 h-8 rounded-xl hover:bg-gray-100 flex items-center justify-center transition-colors">
          <Icon name="lucide:arrow-left" class="w-4 h-4 text-gray-400" />
        </NuxtLink>
        <div>
          <h2 class="text-lg font-black text-gray-900 tracking-tight">Professores & Vínculos</h2>
          <p class="text-xs text-gray-400">Gerencie professores e suas turmas/disciplinas</p>
        </div>
      </div>
      <button
        class="flex items-center gap-2 px-4 py-2 bg-gray-900 hover:bg-gray-700 text-white text-xs font-bold rounded-xl transition-all active:scale-95"
        @click="openCreate">
        <Icon name="lucide:user-plus" class="w-3.5 h-3.5" />
        Novo professor
      </button>
    </div>

    <!-- Layout: lista à esquerda, painel vínculos à direita -->
    <div class="flex gap-4 flex-1 min-h-0">

      <!-- Coluna esquerda: lista de professores -->
      <div class="w-72 flex-shrink-0 flex flex-col bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <!-- Busca -->
        <div class="px-3 py-3 border-b border-gray-50">
          <div class="relative">
            <Icon name="lucide:search" class="w-3.5 h-3.5 text-gray-300 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input v-model="busca"
              class="w-full pl-8 pr-3 py-2 text-xs border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 transition-all"
              placeholder="Filtrar professores..." />
          </div>
        </div>

        <!-- Lista -->
        <div v-if="loading" class="p-3 space-y-2">
          <div v-for="i in 5" :key="i" class="h-14 bg-gray-50 rounded-xl animate-pulse" />
        </div>

        <div v-else class="flex-1 overflow-y-auto divide-y divide-gray-50">
          <button
            v-for="(prof, idx) in teachersFiltrados" :key="prof.id"
            class="w-full flex items-center gap-3 px-4 py-3 text-left transition-colors"
            :class="selectedProf?.id === prof.id
              ? 'bg-gray-900 text-white'
              : 'hover:bg-gray-50'"
            @click="selectProf(prof)">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-xs font-black transition-colors"
              :style="selectedProf?.id === prof.id
                ? 'background:rgba(255,255,255,0.15); color:white'
                : `background-color:${avatarBg(idx)}18; color:${avatarBg(idx)}`">
              {{ initials(prof.name) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold truncate">{{ prof.name }}</p>
              <p class="text-[10px] opacity-60 truncate">{{ vinculosDoProf(prof.id).length }} vínculo{{ vinculosDoProf(prof.id).length !== 1 ? 's' : '' }}</p>
            </div>
            <div class="flex items-center gap-1 flex-shrink-0" @click.stop>
              <button
                class="w-6 h-6 rounded-lg flex items-center justify-center transition-colors"
                :class="selectedProf?.id === prof.id ? 'hover:bg-white/20' : 'hover:bg-blue-50'"
                @click="openEdit(prof)">
                <Icon name="lucide:pencil" class="w-3 h-3"
                  :class="selectedProf?.id === prof.id ? 'text-white/70' : 'text-blue-400'" />
              </button>
              <button
                class="w-6 h-6 rounded-lg flex items-center justify-center transition-colors"
                :class="selectedProf?.id === prof.id ? 'hover:bg-white/20' : 'hover:bg-red-50'"
                @click="openDelete(prof)">
                <Icon name="lucide:trash-2" class="w-3 h-3"
                  :class="selectedProf?.id === prof.id ? 'text-white/70' : 'text-red-400'" />
              </button>
            </div>
          </button>

          <div v-if="!teachersFiltrados.length" class="flex flex-col items-center py-12 text-center px-4">
            <Icon name="lucide:users" class="w-8 h-8 text-gray-200 mb-2" />
            <p class="text-xs text-gray-400">{{ busca ? 'Nenhum resultado' : 'Nenhum professor' }}</p>
          </div>
        </div>
      </div>

      <!-- Coluna direita: painel de vínculos -->
      <div class="flex-1 flex flex-col bg-white rounded-2xl border border-gray-100 overflow-hidden">

        <!-- Empty state: nenhum professor selecionado -->
        <div v-if="!selectedProf" class="flex-1 flex flex-col items-center justify-center text-center p-8">
          <div class="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
            <Icon name="lucide:mouse-pointer-click" class="w-7 h-7 text-gray-300" />
          </div>
          <p class="text-sm font-bold text-gray-400">Selecione um professor</p>
          <p class="text-xs text-gray-300 mt-1">para gerenciar seus vínculos de turma e disciplina</p>
        </div>

        <template v-else>
          <!-- Header do painel -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-50 flex-shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-black"
                :style="`background-color:${avatarBg(teachers.findIndex(t => t.id === selectedProf.id))}18; color:${avatarBg(teachers.findIndex(t => t.id === selectedProf.id))}`">
                {{ initials(selectedProf.name) }}
              </div>
              <div>
                <p class="text-sm font-black text-gray-900">{{ selectedProf.name }}</p>
                <p class="text-xs text-gray-400">{{ selectedProf.email }}</p>
              </div>
            </div>
            <span class="text-[10px] font-bold px-2 py-1 rounded-full"
              :class="vinculosDoProf(selectedProf.id).length ? 'bg-blue-50 text-blue-600' : 'bg-gray-100 text-gray-400'">
              {{ vinculosDoProf(selectedProf.id).length }} vínculo{{ vinculosDoProf(selectedProf.id).length !== 1 ? 's' : '' }}
            </span>
          </div>

          <!-- Vínculos existentes -->
          <div class="flex-1 overflow-y-auto p-5">
            <p class="text-[11px] font-black text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Icon name="lucide:link" class="w-3 h-3" />
              Turmas e disciplinas vinculadas
            </p>

            <!-- Grid de vínculos existentes -->
            <div v-if="vinculosDoProf(selectedProf.id).length" class="grid grid-cols-2 gap-2 mb-5">
              <div v-for="v in vinculosDoProf(selectedProf.id)" :key="v.id"
                class="flex items-center gap-2 px-3 py-2.5 bg-gray-50 border border-gray-100 rounded-xl group/tag hover:border-red-100 hover:bg-red-50/30 transition-colors">
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-black text-gray-800 leading-tight">{{ className(v.class_id) }}</p>
                  <p class="text-[11px] text-gray-500 truncate">{{ disciplineName(v.discipline_id) }}</p>
                </div>
                <button
                  class="w-6 h-6 rounded-lg hover:bg-red-100 flex items-center justify-center transition-colors opacity-0 group-hover/tag:opacity-100 flex-shrink-0"
                  @click="removeVinculo(v.id)">
                  <Icon name="lucide:x" class="w-3 h-3 text-red-400" />
                </button>
              </div>
            </div>
            <p v-else class="text-xs text-gray-400 italic mb-5">Nenhum vínculo cadastrado.</p>

            <!-- Separador -->
            <div class="border-t border-gray-100 mb-4" />

            <!-- Adicionar novo vínculo -->
            <p class="text-[11px] font-black text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Icon name="lucide:plus-circle" class="w-3 h-3" />
              Adicionar vínculo
            </p>

            <div class="grid grid-cols-2 gap-3 mb-3">
              <div>
                <label class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Turma</label>
                <select v-model="novoVinculo.class_id"
                  class="w-full text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-700">
                  <option value="">Selecionar turma</option>
                  <option v-for="c in allClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div>
                <label class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Disciplina</label>
                <select v-model="novoVinculo.discipline_id"
                  class="w-full text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-700">
                  <option value="">Selecionar disciplina</option>
                  <option v-for="d in disciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
                </select>
              </div>
            </div>

            <button
              :disabled="!novoVinculo.class_id || !novoVinculo.discipline_id || addingVinculo"
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all"
              :class="!novoVinculo.class_id || !novoVinculo.discipline_id
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
              @click="addVinculo">
              <svg v-if="addingVinculo" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              <Icon v-else name="lucide:link" class="w-3.5 h-3.5" />
              {{ addingVinculo ? 'Vinculando...' : 'Adicionar vínculo' }}
            </button>

            <p v-if="vinculoError" class="text-[11px] text-red-500 mt-2 flex items-center gap-1">
              <Icon name="lucide:alert-circle" class="w-3 h-3" />{{ vinculoError }}
            </p>
          </div>
        </template>
      </div>
    </div>

    <!-- MODAL: CRIAR / EDITAR -->
    <Transition name="modal">
      <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="closeForm" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-modal-in">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              :class="editingProf ? 'bg-blue-50' : 'bg-gray-900'">
              <Icon :name="editingProf ? 'lucide:pencil' : 'lucide:user-plus'"
                class="w-4 h-4" :class="editingProf ? 'text-blue-500' : 'text-white'" />
            </div>
            <div class="flex-1">
              <h3 class="text-sm font-black text-gray-900">{{ editingProf ? 'Editar professor' : 'Novo professor' }}</h3>
              <p class="text-xs text-gray-400">{{ editingProf ? editingProf.email : 'Preencha os dados abaixo' }}</p>
            </div>
            <button class="w-7 h-7 rounded-xl hover:bg-gray-100 flex items-center justify-center" @click="closeForm">
              <Icon name="lucide:x" class="w-3.5 h-3.5 text-gray-400" />
            </button>
          </div>

          <div class="space-y-3">
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1">Nome completo</label>
              <input v-model="form.name" type="text" placeholder="Ex: Prof. João Silva"
                class="w-full px-3 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 transition-all"
                :class="errors.name ? 'border-red-300 focus:ring-red-100' : 'border-gray-200 focus:ring-blue-200'" />
              <p v-if="errors.name" class="text-[11px] text-red-500 mt-1">{{ errors.name }}</p>
            </div>
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1">E-mail</label>
              <input v-model="form.email" type="email" placeholder="prof@escola.edu.br"
                class="w-full px-3 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 transition-all"
                :class="errors.email ? 'border-red-300 focus:ring-red-100' : 'border-gray-200 focus:ring-blue-200'" />
              <p v-if="errors.email" class="text-[11px] text-red-500 mt-1">{{ errors.email }}</p>
            </div>
            <div>
              <label class="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-1">
                {{ editingProf ? 'Nova senha (opcional)' : 'Senha' }}
              </label>
              <div class="relative">
                <input v-model="form.password" :type="showPassword ? 'text' : 'password'"
                  :placeholder="editingProf ? '••••••••' : 'Mínimo 6 caracteres'"
                  class="w-full px-3 py-2.5 pr-10 border rounded-xl text-sm focus:outline-none focus:ring-2 transition-all"
                  :class="errors.password ? 'border-red-300 focus:ring-red-100' : 'border-gray-200 focus:ring-blue-200'" />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-300 hover:text-gray-500"
                  @click="showPassword = !showPassword">
                  <Icon :name="showPassword ? 'lucide:eye-off' : 'lucide:eye'" class="w-4 h-4" />
                </button>
              </div>
              <p v-if="errors.password" class="text-[11px] text-red-500 mt-1">{{ errors.password }}</p>
            </div>

            <div v-if="formError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
              <p class="text-xs text-red-600">{{ formError }}</p>
            </div>

            <div class="flex gap-2 pt-1">
              <button class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600"
                @click="closeForm">Cancelar</button>
              <button :disabled="saving"
                class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
                :class="saving ? 'bg-gray-100 text-gray-300 cursor-not-allowed' : 'bg-gray-900 hover:bg-gray-700 text-white active:scale-95'"
                @click="submitForm">
                <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                </svg>
                {{ saving ? 'Salvando...' : editingProf ? 'Salvar' : 'Adicionar' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- MODAL: EXCLUIR -->
    <Transition name="modal">
      <div v-if="showDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/25 backdrop-blur-sm" @click="showDelete = false" />
        <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-modal-in">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
              <Icon name="lucide:trash-2" class="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h3 class="text-sm font-black text-gray-900">Excluir professor</h3>
              <p class="text-xs text-gray-400">Esta ação não pode ser desfeita</p>
            </div>
          </div>
          <p class="text-sm text-gray-600 mb-4">
            Excluir <span class="font-bold text-gray-900">{{ deletingProf?.name }}</span>?
            Todos os vínculos serão removidos permanentemente.
          </p>
          <div v-if="deleteError" class="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-100 rounded-xl mb-3">
            <Icon name="lucide:circle-x" class="w-4 h-4 text-red-400 flex-shrink-0" />
            <p class="text-xs text-red-600">{{ deleteError }}</p>
          </div>
          <div class="flex gap-2">
            <button class="flex-1 py-2.5 rounded-xl text-sm font-bold border border-gray-200 hover:bg-gray-50 text-gray-600"
              @click="showDelete = false">Cancelar</button>
            <button :disabled="deleting"
              class="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="deleting ? 'bg-red-200 text-red-300 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700 text-white active:scale-95'"
              @click="confirmDelete">
              <svg v-if="deleting" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              {{ deleting ? 'Excluindo...' : 'Sim, excluir' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast"
        class="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl text-white text-xs font-bold"
        :class="toast.type === 'success' ? 'bg-emerald-600' : 'bg-red-600'">
        <Icon :name="toast.type === 'success' ? 'lucide:check-circle-2' : 'lucide:alert-circle'" class="w-4 h-4" />
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { get, post, patch, delete: del } = useApi()

const teachers    = ref<any[]>([])
const vinculos    = ref<any[]>([])
const allClasses  = ref<any[]>([])
const disciplines = ref<any[]>([])
const loading     = ref(true)
const busca       = ref('')

// Professor selecionado no painel
const selectedProf = ref<any>(null)

function selectProf(prof: any) {
  selectedProf.value = selectedProf.value?.id === prof.id ? null : prof
  novoVinculo.class_id = ''
  novoVinculo.discipline_id = ''
  vinculoError.value = ''
}

const teachersFiltrados = computed(() => {
  if (!busca.value) return teachers.value
  const q = busca.value.toLowerCase()
  return teachers.value.filter(t => t.name.toLowerCase().includes(q) || t.email.toLowerCase().includes(q))
})

function vinculosDoProf(profId: number) {
  return vinculos.value.filter(v => v.teacher_user_id === profId)
}
function className(id: number) { return allClasses.value.find(c => c.id === id)?.name ?? `#${id}` }
function disciplineName(id: number) { return disciplines.value.find(d => d.id === id)?.name ?? `#${id}` }

// ── Vínculo ──
const novoVinculo  = reactive({ class_id: '' as number | '', discipline_id: '' as number | '' })
const addingVinculo = ref(false)
const vinculoError  = ref('')

async function addVinculo() {
  if (!selectedProf.value || !novoVinculo.class_id || !novoVinculo.discipline_id) return
  addingVinculo.value = true
  vinculoError.value  = ''
  try {
    const created = await post<any>('/school/teacher-subjects', {
      teacher_user_id: selectedProf.value.id,
      class_id:        novoVinculo.class_id,
      discipline_id:   novoVinculo.discipline_id,
    })
    vinculos.value.push(created)
    novoVinculo.class_id = ''
    novoVinculo.discipline_id = ''
    showToast('success', 'Vínculo adicionado!')
  } catch (e: any) {
    vinculoError.value = e?.data?.detail ?? 'Erro ao adicionar vínculo.'
  } finally {
    addingVinculo.value = false
  }
}

async function removeVinculo(linkId: number) {
  try {
    await del(`/school/teacher-subjects/${linkId}`)
    vinculos.value = vinculos.value.filter(v => v.id !== linkId)
    showToast('success', 'Vínculo removido.')
  } catch (e: any) {
    showToast('error', e?.data?.detail ?? 'Erro ao remover.')
  }
}

// ── Form criar/editar ──
const showForm     = ref(false)
const editingProf  = ref<any>(null)
const saving       = ref(false)
const showPassword = ref(false)
const formError    = ref('')
const form   = reactive({ name: '', email: '', password: '', is_active: true })
const errors = reactive({ name: '', email: '', password: '' })

function openCreate() {
  editingProf.value = null
  Object.assign(form, { name: '', email: '', password: '', is_active: true })
  Object.assign(errors, { name: '', email: '', password: '' })
  formError.value = ''; showPassword.value = false; showForm.value = true
}

function openEdit(prof: any) {
  editingProf.value = prof
  Object.assign(form, { name: prof.name, email: prof.email, password: '', is_active: prof.is_active !== false })
  Object.assign(errors, { name: '', email: '', password: '' })
  formError.value = ''; showPassword.value = false; showForm.value = true
}

function closeForm() { showForm.value = false; setTimeout(() => { editingProf.value = null }, 200) }

function validate() {
  let ok = true
  Object.assign(errors, { name: '', email: '', password: '' })
  if (!form.name.trim()) { errors.name = 'Nome obrigatório.'; ok = false }
  if (!form.email.trim()) { errors.email = 'E-mail obrigatório.'; ok = false }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = 'E-mail inválido.'; ok = false }
  if (!editingProf.value && !form.password.trim()) { errors.password = 'Senha obrigatória.'; ok = false }
  else if (form.password && form.password.length < 6) { errors.password = 'Mínimo 6 caracteres.'; ok = false }
  return ok
}

async function submitForm() {
  if (!validate()) return
  saving.value = true; formError.value = ''
  try {
    if (editingProf.value) {
      const payload: any = { name: form.name, email: form.email, is_active: form.is_active }
      if (form.password.trim()) payload.password = form.password
      const updated = await patch<any>(`/auth/users/${editingProf.value.id}`, payload)
      const idx = teachers.value.findIndex(t => t.id === editingProf.value.id)
      if (idx !== -1) teachers.value[idx] = { ...teachers.value[idx], ...updated }
      if (selectedProf.value?.id === editingProf.value.id) selectedProf.value = { ...selectedProf.value, ...updated }
      showToast('success', 'Professor atualizado!')
    } else {
      const created = await post<any>('/auth/users', { name: form.name, email: form.email, password: form.password, role: 'TEACHER' })
      teachers.value.push(created)
      showToast('success', `${form.name} adicionado!`)
    }
    closeForm()
  } catch (e: any) {
    formError.value = e?.data?.detail ?? e?.message ?? 'Erro ao salvar.'
  } finally {
    saving.value = false
  }
}

// ── Delete ──
const showDelete   = ref(false)
const deletingProf = ref<any>(null)
const deleting     = ref(false)
const deleteError  = ref('')

function openDelete(prof: any) { deletingProf.value = prof; deleteError.value = ''; showDelete.value = true }

async function confirmDelete() {
  if (!deletingProf.value) return
  deleting.value = true; deleteError.value = ''
  try {
    await del(`/auth/users/${deletingProf.value.id}`)
    teachers.value = teachers.value.filter(t => t.id !== deletingProf.value.id)
    vinculos.value = vinculos.value.filter(v => v.teacher_user_id !== deletingProf.value.id)
    if (selectedProf.value?.id === deletingProf.value.id) selectedProf.value = null
    showDelete.value = false
    showToast('success', 'Professor excluído.')
  } catch (e: any) {
    deleteError.value = e?.data?.detail ?? 'Erro ao excluir.'
  } finally {
    deleting.value = false
  }
}

// ── Toast ──
const toast = ref<{ type: 'success' | 'error'; message: string } | null>(null)
function showToast(type: 'success' | 'error', message: string) {
  toast.value = { type, message }
  setTimeout(() => { toast.value = null }, 3000)
}

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']
function avatarBg(idx: number) { return COLORS[idx % COLORS.length] }
function initials(name: string) { return name.split(' ').slice(0, 2).map((n: string) => n[0]).join('').toUpperCase() }

onMounted(async () => {
  const [tr, vr, cr, dr] = await Promise.allSettled([
    get<any[]>('/school/teachers'),
    get<any[]>('/school/teacher-subjects'),
    get<any[]>('/school/classes'),
    get<any[]>('/disciplines/'),
  ])
  if (tr.status === 'fulfilled') teachers.value    = tr.value
  if (vr.status === 'fulfilled') vinculos.value    = vr.value
  if (cr.status === 'fulfilled') allClasses.value  = cr.value
  if (dr.status === 'fulfilled') disciplines.value = dr.value
  loading.value = false
})
</script>

<style scoped>
@keyframes modal-in { from { opacity:0; transform:scale(.94) translateY(8px) } to { opacity:1; transform:scale(1) translateY(0) } }
@keyframes toast-in { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:translateY(0) } }
.animate-modal-in { animation: modal-in 0.22s cubic-bezier(0.34,1.56,0.64,1) both }
.modal-enter-active, .modal-leave-active { transition: opacity 0.18s ease }
.modal-enter-from, .modal-leave-to { opacity: 0 }
.toast-enter-active { animation: toast-in 0.25s ease both }
.toast-leave-active { transition: opacity 0.2s ease }
.toast-leave-to { opacity: 0 }
</style>
