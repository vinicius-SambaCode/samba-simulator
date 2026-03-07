<!-- pages/dashboard/professor/simulados/[id].vue -->
<template>
  <div class="max-w-4xl mx-auto space-y-6">

    <!-- Cabeçalho -->
    <div class="flex items-center gap-4">
      <NuxtLink
        to="/dashboard/professor/simulados"
        class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
      >
        <Icon name="lucide:arrow-left" class="w-5 h-5" />
      </NuxtLink>
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-0.5">
          <h2 class="text-2xl font-bold text-gray-900">{{ simulado.nome }}</h2>
          <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">
            Prazo: {{ simulado.dataLimite }}
          </span>
        </div>
        <p class="text-gray-500 text-sm">{{ simulado.disciplina }} · {{ simulado.questoesPendentes }} questões para cadastrar</p>
      </div>
    </div>

    <!-- Progresso -->
    <div class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
      <div class="flex items-center justify-between mb-2">
        <p class="text-sm font-medium text-gray-700">Progresso</p>
        <p class="text-sm font-bold text-gray-900">{{ questoes.length }} / {{ simulado.questoesPendentes }} questões</p>
      </div>
      <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-500"
          :class="progresso === 100 ? 'bg-emerald-500' : 'bg-blue-500'"
          :style="{ width: `${progresso}%` }"
        />
      </div>
      <p class="text-xs mt-2" :class="progresso === 100 ? 'text-emerald-600 font-semibold' : 'text-gray-400'">
        {{ progresso === 100 ? '✓ Todas as questões cadastradas!' : `Faltam ${simulado.questoesPendentes - questoes.length} questões` }}
      </p>
    </div>

    <!-- Upload de arquivo -->
    <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
      <div class="flex items-center gap-2 mb-4">
        <Icon name="lucide:file-up" class="w-5 h-5 text-blue-600" />
        <h3 class="font-semibold text-gray-900">Importar via arquivo Word</h3>
      </div>

      <!-- Área de drop -->
      <div
        class="border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer"
        :class="isDragging
          ? 'border-blue-400 bg-blue-50'
          : uploadStatus === 'success'
            ? 'border-emerald-300 bg-emerald-50'
            : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/30'"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".docx"
          class="hidden"
          @change="handleFileChange"
        />

        <!-- Estado: aguardando -->
        <div v-if="uploadStatus === 'idle'" class="space-y-2">
          <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center mx-auto">
            <Icon name="lucide:file-text" class="w-6 h-6 text-blue-600" />
          </div>
          <p class="text-sm font-medium text-gray-700">Arraste o arquivo ou clique para selecionar</p>
          <p class="text-xs text-gray-400">Apenas arquivos <span class="font-semibold">.docx</span> são aceitos</p>
        </div>

        <!-- Estado: processando -->
        <div v-else-if="uploadStatus === 'loading'" class="space-y-3">
          <svg class="animate-spin w-10 h-10 text-blue-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          <p class="text-sm font-medium text-blue-700">Processando arquivo...</p>
          <p class="text-xs text-blue-400">O backend está extraindo as questões</p>
        </div>

        <!-- Estado: sucesso -->
        <div v-else-if="uploadStatus === 'success'" class="space-y-2">
          <div class="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center mx-auto">
            <Icon name="lucide:check-circle" class="w-6 h-6 text-emerald-600" />
          </div>
          <p class="text-sm font-medium text-emerald-700">{{ uploadedFileName }} importado!</p>
          <p class="text-xs text-emerald-500">{{ questoes.length }} questões extraídas — revise abaixo antes de enviar</p>
          <button
            class="text-xs text-gray-400 hover:text-gray-600 underline mt-1"
            @click.stop="resetUpload"
          >
            Enviar outro arquivo
          </button>
        </div>

        <!-- Estado: erro -->
        <div v-else-if="uploadStatus === 'error'" class="space-y-2">
          <div class="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center mx-auto">
            <Icon name="lucide:alert-circle" class="w-6 h-6 text-red-500" />
          </div>
          <p class="text-sm font-medium text-red-700">Erro ao processar o arquivo</p>
          <p class="text-xs text-red-400">Verifique o formato e tente novamente</p>
          <button
            class="text-xs text-gray-400 hover:text-gray-600 underline mt-1"
            @click.stop="resetUpload"
          >
            Tentar novamente
          </button>
        </div>
      </div>

      <p class="text-xs text-gray-400 mt-3 flex items-center gap-1.5">
        <Icon name="lucide:info" class="w-3.5 h-3.5" />
        O arquivo deve seguir o modelo padrão. Após importar, você pode editar cada questão antes de enviar.
      </p>
    </div>

    <!-- Separador -->
    <div class="flex items-center gap-4">
      <div class="flex-1 h-px bg-gray-200" />
      <span class="text-xs text-gray-400 font-medium">ou adicione manualmente</span>
      <div class="flex-1 h-px bg-gray-200" />
    </div>

    <!-- Formulário manual -->
    <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm space-y-5">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold text-gray-900">
          {{ editandoIndex !== null ? `Editando questão ${editandoIndex + 1}` : 'Nova questão' }}
        </h3>
        <span class="text-xs text-gray-400">Alternativas de A a {{ simulado.alternativas === 4 ? 'D' : 'E' }}</span>
      </div>

      <!-- Enunciado -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Enunciado <span class="text-red-500">*</span></label>
        <textarea
          v-model="novaQuestao.enunciado"
          rows="3"
          placeholder="Digite o enunciado da questão..."
          class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>

      <!-- Alternativas -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Alternativas <span class="text-red-500">*</span></label>
        <div class="space-y-2">
          <div
            v-for="(_, i) in novaQuestao.alternativas.slice(0, simulado.alternativas)"
            :key="i"
            class="flex items-center gap-3"
          >
            <button
              class="w-7 h-7 rounded-full border-2 flex items-center justify-center text-xs font-bold flex-shrink-0 transition-colors"
              :class="novaQuestao.correta === i
                ? 'border-emerald-500 bg-emerald-500 text-white'
                : 'border-gray-200 text-gray-400 hover:border-emerald-400'"
              @click="novaQuestao.correta = i"
            >
              {{ letras[i] }}
            </button>
            <input
              v-model="novaQuestao.alternativas[i]"
              type="text"
              :placeholder="`Alternativa ${letras[i]}`"
              class="flex-1 px-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 transition-colors"
              :class="novaQuestao.correta === i
                ? 'border-emerald-300 focus:ring-emerald-400 bg-emerald-50'
                : 'border-gray-200 focus:ring-blue-500'"
            />
          </div>
        </div>
        <p class="text-xs text-gray-400 mt-2">Clique na letra para marcar a alternativa correta</p>
      </div>

      <div class="flex items-center gap-3 pt-2">
        <button
          :disabled="!questaoValida"
          class="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg transition-colors"
          @click="salvarQuestao"
        >
          <Icon :name="editandoIndex !== null ? 'lucide:check' : 'lucide:plus'" class="w-4 h-4" />
          {{ editandoIndex !== null ? 'Salvar edição' : 'Adicionar questão' }}
        </button>
        <button
          v-if="editandoIndex !== null"
          class="px-4 py-2.5 border border-gray-200 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
          @click="cancelarEdicao"
        >
          Cancelar
        </button>
      </div>
    </div>

    <!-- Lista de questões -->
    <div v-if="questoes.length > 0" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-gray-900">Questões cadastradas</h3>
        <span class="text-xs text-gray-400">{{ questoes.length }} de {{ simulado.questoesPendentes }}</span>
      </div>
      <div class="space-y-3">
        <div
          v-for="(q, i) in questoes"
          :key="i"
          class="p-4 rounded-xl border transition-colors"
          :class="editandoIndex === i ? 'border-blue-300 bg-blue-50' : 'border-gray-100 hover:bg-gray-50'"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-start gap-3 flex-1 min-w-0">
              <div class="flex items-center gap-1.5 flex-shrink-0 mt-0.5">
                <span class="w-6 h-6 rounded-full bg-gray-100 text-gray-500 text-xs font-bold flex items-center justify-center">
                  {{ i + 1 }}
                </span>
                <Icon v-if="q.importado" name="lucide:file-text" class="w-3.5 h-3.5 text-blue-400" title="Importado via arquivo" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-800 line-clamp-2">{{ q.enunciado }}</p>
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <span
                    v-for="(alt, j) in q.alternativas.slice(0, simulado.alternativas)"
                    :key="j"
                    class="text-xs px-2 py-0.5 rounded-full"
                    :class="q.correta === j
                      ? 'bg-emerald-100 text-emerald-700 font-semibold'
                      : 'bg-gray-100 text-gray-500'"
                  >
                    {{ letras[j] }}) {{ alt }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-1 flex-shrink-0">
              <button
                class="p-1.5 rounded-lg text-gray-300 hover:text-blue-500 hover:bg-blue-50 transition-colors"
                @click="editarQuestao(i)"
              >
                <Icon name="lucide:pencil" class="w-4 h-4" />
              </button>
              <button
                class="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                @click="removerQuestao(i)"
              >
                <Icon name="lucide:trash-2" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Botão enviar -->
    <div v-if="questoes.length > 0" class="flex justify-end">
      <button
        :disabled="progresso < 100"
        class="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition-colors"
        :class="progresso === 100
          ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
          : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
        @click="enviarQuestoes"
      >
        <Icon name="lucide:send" class="w-4 h-4" />
        {{ progresso === 100 ? 'Enviar questões ao coordenador' : `Faltam ${simulado.questoesPendentes - questoes.length} questões` }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const router = useRouter()
const letras = ['A', 'B', 'C', 'D', 'E']

const simulado = reactive({
  nome: 'Simulado Bimestral — 1º Bimestre 2026',
  disciplina: 'Matemática',
  dataLimite: '10/03/2026',
  questoesPendentes: 10,
  alternativas: 4,
})

interface Questao {
  enunciado: string
  alternativas: string[]
  correta: number
  importado?: boolean
}

const questoes = ref<Questao[]>([])
const editandoIndex = ref<number | null>(null)

const novaQuestao = reactive<Questao>({
  enunciado: '',
  alternativas: ['', '', '', '', ''],
  correta: 0,
})

// Upload states
const fileInput = ref<HTMLInputElement | null>(null)
const uploadStatus = ref<'idle' | 'loading' | 'success' | 'error'>('idle')
const uploadedFileName = ref('')
const isDragging = ref(false)

const progresso = computed(() =>
  Math.round((questoes.value.length / simulado.questoesPendentes) * 100)
)

const questaoValida = computed(() => {
  const altsPreenchidas = novaQuestao.alternativas
    .slice(0, simulado.alternativas)
    .every(a => a.trim() !== '')
  return novaQuestao.enunciado.trim() !== '' && altsPreenchidas
})

function triggerFileInput() {
  if (uploadStatus.value === 'success') return
  fileInput.value?.click()
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) processFile(file)
}

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) processFile(file)
}

async function processFile(file: File) {
  if (!file.name.endsWith('.docx')) {
    uploadStatus.value = 'error'
    return
  }

  uploadedFileName.value = file.name
  uploadStatus.value = 'loading'

  // Simula chamada ao backend — substituir por $fetch real
  await new Promise(r => setTimeout(r, 2000))

  // Mock das questões extraídas pelo backend
  const extracted: Questao[] = [
    {
      enunciado: 'Qual é o resultado de 3/4 + 1/2?',
      alternativas: ['1/4', '5/4', '1', '3/2', ''],
      correta: 1,
      importado: true,
    },
    {
      enunciado: 'Resolva: 2x + 5 = 13. Qual o valor de x?',
      alternativas: ['2', '3', '4', '5', ''],
      correta: 2,
      importado: true,
    },
    {
      enunciado: 'Qual é a área de um quadrado com lado 6cm?',
      alternativas: ['24 cm²', '36 cm²', '12 cm²', '18 cm²', ''],
      correta: 1,
      importado: true,
    },
  ]

  // Preenche o formulário com as questões extraídas
  questoes.value = extracted
  uploadStatus.value = 'success'
}

function resetUpload() {
  uploadStatus.value = 'idle'
  uploadedFileName.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

function salvarQuestao() {
  if (!questaoValida.value) return
  const q: Questao = {
    enunciado: novaQuestao.enunciado,
    alternativas: [...novaQuestao.alternativas],
    correta: novaQuestao.correta,
    importado: false,
  }
  if (editandoIndex.value !== null) {
    questoes.value[editandoIndex.value] = q
    editandoIndex.value = null
  } else {
    questoes.value.push(q)
  }
  resetForm()
}

function editarQuestao(i: number) {
  const q = questoes.value[i]
  novaQuestao.enunciado = q.enunciado
  novaQuestao.alternativas = [...q.alternativas]
  novaQuestao.correta = q.correta
  editandoIndex.value = i
  window.scrollTo({ top: 400, behavior: 'smooth' })
}

function cancelarEdicao() {
  editandoIndex.value = null
  resetForm()
}

function removerQuestao(i: number) {
  questoes.value.splice(i, 1)
  if (editandoIndex.value === i) cancelarEdicao()
}

function resetForm() {
  novaQuestao.enunciado = ''
  novaQuestao.alternativas = ['', '', '', '', '']
  novaQuestao.correta = 0
}

function enviarQuestoes() {
  // Substituir por $fetch real ao backend
  alert('Questões enviadas ao coordenador com sucesso!')
  router.push('/dashboard/professor')
}
</script>