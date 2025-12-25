import { DocumentsPreviewClient } from './_components/documents-preview-client'

export default async function DocumentsPreviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ docs?: string }>
}) {
  const { id } = await params
  const { docs } = await searchParams
  
  // 解析文档 ID 列表
  const documentIds = docs ? docs.split(',') : []
  
  return (
    <div className="h-[calc(100vh-64px)] overflow-hidden">
      <DocumentsPreviewClient 
        knowledgeBaseId={id} 
        documentIds={documentIds} 
      />
    </div>
  )
}
