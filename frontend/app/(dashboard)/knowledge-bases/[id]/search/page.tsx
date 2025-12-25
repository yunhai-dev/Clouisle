import { Header } from '@/components/layout/header'
import { SearchTestClient } from './_components/search-test-client'

interface PageProps {
  params: Promise<{
    id: string
  }>
}

export default async function SearchTestPage({ params }: PageProps) {
  const { id } = await params
  return (
    <div className="flex h-full flex-col">
      <Header />
      <div className="flex-1 min-h-0">
        <SearchTestClient knowledgeBaseId={id} />
      </div>
    </div>
  )
}
