import { afterEach, expect, mock, test } from 'bun:test'
import { Window } from 'happy-dom'
import React, { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { FilePreviewPanel } from './file-preview-panel'

const window = new Window({ url: 'http://localhost' })
Object.assign(globalThis, {
  window,
  document: window.document,
  navigator: window.navigator,
  HTMLElement: window.HTMLElement,
  Node: window.Node,
  Event: window.Event,
})
;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const roots: Root[] = []
afterEach(() => {
  for (const root of roots.splice(0)) act(() => root.unmount())
  document.body.replaceChildren()
})

function render(element: React.ReactElement) {
  const container = document.body.appendChild(document.createElement('div'))
  const root = createRoot(container)
  roots.push(root)
  act(() => root.render(element))
  return container
}

async function flush() {
  await act(async () => {
    await Bun.sleep(0)
  })
}

test('loads text from a provided file loader and keeps it downloadable', async () => {
  const loadFile = mock(async () => new Blob(['hello preview'], { type: 'text/plain' }))
  const createObjectURL = mock(() => 'blob:preview')
  const revokeObjectURL = mock(() => {})
  const originalCreateObjectURL = URL.createObjectURL
  const originalRevokeObjectURL = URL.revokeObjectURL
  Object.assign(URL, { createObjectURL, revokeObjectURL })

  try {
    const container = render(
      <FilePreviewPanel
        file={{ filename: 'notes.txt', mimeType: 'text/plain' }}
        loadFile={loadFile}
      />
    )
    await flush()

    expect(loadFile).toHaveBeenCalledTimes(1)
    expect(container.textContent).toContain('hello preview')
    const downloadButton = container.querySelector('button[aria-label="Download"]') as HTMLButtonElement
    expect(downloadButton.disabled).toBe(false)

    act(() => downloadButton.click())
    expect(createObjectURL).toHaveBeenCalledWith(expect.any(Blob))
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:preview')
  } finally {
    Object.assign(URL, { createObjectURL: originalCreateObjectURL, revokeObjectURL: originalRevokeObjectURL })
  }
})

test('loads an unsupported knowledge-base file so it remains downloadable', async () => {
  const loadFile = mock(async () => new Blob(['legacy document']))
  const container = render(
    <FilePreviewPanel
      file={{ filename: 'legacy.doc', mimeType: 'application/msword' }}
      loadFile={loadFile}
    />
  )
  await flush()

  expect(loadFile).toHaveBeenCalledTimes(1)
  expect(container.textContent).toContain('This file type cannot be previewed here')
  expect((container.querySelector('button[aria-label="Download"]') as HTMLButtonElement).disabled).toBe(false)
})
test('renders PDF using native viewer with FitH and without overlapping zoom floating controls', async () => {
  const loadFile = mock(async () => new Blob(['pdf preview'], { type: 'application/pdf' }))
  const originalCreateObjectURL = URL.createObjectURL
  const originalRevokeObjectURL = URL.revokeObjectURL
  Object.assign(URL, {
    createObjectURL: () => 'blob:pdf-preview',
    revokeObjectURL: () => {},
  })

  try {
    const container = render(
      <FilePreviewPanel
        file={{ filename: 'report.pdf', mimeType: 'application/pdf' }}
        loadFile={loadFile}
      />,
    )
    await flush()
    expect((container.querySelector('iframe') as HTMLIFrameElement).src).toContain('#view=FitH')
    expect(container.querySelector('[data-slot="file-preview-zoom-controls"]')).toBeNull()
  } finally {
    Object.assign(URL, { createObjectURL: originalCreateObjectURL, revokeObjectURL: originalRevokeObjectURL })
  }
})
