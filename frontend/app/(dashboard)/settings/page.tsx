import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'

export default async function SettingsPage() {
  redirect('/settings/profile')
}
