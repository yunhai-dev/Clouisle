import { Header } from '@/components/layout/header'
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
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex-1 min-h-0">
        <DocumentsPreviewClient 
          knowledgeBaseId={id} 
          documentIds={documentIds} 
        />
      </div>
    </div>
  )
}
