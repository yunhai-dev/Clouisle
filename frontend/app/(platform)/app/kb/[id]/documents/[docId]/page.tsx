import { DocumentDetailClient } from './_components/document-detail-client'

export default async function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string; docId: string }>
}) {
  const { id, docId } = await params
  
  return (
    <div className="h-[calc(100vh-64px)] overflow-hidden">
      <DocumentDetailClient knowledgeBaseId={id} documentId={docId} />
    </div>
  )
}
