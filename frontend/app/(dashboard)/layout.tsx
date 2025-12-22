'use client'

import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/layout/app-sidebar'
import { useSettings } from '@/hooks/use-settings'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { sidebarVariant, layoutVariant, direction, mounted } = useSettings()

  // 在 mounted 前使用默认值，避免水合不匹配
  const effectiveSidebarVariant = mounted ? sidebarVariant : 'inset'
  const effectiveLayoutVariant = mounted ? layoutVariant : 'default'
  const effectiveDirection = mounted ? direction : 'ltr'

  // Layout 控制侧边栏状态:
  // - default: 侧边栏完全展开
  // - compact: 侧边栏收缩只显示图标
  // - full: 侧边栏完全隐藏
  const sidebarOpen = effectiveLayoutVariant === 'default'
  const collapsible = effectiveLayoutVariant === 'full' ? 'offExamples' : effectiveLayoutVariant === 'compact' ? 'icon' : 'offExamples'
  
  // Direction 控制侧边栏位置
  const sidebarSide = effectiveDirection === 'rtl' ? 'right' : 'left'

  return (
    <SidebarProvider defaultOpen={sidebarOpen} key={effectiveLayoutVariant}>
      <AppSidebar 
        variant={effectiveSidebarVariant} 
        collapsible={collapsible} 
        side={sidebarSide}
      />
      <SidebarInset>
        {children}
      </SidebarInset>
    </SidebarProvider>
  )
}
