import { Header } from '@/components/layout/header'
import { TeamsClient } from './_components'

export default async function TeamsPage() {
  return (
    <div className="flex h-full flex-col">
      <Header />
      <div className="flex flex-1 flex-col gap-4 overflow-auto p-4">
        <TeamsClient />
      </div>
    </div>
  )
}
