import { Header } from '@/components/layout/header'
import { DocumentDetailClient } from './_components/document-detail-client'

export default async function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string; docId: string }>
}) {
  const { id, docId } = await params
  
  return (
    <div className="flex h-svh flex-col overflow-hidden">
      <Header />
      <div className="flex-1 min-h-0 overflow-hidden">
        <DocumentDetailClient knowledgeBaseId={id} documentId={docId} />
      </div>
    </div>
  )
}
