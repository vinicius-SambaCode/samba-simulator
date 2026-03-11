// composables/useQuestionRenderer.ts
//
// Renderiza texto de questões com suporte a LaTeX (KaTeX) e imagens.
// Importa KaTeX diretamente — sem depender de script CDN assíncrono.

import katex from 'katex'

const BASE_URL = 'http://localhost:8000'

export interface QuestionImage {
  id: number
  url: string          // ex: /media/questions/42/img_stem_0_abc.png
  context: string      // 'stem' | 'option_A' | 'option_B' ...
  order_idx: number
  mime_type: string
  width_px?: number
  height_px?: number
}

/**
 * Escapa apenas o texto puro (fora de fórmulas) para HTML seguro.
 * Processa $$...$$ e $...$ com KaTeX ANTES de escapar o restante,
 * para não corromper símbolos LaTeX (<, >, &, etc.).
 */
function renderLatex(text: string): string {
  if (!text) return ''

  const parts: string[] = []
  let lastIndex = 0

  // Captura $$...$$ (display) e $...$ (inline)
  const pattern = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g
  let match: RegExpExecArray | null

  pattern.lastIndex = 0
  while ((match = pattern.exec(text)) !== null) {
    // Texto literal antes da fórmula
    const before = text.slice(lastIndex, match.index)
    if (before) parts.push(escapeHtml(before))

    const isDisplay = match[1] !== undefined
    const formula   = (isDisplay ? match[1] : match[2]).trim()

    try {
      parts.push(katex.renderToString(formula, {
        displayMode:  isDisplay,
        throwOnError: false,
        strict:       false,
      }))
    } catch {
      parts.push(`<span class="math-error">${escapeHtml(match[0])}</span>`)
    }

    lastIndex = match.index + match[0].length
  }

  // Texto restante
  const tail = text.slice(lastIndex)
  if (tail) parts.push(escapeHtml(tail))

  return parts.join('')
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function imgHtml(img: QuestionImage): string {
  const src = img.url.startsWith('http') ? img.url : `${BASE_URL}${img.url}`
  const w   = img.width_px ? `max-width: ${Math.min(img.width_px, 600)}px;` : 'max-width: 100%;'
  return `<img src="${src}" alt="Imagem da questão" class="question-img rounded-lg my-2 block" style="${w}" loading="lazy" />`
}

export function useQuestionRenderer() {

  function renderStem(stem: string, images: QuestionImage[] = []): string {
    const stemImgs = images
      .filter(i => i.context === 'stem')
      .sort((a, b) => a.order_idx - b.order_idx)
    return renderLatex(stem) + stemImgs.map(imgHtml).join('')
  }

  function renderOption(text: string, label: string, images: QuestionImage[] = []): string {
    const ctx     = `option_${label.toUpperCase()}`
    const optImgs = images
      .filter(i => i.context === ctx)
      .sort((a, b) => a.order_idx - b.order_idx)
    return renderLatex(text) + optImgs.map(imgHtml).join('')
  }

  return { renderStem, renderOption }
}

// ─────────────────────────────────────────────
// Para instalar o KaTeX no projeto Nuxt:
//   npm install katex
//   npm install -D @types/katex
// ─────────────────────────────────────────────