<!-- pages/dashboard/coordenador/simulados/novo.vue -->
<template>
  <div class="max-w-4xl mx-auto space-y-6">

    <!-- Cabeçalho -->
    <div class="flex items-center gap-4">
      <NuxtLink
        to="/dashboard/coordenador"
        class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
      >
        <Icon name="lucide:arrow-left" class="w-5 h-5" />
      </NuxtLink>
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Novo simulado</h2>
        <p class="text-gray-500 text-sm mt-0.5">Preencha os dados e adicione as disciplinas</p>
      </div>
    </div>

    <!-- Step indicator -->
    <div class="flex items-center gap-2">
      <div
        v-for="(step, i) in steps"
        :key="i"
        class="flex items-center gap-2"
      >
        <div class="flex items-center gap-2">
          <div
            class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors"
            :class="currentStep > i
              ? 'bg-blue-600 text-white'
              : currentStep === i
                ? 'bg-blue-600 text-white ring-4 ring-blue-100'
                : 'bg-gray-100 text-gray-400'"
          >
            <Icon v-if="currentStep > i" name="lucide:check" class="w-3.5 h-3.5" />
            <span v-else>{{ i + 1 }}</span>
          </div>
          <span class="text-sm font-medium hidden sm:block" :class="currentStep === i ? 'text-gray-900' : 'text-gray-400'">
            {{ step }}
          </span>
        </div>
        <div v-if="i < steps.length - 1" class="w-8 h-px bg-gray-200 mx-1" />
      </div>
    </div>

    <!-- STEP 0: Dados gerais -->
    <div v-if="currentStep === 0" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm space-y-5">
      <h3 class="font-semibold text-gray-900">Dados gerais</h3>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Nome do simulado <span class="text-red-500">*</span></label>
        <input
          v-model="form.nome"
          type="text"
          placeholder="Ex: Simulado Bimestral — 1º Bimestre 2026"
          class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Data de aplicação <span class="text-red-500">*</span></label>
          <div class="relative">
            <Icon name="lucide:calendar" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              v-model="form.dataAplicacao"
              type="date"
              class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Data limite para questões <span class="text-red-500">*</span></label>
          <div class="relative">
            <Icon name="lucide:clock" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              v-model="form.dataLimite"
              type="date"
              class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nível de ensino <span class="text-red-500">*</span></label>
          <select
            v-model="form.nivel"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="">Selecione...</option>
            <option value="fund1">Fundamental I (1º ao 5º ano)</option>
            <option value="fund2">Fundamental II (6º ao 9º ano)</option>
            <option value="medio">Ensino Médio (1º ao 3º ano)</option>
            <option value="fund1_fund2">Fundamental I e II</option>
            <option value="fund2_medio">Fundamental II e Médio</option>
            <option value="todos">Todos os níveis</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Alternativas</label>
          <select
            v-model="form.alternativas"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="4">A até D (4 alternativas)</option>
            <option value="5">A até E (5 alternativas)</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Instruções gerais</label>
        <textarea
          v-model="form.instrucoes"
          rows="3"
          placeholder="Ex: Leia atentamente cada questão antes de responder..."
          class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>
    </div>

    <!-- STEP 1: Disciplinas -->
    <div v-if="currentStep === 1" class="space-y-4">
      <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <h3 class="font-semibold text-gray-900 mb-4">Adicionar disciplina</h3>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Disciplina</label>
            <select
              v-model="novaDisciplina.id"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option value="">Selecione...</option>
              <option
                v-for="d in disciplinasDisponiveis"
                :key="d.id"
                :value="d.id"
                :disabled="disciplinasSelecionadas.some(s => s.id === d.id)"
              >
                {{ d.nome }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nº de questões</label>
            <input
              v-model.number="novaDisciplina.questoes"
              type="number"
              min="1"
              max="50"
              placeholder="Ex: 10"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div class="flex items-end">
            <button
              :disabled="!novaDisciplina.id || !novaDisciplina.questoes"
              class="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg transition-colors"
              @click="adicionarDisciplina"
            >
              <Icon name="lucide:plus" class="w-4 h-4" />
              Adicionar
            </button>
          </div>
        </div>
      </div>

      <!-- Lista de disciplinas adicionadas -->
      <div v-if="disciplinasSelecionadas.length > 0" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-900">Disciplinas do simulado</h3>
          <span class="text-xs text-gray-400">{{ totalQuestoes }} questões no total</span>
        </div>
        <div class="space-y-2">
          <div
            v-for="(disc, i) in disciplinasSelecionadas"
            :key="disc.id"
            class="flex items-center gap-4 p-3 rounded-xl border border-gray-100 hover:bg-gray-50"
          >
            <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :class="disc.cor">
              <Icon :name="disc.icon" class="w-4 h-4 text-white" />
            </div>
            <div class="flex-1">
              <p class="text-sm font-semibold text-gray-900">{{ disc.nome }}</p>
              <p class="text-xs text-gray-400">{{ disc.professor || 'Professor não atribuído' }}</p>
            </div>
            <div class="flex items-center gap-3">
              <div class="flex items-center gap-1">
                <button
                  class="w-6 h-6 rounded border border-gray-200 flex items-center justify-center text-gray-400 hover:border-blue-400 hover:text-blue-600 transition-colors"
                  @click="disc.questoes = Math.max(1, disc.questoes - 1)"
                >
                  <Icon name="lucide:minus" class="w-3 h-3" />
                </button>
                <span class="w-8 text-center text-sm font-bold text-gray-900">{{ disc.questoes }}</span>
                <button
                  class="w-6 h-6 rounded border border-gray-200 flex items-center justify-center text-gray-400 hover:border-blue-400 hover:text-blue-600 transition-colors"
                  @click="disc.questoes++"
                >
                  <Icon name="lucide:plus" class="w-3 h-3" />
                </button>
              </div>
              <span class="text-xs text-gray-400">questões</span>
              <button
                class="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                @click="removerDisciplina(i)"
              >
                <Icon name="lucide:trash-2" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-2xl border border-dashed border-gray-200 p-10 text-center">
        <Icon name="lucide:book-open" class="w-10 h-10 text-gray-300 mx-auto mb-3" />
        <p class="text-gray-400 text-sm">Nenhuma disciplina adicionada ainda</p>
      </div>
    </div>

    <!-- STEP 2: Revisão -->
    <div v-if="currentStep === 2" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm space-y-5">
      <h3 class="font-semibold text-gray-900">Revisão do simulado</h3>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="p-4 bg-gray-50 rounded-xl">
          <p class="text-xs text-gray-400 mb-1">Nome</p>
          <p class="text-sm font-semibold text-gray-900">{{ form.nome }}</p>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl">
          <p class="text-xs text-gray-400 mb-1">Aplicação</p>
          <p class="text-sm font-semibold text-gray-900">{{ formatDate(form.dataAplicacao) }}</p>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl">
          <p class="text-xs text-gray-400 mb-1">Prazo questões</p>
          <p class="text-sm font-semibold text-gray-900">{{ formatDate(form.dataLimite) }}</p>
        </div>
        <div class="p-4 bg-gray-50 rounded-xl">
          <p class="text-xs text-gray-400 mb-1">Alternativas</p>
          <p class="text-sm font-semibold text-gray-900">A até {{ form.alternativas === '4' ? 'D' : 'E' }}</p>
        </div>
      </div>

      <div>
        <p class="text-sm font-medium text-gray-700 mb-3">Disciplinas e professores notificados</p>
        <div class="space-y-2">
          <div
            v-for="disc in disciplinasSelecionadas"
            :key="disc.id"
            class="flex items-center gap-3 p-3 rounded-xl border border-gray-100"
          >
            <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" :class="disc.cor">
              <Icon :name="disc.icon" class="w-3.5 h-3.5 text-white" />
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900">{{ disc.nome }}</p>
              <p class="text-xs text-gray-400">{{ disc.professor }}</p>
            </div>
            <span class="text-sm font-bold text-gray-700">{{ disc.questoes }} questões</span>
          </div>
        </div>
      </div>

      <div class="p-4 bg-blue-50 border border-blue-100 rounded-xl flex items-start gap-3">
        <Icon name="lucide:info" class="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
        <p class="text-sm text-blue-700">
          Ao confirmar, cada professor receberá uma notificação com as instruções e prazo para cadastrar suas questões.
        </p>
      </div>
    </div>

    <!-- Navegação -->
    <div class="flex items-center justify-between pt-2">
      <button
        v-if="currentStep > 0"
        class="flex items-center gap-2 px-4 py-2.5 border border-gray-200 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
        @click="currentStep--"
      >
        <Icon name="lucide:arrow-left" class="w-4 h-4" />
        Voltar
      </button>
      <div v-else />

      <button
        v-if="currentStep < steps.length - 1"
        :disabled="!canAdvance"
        class="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg transition-colors"
        @click="avancar"
      >
        Continuar
        <Icon name="lucide:arrow-right" class="w-4 h-4" />
      </button>

      <button
        v-else
        class="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold rounded-lg transition-colors"
        @click="confirmar"
      >
        <Icon name="lucide:send" class="w-4 h-4" />
        Criar e notificar professores
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const router = useRouter()

const steps = ['Dados gerais', 'Disciplinas', 'Revisão']
const currentStep = ref(0)

const form = reactive({
  nome: '',
  dataAplicacao: '',
  dataLimite: '',
  nivel: '',
  alternativas: '4',
  instrucoes: '',
})

const disciplinasDisponiveis = [
  { id: 'port', nome: 'Português', cor: 'bg-blue-500', icon: 'lucide:book-open', professor: 'Ana Lima' },
  { id: 'mat', nome: 'Matemática', cor: 'bg-purple-500', icon: 'lucide:calculator', professor: 'Carlos Mendes' },
  { id: 'hist', nome: 'História', cor: 'bg-amber-500', icon: 'lucide:landmark', professor: 'Roberto Dias' },
  { id: 'geo', nome: 'Geografia', cor: 'bg-green-500', icon: 'lucide:globe', professor: 'Paula Ferreira' },
  { id: 'cien', nome: 'Ciências', cor: 'bg-teal-500', icon: 'lucide:flask-conical', professor: 'Marcos Souza' },
  { id: 'arte', nome: 'Arte', cor: 'bg-pink-500', icon: 'lucide:palette', professor: 'Julia Costa' },
  { id: 'ef', nome: 'Educação Física', cor: 'bg-orange-500', icon: 'lucide:trophy', professor: 'Diego Alves' },
  { id: 'ing', nome: 'Inglês', cor: 'bg-indigo-500', icon: 'lucide:languages', professor: 'Carla Nunes' },
]

const disciplinasSelecionadas = ref<any[]>([])

const novaDisciplina = reactive({ id: '', questoes: 10 })

function adicionarDisciplina() {
  const disc = disciplinasDisponiveis.find(d => d.id === novaDisciplina.id)
  if (!disc) return
  disciplinasSelecionadas.value.push({ ...disc, questoes: novaDisciplina.questoes })
  novaDisciplina.id = ''
  novaDisciplina.questoes = 10
}

function removerDisciplina(i: number) {
  disciplinasSelecionadas.value.splice(i, 1)
}

const totalQuestoes = computed(() =>
  disciplinasSelecionadas.value.reduce((acc, d) => acc + d.questoes, 0)
)

const canAdvance = computed(() => {
  if (currentStep.value === 0) {
    return form.nome && form.dataAplicacao && form.dataLimite && form.nivel
  }
  if (currentStep.value === 1) {
    return disciplinasSelecionadas.value.length > 0
  }
  return true
})

function avancar() {
  if (canAdvance.value) currentStep.value++
}

function formatDate(d: string) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}

function confirmar() {
  // Aqui chama o backend quando estiver pronto
  alert('Simulado criado! Professores notificados.')
  router.push('/dashboard/coordenador')
}
</script>