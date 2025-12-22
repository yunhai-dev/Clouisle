import { Header } from '@/components/layout/header'
import { RolesClient } from './_components'

export default function RolesPage() {
  return (
    <div className="flex h-full flex-col">
      <Header />
      <div className="flex flex-1 flex-col gap-4 overflow-auto p-4">
        <RolesClient />
      </div>
    </div>
  )
}
