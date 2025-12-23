/**
 * Brand configuration for GetAnswers
 */

export interface ProjectBrand {
  name: string
  tagline: string
  domain: string
  colors: {
    primary: string
    secondary: string
    accent: string
  }
  category: string
}

export const defaultBrandConfigs: Record<string, ProjectBrand> = {
  getanswers: {
    name: 'GetAnswers',
    tagline: 'AI Email Assistant',
    domain: 'getanswers.co',
    colors: {
      primary: '#3b82f6',
      secondary: '#2563eb',
      accent: '#60a5fa',
    },
    category: 'Email Productivity',
  },
}
