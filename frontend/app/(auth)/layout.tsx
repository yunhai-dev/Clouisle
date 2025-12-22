import { LocaleSwitcher } from '@/components/locale-switcher'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50">
      {/* 语言切换 - 固定在右上角 */}
      <div className="fixed top-4 right-4">
        <LocaleSwitcher />
      </div>
      <div className="w-full max-w-md p-4">
        {children}
      </div>
    </div>
  )
}
