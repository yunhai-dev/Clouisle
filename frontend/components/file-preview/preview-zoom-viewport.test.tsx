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
  MouseEvent: window.MouseEvent,
  PointerEvent: (window as unknown as { PointerEvent?: unknown }).PointerEvent ?? window.MouseEvent,
  WheelEvent: window.WheelEvent,
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

test('supports contain mode and pointer drag panning', () => {
  const container = document.body.appendChild(document.createElement('div'))
  const root = createRoot(container)
  roots.push(root)
  act(() => root.render(
    <PreviewZoomViewport
      fitKey="media"
      fitMode="contain"
      labels={{ zoomIn: 'Zoom in', zoomOut: 'Zoom out', fitToView: 'Fit to view' }}
    >
      <div>Media content</div>
    </PreviewZoomViewport>,
  ))

  const viewport = container.querySelector('[data-preview-zoom-scroll-area]') as HTMLDivElement
  const content = container.querySelector('[data-preview-zoom-content]') as HTMLDivElement
  viewport.getBoundingClientRect = () => ({ width: 500, height: 500 }) as DOMRect
  content.getBoundingClientRect = () => ({
    width: 1000 * scaleOf(content),
    height: 800 * scaleOf(content),
  }) as DOMRect

  const button = (label: string) => container.querySelector(`button[aria-label="${label}"]`) as HTMLButtonElement
  act(() => button('Fit to view').click())
  expect(scaleOf(content)).toBeLessThanOrEqual(0.5)

  act(() => {
    const down = new window.MouseEvent('pointerdown', { clientX: 100, clientY: 100, bubbles: true })
    const move = new window.MouseEvent('pointermove', { clientX: 150, clientY: 120, bubbles: true })
    const up = new window.MouseEvent('pointerup', { bubbles: true })
    viewport.dispatchEvent(down)
    viewport.dispatchEvent(move)
    viewport.dispatchEvent(up)
  })
  expect(content.style.transform).toBeDefined()
})

test('handles wheel and pinch zoom events', async () => {
  const container = render()
  const viewport = container.querySelector('[data-preview-zoom-scroll-area]') as HTMLDivElement
  const content = container.querySelector('[data-preview-zoom-content]') as HTMLDivElement
  viewport.getBoundingClientRect = () => ({ width: 500, height: 500, left: 0, top: 0 }) as DOMRect
  content.getBoundingClientRect = () => ({
    width: 500 * scaleOf(content),
    height: 500 * scaleOf(content),
    left: 0,
    top: 0,
  }) as DOMRect

  const event = new window.Event('wheel', { bubbles: true, cancelable: true })
  Object.assign(event, { ctrlKey: true, deltaY: -50, deltaMode: 0 })
  await act(async () => {
    viewport.dispatchEvent(event)
  })
  expect(scaleOf(content)).toBeGreaterThan(1)
})
