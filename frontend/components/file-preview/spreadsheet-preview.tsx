'use client'

import * as React from 'react'

interface SpreadsheetPreviewLabels {
  sheet: string
  rowsLimited: (values: { rows: number; columns: number }) => string
  parseError: string
}

interface SpreadsheetSheet {
  name: string
  rows: string[][]
  rowCount: number
  columnCount: number
  visibleColumnCount: number
  truncated: boolean
}

interface SpreadsheetPreviewProps {
  blob: Blob
  labels: SpreadsheetPreviewLabels
}

const MAX_ROWS = 200
const MAX_COLUMNS = 50

function cellToText(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (value instanceof Date) return value.toLocaleString()
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value)
    } catch {
      return String(value)
    }
  }
  return String(value)
}

export function SpreadsheetPreview({ blob, labels }: SpreadsheetPreviewProps) {
  const [sheets, setSheets] = React.useState<SpreadsheetSheet[]>([])
  const [activeSheet, setActiveSheet] = React.useState(0)
  const [isLoading, setIsLoading] = React.useState(true)
  const [hasError, setHasError] = React.useState(false)

  React.useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setSheets([])
    setActiveSheet(0)
    setHasError(false)
    void blob.arrayBuffer()
      .then((data) => import('xlsx').then((XLSX) => ({ data, XLSX })))
      .then(({ data, XLSX }) => {
        const workbook = XLSX.read(data, { type: 'array', cellDates: true, cellText: true })
        const parsedSheets = workbook.SheetNames.map((name) => {
          const sheet = workbook.Sheets[name]
          const range = sheet?.['!ref'] ? XLSX.utils.decode_range(sheet['!ref']) : null
          const rowCount = range ? range.e.r - range.s.r + 1 : 0
          const columnCount = range ? range.e.c - range.s.c + 1 : 0
          const readRange = range
            ? {
                s: range.s,
                e: {
                  r: Math.min(range.e.r, range.s.r + MAX_ROWS - 1),
                  c: Math.min(range.e.c, range.s.c + MAX_COLUMNS - 1),
                },
              }
            : undefined
          const rows = XLSX.utils.sheet_to_json(sheet, {
            header: 1,
            raw: false,
            defval: '',
            range: readRange,
          }) as unknown[][]
          const visibleRows = rows.slice(0, MAX_ROWS).map((row) => (
            Array.from({ length: Math.min(Math.max(row.length, columnCount), MAX_COLUMNS) }, (_, index) => (
              cellToText(row[index])
            ))
          ))
          const visibleColumnCount = Math.min(Math.max(columnCount, ...visibleRows.map((row) => row.length), 0), MAX_COLUMNS)

          return {
            name,
            rows: visibleRows.map((row) => row.slice(0, visibleColumnCount)),
            rowCount,
            columnCount,
            visibleColumnCount,
            truncated: rowCount > MAX_ROWS || columnCount > MAX_COLUMNS,
          }
        })

        if (!cancelled) {
          setSheets(parsedSheets)
          setIsLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setHasError(true)
          setIsLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [blob])

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-sm text-muted-foreground">
        <span aria-hidden="true" className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        <span>Loading spreadsheet...</span>
      </div>
    )
  }

  if (hasError || !sheets[activeSheet]) {
    return <div className="flex h-full items-center justify-center p-8 text-sm text-muted-foreground">{labels.parseError}</div>
  }

  const sheet = sheets[activeSheet]
  return (
    <div className="flex w-max flex-col">
      <div className="flex shrink-0 items-center gap-1 overflow-x-auto border-b bg-muted/20 px-3 py-2">
        <span className="mr-2 shrink-0 text-xs font-medium text-muted-foreground">{labels.sheet}</span>
        {sheets.map((item, index) => (
          <button
            key={`${item.name}-${index}`}
            type="button"
            className={`shrink-0 rounded-md px-2.5 py-1 text-xs transition-colors ${index === activeSheet ? 'bg-background font-medium shadow-sm' : 'text-muted-foreground hover:bg-background/70'}`}
            onClick={() => setActiveSheet(index)}
          >
            {item.name}
          </button>
        ))}
      </div>
      <div className="p-3">
        {sheet.truncated && (
          <p className="mb-3 text-xs text-muted-foreground">
            {labels.rowsLimited({ rows: MAX_ROWS, columns: MAX_COLUMNS })}
          </p>
        )}
        <table className="w-max border-collapse text-xs">
          <thead>
            <tr>
              <th className="sticky top-0 z-10 border bg-muted px-2 py-1 text-right font-medium text-muted-foreground">#</th>
              {Array.from({ length: sheet.visibleColumnCount }, (_, index) => (
                <th key={index} className="sticky top-0 z-10 border bg-muted px-2 py-1 text-left font-medium text-muted-foreground">
                  {index + 1}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sheet.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <th className="border bg-muted/50 px-2 py-1 text-right font-medium text-muted-foreground">{rowIndex + 1}</th>
                {Array.from({ length: sheet.visibleColumnCount }, (_, columnIndex) => (
                  <td key={columnIndex} className="max-w-80 whitespace-pre-wrap break-words border px-2 py-1 align-top">
                    {row[columnIndex] || ''}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
