'use client'

import * as React from 'react'

interface DocxPreviewProps {
  blob: Blob
  onError: () => void
}

export function DocxPreview({ blob, onError }: DocxPreviewProps) {
  const bodyRef = React.useRef<HTMLDivElement>(null)
  const stylesRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    let cancelled = false
    const body = bodyRef.current
    const styles = stylesRef.current
    if (!body || !styles) return

    body.replaceChildren()
    styles.replaceChildren()

    void import('docx-preview')
      .then(({ renderAsync }) => {
        if (cancelled || !body || !styles) return
        return renderAsync(blob, body, styles, {
          breakPages: true,
          inWrapper: true,
          useBase64URL: true,
        })
      })
      .catch(() => {
        if (!cancelled) onError()
      })

    return () => {
      cancelled = true
      body.replaceChildren()
      styles.replaceChildren()
    }
  }, [blob, onError])

  return (
    <div className="w-fit bg-muted/20 p-4">
      <div ref={stylesRef} className="hidden" aria-hidden="true" />
      <div ref={bodyRef} className="w-fit" />
    </div>
  )
}
