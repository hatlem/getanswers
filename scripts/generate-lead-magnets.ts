/**
 * Generate Lead Magnet PDFs for GetAnswers
 *
 * Usage: cd scripts && npx tsx generate-lead-magnets.ts
 */

import puppeteer from 'puppeteer'
import { marked } from 'marked'
import { mkdir, readFile } from 'fs/promises'
import { join, dirname } from 'path'
import { existsSync } from 'fs'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const projectRoot = join(__dirname, '..')

// Brand config
const brand = {
  name: 'GetAnswers',
  tagline: 'AI Email Assistant',
  domain: 'getanswers.co',
  colors: {
    primary: '#3b82f6',
    secondary: '#2563eb',
    accent: '#60a5fa',
  },
  category: 'Email Productivity',
}

interface LeadMagnetConfig {
  title: string
  description: string
  contentPath: string
  slug: string
  category: string
  coverFeatures: string[]
  salesCTA: {
    headline: string
    subheadline: string
    buttonText: string
  }
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function generateHTML(config: LeadMagnetConfig, contentHtml: string): string {
  const { title, description, category, coverFeatures, salesCTA } = config
  const { colors, name, domain } = brand
  const year = new Date().getFullYear()
  const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long' })

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${escapeHtml(title)}</title>
  <style>
    @page { size: letter; margin: 0; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
      font-size: 10pt;
      line-height: 1.5;
      color: #1f2937;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    .cover-page {
      width: 8.5in;
      height: 11in;
      background: linear-gradient(145deg, ${colors.primary} 0%, ${colors.secondary} 50%, #1e293b 100%);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 0.75in;
      page-break-after: always;
      position: relative;
      overflow: hidden;
    }
    .cover-page::before {
      content: '';
      position: absolute;
      top: -50%;
      right: -30%;
      width: 80%;
      height: 100%;
      background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    }
    .cover-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      position: relative;
      z-index: 1;
    }
    .cover-brand-icon {
      width: 48px;
      height: 48px;
      background: rgba(255,255,255,0.15);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: bold;
      color: white;
    }
    .cover-brand-text { font-size: 18pt; font-weight: 700; color: white; }
    .cover-main {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      position: relative;
      z-index: 1;
    }
    .cover-category {
      display: inline-block;
      background: rgba(255,255,255,0.2);
      color: white;
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 10pt;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 24px;
      width: fit-content;
    }
    .cover-title {
      font-size: 38pt;
      font-weight: 800;
      color: white;
      line-height: 1.1;
      margin-bottom: 20px;
      letter-spacing: -0.02em;
    }
    .cover-description {
      font-size: 14pt;
      color: rgba(255,255,255,0.85);
      line-height: 1.5;
      max-width: 5.5in;
    }
    .cover-features {
      display: flex;
      gap: 32px;
      margin-top: 40px;
    }
    .cover-feature {
      display: flex;
      align-items: center;
      gap: 8px;
      color: rgba(255,255,255,0.9);
      font-size: 10pt;
    }
    .cover-feature-icon {
      width: 20px;
      height: 20px;
      background: rgba(255,255,255,0.2);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10pt;
    }
    .cover-footer {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      position: relative;
      z-index: 1;
    }
    .cover-url { color: rgba(255,255,255,0.7); font-size: 11pt; }
    .cover-version { color: rgba(255,255,255,0.5); font-size: 9pt; }

    .content-page {
      width: 8.5in;
      min-height: 11in;
      padding: 0.6in 0.7in;
      page-break-after: always;
    }
    .content-header {
      background: linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%);
      color: white;
      padding: 0.3in 0.4in;
      margin: -0.6in -0.7in 0.4in -0.7in;
    }
    .content-title { font-size: 20pt; font-weight: 700; margin-bottom: 4px; }
    .content-subtitle { font-size: 10pt; opacity: 0.9; }
    .content-body { font-size: 10pt; line-height: 1.6; }
    .content-body h1 { font-size: 16pt; color: ${colors.primary}; margin: 24px 0 12px 0; font-weight: 700; }
    .content-body h2 { font-size: 14pt; color: ${colors.primary}; margin: 20px 0 10px 0; font-weight: 700; }
    .content-body h3 { font-size: 12pt; color: ${colors.secondary}; margin: 16px 0 8px 0; font-weight: 600; }
    .content-body p { margin: 0 0 12px 0; }
    .content-body ul, .content-body ol { margin: 0 0 12px 20px; }
    .content-body li { margin: 4px 0; }
    .content-body strong { color: ${colors.primary}; }
    .content-body code {
      background: #f3f4f6;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 9pt;
    }
    .content-body pre {
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 12px 16px;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 8pt;
      margin: 12px 0;
    }
    .content-body pre code { background: none; padding: 0; color: inherit; }
    .content-body blockquote {
      border-left: 4px solid ${colors.primary};
      padding-left: 16px;
      margin: 12px 0;
      color: #4b5563;
      font-style: italic;
    }
    .content-body table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 9pt; }
    .content-body th {
      background: ${colors.primary};
      color: white;
      padding: 8px 12px;
      text-align: left;
      font-weight: 600;
    }
    .content-body td { padding: 8px 12px; border-bottom: 1px solid #e5e7eb; }
    .content-body tr:nth-child(even) { background: #f9fafb; }

    .sales-page {
      width: 8.5in;
      height: 11in;
      background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
      padding: 0.6in;
      display: flex;
      flex-direction: column;
    }
    .sales-header { text-align: center; margin-bottom: 0.5in; }
    .sales-pretitle {
      font-size: 10pt;
      color: ${colors.primary};
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 8px;
    }
    .sales-title {
      font-size: 28pt;
      font-weight: 800;
      color: #1e293b;
      line-height: 1.2;
      margin-bottom: 12px;
    }
    .sales-subtitle {
      font-size: 12pt;
      color: #64748b;
      max-width: 5in;
      margin: 0 auto;
      line-height: 1.5;
    }
    .sales-features { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 0.4in; }
    .sales-feature-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .sales-feature-icon {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, ${colors.primary}20 0%, ${colors.secondary}20 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      margin-bottom: 12px;
    }
    .sales-feature-title { font-size: 11pt; font-weight: 700; color: #1e293b; margin-bottom: 6px; }
    .sales-feature-desc { font-size: 9pt; color: #64748b; line-height: 1.4; }
    .sales-cta-box {
      background: linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%);
      border-radius: 16px;
      padding: 32px;
      text-align: center;
      margin-bottom: 0.3in;
    }
    .sales-cta-title { font-size: 18pt; font-weight: 700; color: white; margin-bottom: 8px; }
    .sales-cta-subtitle { font-size: 11pt; color: rgba(255,255,255,0.85); margin-bottom: 20px; }
    .sales-cta-button {
      display: inline-block;
      background: white;
      color: ${colors.primary};
      padding: 14px 32px;
      border-radius: 8px;
      font-size: 12pt;
      font-weight: 700;
    }
    .sales-cta-url { margin-top: 12px; font-size: 10pt; color: rgba(255,255,255,0.7); }
    .sales-resources { margin-bottom: 0.3in; }
    .sales-resources-title { font-size: 11pt; font-weight: 700; color: #1e293b; margin-bottom: 12px; text-align: center; }
    .sales-resources-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    .sales-resource {
      background: white;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .sales-resource-icon { font-size: 20px; margin-bottom: 6px; }
    .sales-resource-name { font-size: 8pt; font-weight: 600; color: #1e293b; }
    .sales-footer {
      margin-top: auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 16px;
      border-top: 1px solid #cbd5e1;
    }
    .sales-footer-brand { display: flex; align-items: center; gap: 8px; }
    .sales-footer-logo {
      width: 28px;
      height: 28px;
      background: ${colors.primary};
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 14px;
      font-weight: bold;
    }
    .sales-footer-text { font-size: 9pt; color: #64748b; }
    .sales-footer-links { display: flex; gap: 20px; font-size: 8pt; color: #64748b; }
    .sales-footer-links a { color: ${colors.primary}; text-decoration: none; }
  </style>
</head>
<body>
  <div class="cover-page">
    <div class="cover-brand">
      <div class="cover-brand-icon">${name.charAt(0)}</div>
      <div class="cover-brand-text">${escapeHtml(name)}</div>
    </div>
    <div class="cover-main">
      <div class="cover-category">${escapeHtml(category)}</div>
      <h1 class="cover-title">${escapeHtml(title)}</h1>
      <p class="cover-description">${escapeHtml(description)}</p>
      <div class="cover-features">
        ${coverFeatures.map(f => `<div class="cover-feature"><div class="cover-feature-icon">&#10003;</div><span>${escapeHtml(f)}</span></div>`).join('')}
      </div>
    </div>
    <div class="cover-footer">
      <div class="cover-url">${domain}</div>
      <div class="cover-version">${date}</div>
    </div>
  </div>

  <div class="content-page">
    <div class="content-header">
      <h1 class="content-title">${escapeHtml(title)}</h1>
      <p class="content-subtitle">${escapeHtml(description)}</p>
    </div>
    <div class="content-body">${contentHtml}</div>
  </div>

  <div class="sales-page">
    <div class="sales-header">
      <div class="sales-pretitle">Take the Next Step</div>
      <h2 class="sales-title">${escapeHtml(salesCTA.headline)}</h2>
      <p class="sales-subtitle">${escapeHtml(salesCTA.subheadline)}</p>
    </div>
    <div class="sales-features">
      <div class="sales-feature-card">
        <div class="sales-feature-icon">&#128200;</div>
        <div class="sales-feature-title">Proven Results</div>
        <div class="sales-feature-desc">Join thousands of professionals already seeing results.</div>
      </div>
      <div class="sales-feature-card">
        <div class="sales-feature-icon">&#9889;</div>
        <div class="sales-feature-title">Easy Setup</div>
        <div class="sales-feature-desc">Get started in minutes, not hours or days.</div>
      </div>
      <div class="sales-feature-card">
        <div class="sales-feature-icon">&#128202;</div>
        <div class="sales-feature-title">Expert Support</div>
        <div class="sales-feature-desc">Our team is here to help you succeed.</div>
      </div>
      <div class="sales-feature-card">
        <div class="sales-feature-icon">&#128279;</div>
        <div class="sales-feature-title">No Risk</div>
        <div class="sales-feature-desc">Try free with no credit card required.</div>
      </div>
    </div>
    <div class="sales-cta-box">
      <div class="sales-cta-title">${escapeHtml(salesCTA.buttonText)}</div>
      <div class="sales-cta-subtitle">Start your free trial today</div>
      <div class="sales-cta-button">${escapeHtml(salesCTA.buttonText)}</div>
      <div class="sales-cta-url">${domain}/signup</div>
    </div>
    <div class="sales-resources">
      <div class="sales-resources-title">More Free Resources</div>
      <div class="sales-resources-grid">
        <div class="sales-resource"><div class="sales-resource-icon">&#128221;</div><div class="sales-resource-name">Templates</div></div>
        <div class="sales-resource"><div class="sales-resource-icon">&#128218;</div><div class="sales-resource-name">Guides</div></div>
        <div class="sales-resource"><div class="sales-resource-icon">&#127891;</div><div class="sales-resource-name">Tutorials</div></div>
        <div class="sales-resource"><div class="sales-resource-icon">&#128187;</div><div class="sales-resource-name">API Docs</div></div>
        <div class="sales-resource"><div class="sales-resource-icon">&#128161;</div><div class="sales-resource-name">Blog</div></div>
        <div class="sales-resource"><div class="sales-resource-icon">&#129309;</div><div class="sales-resource-name">Community</div></div>
      </div>
    </div>
    <div class="sales-footer">
      <div class="sales-footer-brand">
        <div class="sales-footer-logo">${name.charAt(0)}</div>
        <div class="sales-footer-text">&copy; ${year} ${escapeHtml(name)}. All rights reserved.</div>
      </div>
      <div class="sales-footer-links">
        <a href="https://${domain}">Website</a>
        <a href="https://${domain}/resources">Resources</a>
        <a href="https://${domain}/contact">Contact</a>
      </div>
    </div>
  </div>
</body>
</html>`
}

async function generatePDF(config: LeadMagnetConfig): Promise<void> {
  const outputDir = join(projectRoot, 'frontend/public/lead-magnets')

  if (!existsSync(outputDir)) {
    await mkdir(outputDir, { recursive: true })
  }

  const markdown = await readFile(config.contentPath, 'utf-8')
  const contentHtml = await marked(markdown)
  const html = generateHTML(config, contentHtml)

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  })

  const page = await browser.newPage()
  await page.setViewport({ width: 816, height: 1056, deviceScaleFactor: 2 })
  await page.setContent(html, { waitUntil: 'domcontentloaded' })

  const pdfPath = join(outputDir, `${config.slug}.pdf`)
  const pdfBuffer = await page.pdf({
    path: pdfPath,
    format: 'letter',
    printBackground: true,
  })

  await browser.close()

  console.log(`   Created: ${pdfPath}`)
  console.log(`   Size: ${(pdfBuffer.length / 1024).toFixed(1)} KB`)
}

const leadMagnets: LeadMagnetConfig[] = [
  {
    title: 'Inbox Zero Guide',
    description: 'Achieve and maintain inbox zero with this proven system',
    contentPath: join(projectRoot, 'frontend/public/lead-magnets/inbox-zero-guide.md'),
    slug: 'inbox-zero-guide',
    category: 'PRODUCTIVITY',
    coverFeatures: ['Proven system', 'Daily habits', 'Peace of mind'],
    salesCTA: {
      headline: 'Ready to Transform Your Productivity?',
      subheadline: 'GetAnswers helps you achieve better results, faster.',
      buttonText: 'Start Free Trial',
    },
  },
  {
    title: 'Email Automation Prompt Library',
    description: '100+ production-ready prompts for AI email triage and response',
    contentPath: join(projectRoot, 'frontend/public/lead-magnets/email-automation-prompts.md'),
    slug: 'email-automation-prompts',
    category: 'AI PROMPTS',
    coverFeatures: ['100+ prompts', 'Copy-paste ready', 'Battle-tested'],
    salesCTA: {
      headline: 'Ready to Automate Your Email?',
      subheadline: 'GetAnswers uses AI to handle your inbox automatically.',
      buttonText: 'Start Free Trial',
    },
  },
]

async function main() {
  console.log('Generating lead magnet PDFs for GetAnswers...\n')

  for (const config of leadMagnets) {
    try {
      console.log(`Generating: ${config.title}`)
      await generatePDF(config)
      console.log('')
    } catch (error) {
      console.error(`Failed: ${config.title}`)
      console.error(`Error: ${error instanceof Error ? error.message : error}\n`)
    }
  }

  console.log('Done!')
}

main().catch(console.error)
