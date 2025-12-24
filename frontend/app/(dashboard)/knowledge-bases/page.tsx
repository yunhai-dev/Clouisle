import { Header } from '@/components/layout/header'
import { KnowledgeBasesClient } from './_components'

export default function KnowledgeBasesPage() {
  return (
    <div className="flex h-full flex-col">
      <Header />
      <div className="flex flex-1 flex-col gap-4 overflow-auto p-4">
        <KnowledgeBasesClient />
      </div>
    </div>
  )
}
