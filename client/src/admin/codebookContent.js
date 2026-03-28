import rawCodebookContent from '../../../WORKSTATION_MASTER_CODEBOOK.md?raw'

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

function pushParagraph(section, paragraphLines) {
  if (!section || paragraphLines.length === 0) {
    return
  }

  const joinWithNewlines = paragraphLines.some((line) => line.startsWith('->'))

  section.blocks.push({
    type: 'paragraph',
    content: paragraphLines.join(joinWithNewlines ? '\n' : ' '),
  })
}

function pushList(section, listState) {
  if (!section || !listState || listState.items.length === 0) {
    return
  }

  section.blocks.push(listState)
}

function ensureSection(sections, currentSection) {
  if (currentSection) {
    return currentSection
  }

  const fallbackSection = {
    id: 'overview',
    title: 'Overview',
    blocks: [],
  }

  sections.push(fallbackSection)
  return fallbackSection
}

function parseCodebook(markdown) {
  const lines = markdown.replace(/\r/g, '').split('\n')
  const sections = []
  let title = 'Workstation Master Codebook'
  let currentSection = null
  let paragraphLines = []
  let listState = null

  function flushParagraph() {
    currentSection = ensureSection(sections, currentSection)
    pushParagraph(currentSection, paragraphLines)
    paragraphLines = []
  }

  function flushList() {
    currentSection = ensureSection(sections, currentSection)
    pushList(currentSection, listState)
    listState = null
  }

  for (const line of lines) {
    const trimmed = line.trim()

    if (!trimmed) {
      flushParagraph()
      flushList()
      continue
    }

    if (trimmed.startsWith('# ')) {
      title = trimmed.slice(2).trim()
      continue
    }

    if (trimmed.startsWith('## ')) {
      flushParagraph()
      flushList()

      currentSection = {
        id: slugify(trimmed.slice(3)),
        title: trimmed.slice(3).trim(),
        blocks: [],
      }

      sections.push(currentSection)
      continue
    }

    const orderedMatch = trimmed.match(/^(\d+)\.\s+(.+)$/)
    const unorderedMatch = trimmed.match(/^-\s+(.+)$/)

    if (orderedMatch) {
      flushParagraph()
      currentSection = ensureSection(sections, currentSection)

      if (!listState || listState.type !== 'ordered') {
        flushList()
        listState = { type: 'ordered', items: [] }
      }

      listState.items.push({
        index: orderedMatch[1],
        text: orderedMatch[2],
      })
      continue
    }

    if (unorderedMatch) {
      flushParagraph()
      currentSection = ensureSection(sections, currentSection)

      if (!listState || listState.type !== 'unordered') {
        flushList()
        listState = { type: 'unordered', items: [] }
      }

      listState.items.push(unorderedMatch[1])
      continue
    }

    flushList()
    paragraphLines.push(trimmed)
  }

  flushParagraph()
  flushList()

  return {
    title,
    sections: sections.filter((section) => section.blocks.length > 0),
  }
}

export const workstationMasterCodebook = rawCodebookContent.trim()
export const codebookSource = 'WORKSTATION_MASTER_CODEBOOK.md'
export const { title: codebookTitle, sections: codebookSections } = parseCodebook(workstationMasterCodebook)