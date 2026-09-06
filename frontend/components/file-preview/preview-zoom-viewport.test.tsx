import { afterEach, expect, test } from 'bun:test'
import { Window } from 'happy-dom'
import React, { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { PreviewZoomViewport } from './preview-zoom-viewport'

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

class TestResizeObserver {
  static latest: TestResizeObserver | null = null
  private readonly callback: ResizeObserverCallback

  constructor(callback: ResizeObserverCallback) {
    this.callback = callback
    TestResizeObserver.latest = this
  }

  observe() {}
  disconnect() {}
  unobserve() {}

  trigger() {
    this.callback([], this as unknown as ResizeObserver)
  }
}

globalThis.ResizeObserver = TestResizeObserver as unknown as typeof ResizeObserver

const roots: Root[] = []
afterEach(() => {
  for (const root of roots.splice(0)) act(() => root.unmount())
  document.body.replaceChildren()
  TestResizeObserver.latest = null
})

function render() {
  const container = document.body.appendChild(document.createElement('div'))
  const root = createRoot(container)
  roots.push(root)
  act(() => root.render(
    <PreviewZoomViewport
      fitKey="document"
      fitMode="width"
      labels={{ zoomIn: 'Zoom in', zoomOut: 'Zoom out', fitToView: 'Fit to view' }}
    >
      <div>Document content</div>
    </PreviewZoomViewport>,
  ))
  return container
}

function scaleOf(element: HTMLElement) {
  const match = element.style.transform.match(/scale\(([^)]+)\)/)
  return Number(match?.[1] || 1)
}

test('fits wide content to the viewport and allows manual zoom controls', () => {
  const container = render()
  const viewport = container.querySelector('[data-preview-zoom-scroll-area]') as HTMLDivElement
  const content = container.querySelector('[data-preview-zoom-content]') as HTMLDivElement
  viewport.getBoundingClientRect = () => ({ width: 548, height: 648 }) as DOMRect
  content.getBoundingClientRect = () => ({
    width: 1000 * scaleOf(content),
    height: 800 * scaleOf(content),
  }) as DOMRect

  const button = (label: string) => container.querySelector(`button[aria-label="${label}"]`) as HTMLButtonElement

  act(() => button('Fit to view').click())
  expect(scaleOf(content)).toBe(0.5)

  act(() => button('Zoom in').click())
  expect(scaleOf(content)).toBeCloseTo(0.6, 10)

  act(() => button('Zoom out').click())
  expect(scaleOf(content)).toBe(0.5)
})

test('keeps a manually adjusted zoom during viewport resize', () => {
  const container = render()
  const viewport = container.querySelector('[data-preview-zoom-scroll-area]') as HTMLDivElement
  const content = container.querySelector('[data-preview-zoom-content]') as HTMLDivElement
  viewport.getBoundingClientRect = () => ({ width: 548, height: 648 }) as DOMRect
  content.getBoundingClientRect = () => ({
    width: 1000 * scaleOf(content),
    height: 800 * scaleOf(content),
  }) as DOMRect

  const button = (label: string) => container.querySelector(`button[aria-label="${label}"]`) as HTMLButtonElement
  act(() => button('Zoom in').click())
  expect(scaleOf(content)).toBe(1.1)

  viewport.getBoundingClientRect = () => ({ width: 1048, height: 848 }) as DOMRect
  act(() => TestResizeObserver.latest?.trigger())

  expect(scaleOf(content)).toBe(1.1)
})
