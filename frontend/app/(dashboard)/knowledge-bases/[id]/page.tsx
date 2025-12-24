import { Header } from '@/components/layout/header'
import { KnowledgeBaseDetailClient } from './_components'

export default async function KnowledgeBaseDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  
  return (
    <div className="flex h-full flex-col">
      <Header />
      <div className="flex flex-1 flex-col gap-4 overflow-auto p-4">
        <KnowledgeBaseDetailClient knowledgeBaseId={id} />
      </div>
    </div>
  )
}
