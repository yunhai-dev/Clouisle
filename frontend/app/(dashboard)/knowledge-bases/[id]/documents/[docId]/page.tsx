import { Header } from '@/components/layout/header'
import { DocumentDetailClient } from './_components/document-detail-client'

export default async function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string; docId: string }>
}) {
  const { id, docId } = await params
  
  return (
    <div className="flex h-full flex-col">
      <Header />
      <div className="flex flex-1 flex-col overflow-hidden">
        <DocumentDetailClient knowledgeBaseId={id} documentId={docId} />
      </div>
    </div>
  )
}
