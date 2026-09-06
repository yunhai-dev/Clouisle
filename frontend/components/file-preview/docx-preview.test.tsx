import { afterEach, expect, mock, test } from 'bun:test'
import { Window } from 'happy-dom'
import React, { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { DocxPreview } from './docx-preview'

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

test('renders docx preview container and handles render errors gracefully', async () => {
  const onError = mock(() => {})
  const container = render(<DocxPreview blob={new Blob(['not a real docx'])} onError={onError} />)
  await act(async () => {
    for (let attempt = 0; attempt < 100 && onError.mock.calls.length === 0; attempt += 1) {
      await Bun.sleep(10)
    }
  })

  expect(container.querySelector('div')).toBeTruthy()
  expect(onError).toHaveBeenCalled()
})
