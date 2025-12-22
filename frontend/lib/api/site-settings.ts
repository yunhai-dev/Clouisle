import { api } from './client'

export interface SiteSetting {
  key: string
  value: unknown
  value_type: string
  category: string
  description?: string
  is_public: boolean
}

export interface SiteSettings {
  settings: Record<string, unknown>
}

export interface PublicSiteSettings {
  site_name: string
  site_description: string
  site_url: string
  site_icon: string
  allow_registration: boolean
  require_approval: boolean
  email_verification: boolean
  enable_captcha: boolean
  allow_account_deletion: boolean
}

export interface GeneralSettings {
  site_name: string
  site_description: string
  site_url: string
  site_icon: string
  allow_registration: boolean
  require_approval: boolean
  email_verification: boolean
  allow_account_deletion: boolean
}

export interface SecuritySettings {
  min_password_length: number
  require_uppercase: boolean
  require_number: boolean
  require_special_char: boolean
  session_timeout_days: number
  single_session: boolean
  max_login_attempts: number
  lockout_duration_minutes: number
  enable_captcha: boolean
}

export interface EmailSettings {
  smtp_enabled: boolean
  smtp_host: string
  smtp_port: number
  smtp_encryption: 'none' | 'ssl' | 'tls'
  smtp_username: string
  smtp_password: string
  email_from_name: string
  email_from_address: string
}

export const siteSettingsApi = {
  /**
   * Get public site settings (no auth required)
   */
  async getPublic(): Promise<PublicSiteSettings> {
    return api.get<PublicSiteSettings>('/site-settings/public')
  },

  /**
   * Get all settings (admin only)
   */
  async getAll(category?: string): Promise<Record<string, unknown>> {
    const params = category ? `?category=${category}` : ''
    const res = await api.get<SiteSettings>(`/site-settings${params}`)
    return res.settings
  },

  /**
   * Get a specific setting
   */
  async get(key: string): Promise<SiteSetting> {
    return api.get<SiteSetting>(`/site-settings/${key}`)
  },

  /**
   * Update a specific setting
   */
  async update(key: string, value: unknown): Promise<SiteSetting> {
    return api.put<SiteSetting>(`/site-settings/${key}`, { value })
  },

  /**
   * Bulk update multiple settings
   */
  async bulkUpdate(settings: Record<string, unknown>): Promise<Record<string, unknown>> {
    const res = await api.put<SiteSettings>('/site-settings', { settings })
    return res.settings
  },

  /**
   * Reset settings to default values
   */
  async reset(category?: string): Promise<Record<string, unknown>> {
    const params = category ? `?category=${category}` : ''
    const res = await api.post<SiteSettings>(`/site-settings/reset${params}`, null)
    return res.settings
  },

  /**
   * Get general settings
   */
  async getGeneral(): Promise<GeneralSettings> {
    const settings = await this.getAll('general')
    return {
      site_name: settings.site_name ?? 'Clouisle',
      site_description: settings.site_description ?? '',
      site_url: settings.site_url ?? '',
      site_icon: settings.site_icon ?? '',
      allow_registration: settings.allow_registration ?? true,
      require_approval: settings.require_approval ?? false,
      email_verification: settings.email_verification ?? true,
      allow_account_deletion: settings.allow_account_deletion ?? true,
    }
  },

  /**
   * Update general settings
   */
  async updateGeneral(data: Partial<GeneralSettings>): Promise<Record<string, unknown>> {
    return this.bulkUpdate(data)
  },

  /**
   * Get security settings
   */
  async getSecurity(): Promise<SecuritySettings> {
    const settings = await this.getAll('security')
    return {
      min_password_length: settings.min_password_length ?? 8,
      require_uppercase: settings.require_uppercase ?? true,
      require_number: settings.require_number ?? true,
      require_special_char: settings.require_special_char ?? false,
      session_timeout_days: settings.session_timeout_days ?? 30,
      single_session: settings.single_session ?? false,
      max_login_attempts: settings.max_login_attempts ?? 5,
      lockout_duration_minutes: settings.lockout_duration_minutes ?? 15,
      enable_captcha: settings.enable_captcha ?? false,
    }
  },

  /**
   * Update security settings
   */
  async updateSecurity(data: Partial<SecuritySettings>): Promise<Record<string, unknown>> {
    return this.bulkUpdate(data)
  },

  /**
   * Get email settings
   */
  async getEmail(): Promise<EmailSettings> {
    const settings = await this.getAll('email')
    return {
      smtp_enabled: settings.smtp_enabled ?? false,
      smtp_host: settings.smtp_host ?? '',
      smtp_port: settings.smtp_port ?? 587,
      smtp_encryption: settings.smtp_encryption ?? 'tls',
      smtp_username: settings.smtp_username ?? '',
      smtp_password: settings.smtp_password ?? '',
      email_from_name: settings.email_from_name ?? 'Clouisle',
      email_from_address: settings.email_from_address ?? '',
    }
  },

  /**
   * Update email settings
   */
  async updateEmail(data: Partial<EmailSettings>): Promise<Record<string, unknown>> {
    return this.bulkUpdate(data)
  },

  /**
   * Send test email
   */
  async sendTestEmail(email: string): Promise<void> {
    await api.post<null>('/site-settings/test-email', { email })
  },
}
