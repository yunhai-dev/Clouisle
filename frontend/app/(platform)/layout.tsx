'use client'

import { PlatformHeader } from '@/components/layout/platform-header'
import { TeamProvider } from '@/contexts/team-context'

export default function PlatformLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <TeamProvider>
      <div className="min-h-screen flex flex-col">
        <PlatformHeader />
        <main className="flex-1 px-8">
          {children}
        </main>
      </div>
    </TeamProvider>
  )
}
