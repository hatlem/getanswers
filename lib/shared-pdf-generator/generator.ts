/**
 * Universal Lead Magnet PDF Generator
 *
 * Generates professional PDFs with:
 * - Branded cover page
 * - Main content (from markdown or HTML)
 * - Sales/CTA page
 */

import puppeteer from 'puppeteer'
import { marked } from 'marked'
import { writeFile, mkdir, readFile } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'
import { defaultBrandConfigs, type ProjectBrand } from './brands'

export interface BrandConfig extends ProjectBrand {}

export interface LeadMagnetOptions {
  /** Title of the lead magnet */
  title: string
  /** Subtitle/description */
  description: string
  /** Content - can be markdown string or path to .md file */
  content: string
  /** Output filename (without extension) */
  slug: string
  /** Category label shown on cover */
  category?: string
  /** Project brand key or custom brand config */
  brand: string | BrandConfig
  /** Output directory */
  outputDir?: string
  /** Features to show on cover page */
  coverFeatures?: string[]
  /** CTA configuration for sales page */
  salesCTA?: {
    headline?: string
    subheadline?: string
    buttonText?: string
    buttonUrl?: string
  }
}

export interface GenerationResult {
  pdfPath: string
  pdfUrl: string
  fileSize: number
  pageCount: number
}

function getBrand(brand: string | BrandConfig): BrandConfig {
  if (typeof brand === 'string') {
    return defaultBrandConfigs[brand] || defaultBrandConfigs.getanswers
  }
  return brand
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

async function getContent(content: string): Promise<string> {
  // If content ends with .md, read the file
  if (content.endsWith('.md')) {
    const markdown = await readFile(content, 'utf-8')
    return marked(markdown) as string
  }
  // If content looks like markdown (has # or *), convert it
  if (content.includes('#') || content.includes('*') || content.includes('-')) {
    return marked(content) as string
  }
  // Otherwise assume it's HTML
  return content
}

function generateHTML(options: LeadMagnetOptions, brand: BrandConfig, contentHtml: string): string {
  const { title, description, category, coverFeatures, salesCTA } = options
  const { colors, name, tagline, domain } = brand

  const features = coverFeatures || ['Print-optimized', 'Expert-curated', 'Actionable tips']
  const categoryLabel = category || brand.category
  const year = new Date().getFullYear()
  const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long' })

  const cta = {
    headline: salesCTA?.headline || `Ready to Transform Your ${categoryLabel}?`,
    subheadline: salesCTA?.subheadline || `${name} helps you achieve better results, faster.`,
    buttonText: salesCTA?.buttonText || 'Start Free Trial',
    buttonUrl: salesCTA?.buttonUrl || `https://${domain}/onboarding`,
  }

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
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

    /* ==================== COVER PAGE ==================== */
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
    .cover-brand-text {
      font-size: 18pt;
      font-weight: 700;
      color: white;
    }
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

    /* ==================== CONTENT PAGE ==================== */
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
    .content-title {
      font-size: 20pt;
      font-weight: 700;
      margin-bottom: 4px;
    }
    .content-subtitle {
      font-size: 10pt;
      opacity: 0.9;
    }
    .content-body {
      font-size: 10pt;
      line-height: 1.6;
    }
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
    .content-body pre code {
      background: none;
      padding: 0;
      color: inherit;
    }
    .content-body blockquote {
      border-left: 4px solid ${colors.primary};
      padding-left: 16px;
      margin: 12px 0;
      color: #4b5563;
      font-style: italic;
    }
    .content-body table {
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      font-size: 9pt;
    }
    .content-body th {
      background: ${colors.primary};
      color: white;
      padding: 8px 12px;
      text-align: left;
      font-weight: 600;
    }
    .content-body td {
      padding: 8px 12px;
      border-bottom: 1px solid #e5e7eb;
    }
    .content-body tr:nth-child(even) { background: #f9fafb; }
    .content-footer {
      position: fixed;
      bottom: 0.3in;
      left: 0.7in;
      right: 0.7in;
      font-size: 8pt;
      color: #9ca3af;
      display: flex;
      justify-content: space-between;
      border-top: 1px solid #e5e7eb;
      padding-top: 8px;
    }
    .content-footer a { color: ${colors.primary}; text-decoration: none; }

    /* ==================== SALES PAGE ==================== */
    .sales-page {
      width: 8.5in;
      height: 11in;
      background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
      padding: 0.6in;
      display: flex;
      flex-direction: column;
    }
    .sales-header {
      text-align: center;
      margin-bottom: 0.5in;
    }
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
    .sales-features {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 0.4in;
    }
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
    .sales-feature-title {
      font-size: 11pt;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 6px;
    }
    .sales-feature-desc {
      font-size: 9pt;
      color: #64748b;
      line-height: 1.4;
    }
    .sales-cta-box {
      background: linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%);
      border-radius: 16px;
      padding: 32px;
      text-align: center;
      margin-bottom: 0.3in;
    }
    .sales-cta-title {
      font-size: 18pt;
      font-weight: 700;
      color: white;
      margin-bottom: 8px;
    }
    .sales-cta-subtitle {
      font-size: 11pt;
      color: rgba(255,255,255,0.85);
      margin-bottom: 20px;
    }
    .sales-cta-button {
      display: inline-block;
      background: white;
      color: ${colors.primary};
      padding: 14px 32px;
      border-radius: 8px;
      font-size: 12pt;
      font-weight: 700;
      text-decoration: none;
    }
    .sales-cta-url {
      margin-top: 12px;
      font-size: 10pt;
      color: rgba(255,255,255,0.7);
    }
    .sales-resources {
      margin-bottom: 0.3in;
    }
    .sales-resources-title {
      font-size: 11pt;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 12px;
      text-align: center;
    }
    .sales-resources-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }
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
    .sales-footer-brand {
      display: flex;
      align-items: center;
      gap: 8px;
    }
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
  <!-- COVER PAGE -->
  <div class="cover-page">
    <div class="cover-brand">
      <div class="cover-brand-icon">${name.charAt(0)}</div>
      <div class="cover-brand-text">${escapeHtml(name)}</div>
    </div>
    <div class="cover-main">
      <div class="cover-category">${escapeHtml(categoryLabel)}</div>
      <h1 class="cover-title">${escapeHtml(title)}</h1>
      <p class="cover-description">${escapeHtml(description)}</p>
      <div class="cover-features">
        ${features.map(f => `<div class="cover-feature"><div class="cover-feature-icon">&#10003;</div><span>${escapeHtml(f)}</span></div>`).join('')}
      </div>
    </div>
    <div class="cover-footer">
      <div class="cover-url">${domain}</div>
      <div class="cover-version">${date}</div>
    </div>
  </div>

  <!-- CONTENT PAGE -->
  <div class="content-page">
    <div class="content-header">
      <h1 class="content-title">${escapeHtml(title)}</h1>
      <p class="content-subtitle">${escapeHtml(description)}</p>
    </div>
    <div class="content-body">
      ${contentHtml}
    </div>
  </div>

  <!-- SALES PAGE -->
  <div class="sales-page">
    <div class="sales-header">
      <div class="sales-pretitle">Take the Next Step</div>
      <h2 class="sales-title">${escapeHtml(cta.headline)}</h2>
      <p class="sales-subtitle">${escapeHtml(cta.subheadline)}</p>
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
      <div class="sales-cta-title">${escapeHtml(cta.buttonText)}</div>
      <div class="sales-cta-subtitle">Start your free trial today</div>
      <div class="sales-cta-button">${escapeHtml(cta.buttonText)}</div>
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
        <div class="sales-footer-text">© ${year} ${escapeHtml(name)}. All rights reserved.</div>
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

export async function generateLeadMagnetPDF(options: LeadMagnetOptions): Promise<GenerationResult> {
  const brand = getBrand(options.brand)
  const outputDir = options.outputDir || join(process.cwd(), 'frontend', 'public', 'lead-magnets')

  // Ensure output directory exists
  if (!existsSync(outputDir)) {
    await mkdir(outputDir, { recursive: true })
  }

  // Get content HTML
  const contentHtml = await getContent(options.content)

  // Generate full HTML
  const html = generateHTML(options, brand, contentHtml)

  // Launch Puppeteer and generate PDF
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  })

  const page = await browser.newPage()
  await page.setViewport({ width: 816, height: 1056, deviceScaleFactor: 2 })
  await page.setContent(html, { waitUntil: 'domcontentloaded' })

  const pdfPath = join(outputDir, `${options.slug}.pdf`)
  const pdfBuffer = await page.pdf({
    path: pdfPath,
    format: 'letter',
    printBackground: true,
  })

  await browser.close()

  return {
    pdfPath,
    pdfUrl: `/lead-magnets/${options.slug}.pdf`,
    fileSize: pdfBuffer.length,
    pageCount: 3,
  }
}
