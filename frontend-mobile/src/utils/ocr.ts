export interface MetricItem {
  name: string
  code?: string
  value: string
  unit?: string
  range?: string
  abnormal?: boolean
  abnormal_symbol?: string
}

export interface MetricGroups {
  left: MetricItem[]
  right: MetricItem[]
}

const cleanText = (s: string) => {
  if (!s) return ''
  return String(s).replace(/\s+/g, ' ').replace(/&nbsp;/g, ' ').trim()
}

const splitAbnormal = (value: string) => {
  const v = cleanText(value)
  if (!v) return { value: '', abnormal: false, symbol: '' }
  if (/uparrow/i.test(v) || /↑/.test(v)) return { value: v.replace(/uparrow/ig, '').replace(/↑/g, '').trim(), abnormal: true, symbol: '↑' }
  if (/downarrow/i.test(v) || /↓/.test(v)) return { value: v.replace(/downarrow/ig, '').replace(/↓/g, '').trim(), abnormal: true, symbol: '↓' }
  return { value: v, abnormal: false, symbol: '' }
}

const extractCodeFromName = (name: string) => {
  const m = String(name).match(/\(([^)]+)\)|（([^）]+)）/)
  return m ? (m[1] || m[2] || '').trim().toUpperCase() : ''
}

export function parseOcrHtmlToGroups(html: string, skipHeaderRows = 3): MetricGroups {
  const groups: MetricGroups = { left: [], right: [] }
  if (!html || !/<table/i.test(html)) return groups

  try {
    const decode = (s: string) =>
      s
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
    const safe = decode(html).replace(/<script[\s\S]*?<\/script>/gi, '').replace(/<style[\s\S]*?<\/style>/gi, '')
    const tableMatch = safe.match(/<table[\s\S]*?<\/table>/i)
    if (!tableMatch) return groups
    const tableHtml = tableMatch[0]
    const rowMatches = tableHtml.match(/<tr[\s\S]*?<\/tr>/gi) || []
    const rows = rowMatches

    const getCellTexts = (rowHtml: string) => {
      const cells = rowHtml.match(/<td[\s\S]*?<\/td>/gi) || []
      return cells.map(td =>
        cleanText(
          td
            .replace(/<td[\s\S]*?>/i, '')
            .replace(/<\/td>/i, '')
            .replace(/<br\s*\/?>/gi, ' ')
            .replace(/<[^>]+>/g, '')
        )
      )
    }

    const isHeader = (cells: string[]) => {
      if (cells.length < 5) return false
      const [n, c, v, u, r] = [cells[0], cells[1], cells[2], cells[3], cells[4]]
      return /中文名称|名称/.test(n) && /项目/.test(c) && /结果/.test(v) && /单位/.test(u) && /(参考|参考值|范围)/.test(r)
    }

    let startIndex = rows.findIndex(r => isHeader(getCellTexts(r)))
    if (startIndex === -1) startIndex = skipHeaderRows - 1
    const dataRows = rows.slice(startIndex + 1)
    for (const r of dataRows) {
      const tds = getCellTexts(r)
      if (tds.length === 0) continue
      const allEmpty = tds.every(t => !t)
      if (allEmpty) continue
      if (tds.length >= 3) {
        const [name, code, value, unit, range] = [
          tds[0] || '',
          tds[1] || '',
          tds[2] || '',
          tds[3] || '',
          tds[4] || ''
        ]
        if (!(isHeader([name, code, value, unit, range])) && (name || value || unit || range)) {
          const extraCode = extractCodeFromName(name)
          const { value: v, abnormal, symbol } = splitAbnormal(value)
          groups.left.push({
            name,
            code: code || extraCode,
            value: v,
            unit,
            range,
            abnormal,
            abnormal_symbol: symbol
          })
        }
      }
      if (tds.length > 5) {
        for (let i = 5; i + 1 < tds.length; i += 5) {
          const name = tds[i] || ''
          const code = tds[i + 1] || ''
          const value = tds[i + 2] || ''
          const unit = tds[i + 3] || ''
          const range = tds[i + 4] || ''
          if (isHeader([name, code, value, unit, range])) continue
          if (!(name || value || unit || range)) continue
          const extraCode = extractCodeFromName(name)
          const { value: v, abnormal, symbol } = splitAbnormal(value)
          groups.right.push({
            name,
            code: code || extraCode,
            value: v,
            unit,
            range,
            abnormal,
            abnormal_symbol: symbol
          })
        }
      }
    }
  } catch (e) {
    // ignore parse errors; return empty groups
  }
  return groups
}

export function toFlatMetrics(groups: MetricGroups): MetricItem[] {
  return [...(groups.left || []), ...(groups.right || [])]
}
