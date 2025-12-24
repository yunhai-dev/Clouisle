import { SearchTestClient } from './_components/search-test-client'

interface PageProps {
  params: Promise<{
    id: string
  }>
}

export default async function SearchTestPage({ params }: PageProps) {
  const { id } = await params
  return <SearchTestClient knowledgeBaseId={id} />
}
