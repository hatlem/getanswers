import { Helmet } from 'react-helmet-async';

interface SEOProps {
  title: string;
  description: string;
  canonical?: string;
  type?: 'website' | 'article' | 'product';
  image?: string;
  imageAlt?: string;
  noindex?: boolean;
  keywords?: string[];
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
  jsonLd?: object | object[];
}

const SITE_NAME = 'GetAnswers';
const SITE_URL = 'https://getanswers.co';
const DEFAULT_IMAGE = `${SITE_URL}/og-image.png`;
const DEFAULT_IMAGE_ALT = 'GetAnswers - AI-Powered Email Automation';
const TWITTER_HANDLE = '@getanswers';

export function SEO({
  title,
  description,
  canonical,
  type = 'website',
  image = DEFAULT_IMAGE,
  imageAlt = DEFAULT_IMAGE_ALT,
  noindex = false,
  keywords = [],
  author,
  publishedTime,
  modifiedTime,
  jsonLd,
}: SEOProps) {
  const fullTitle = title === SITE_NAME ? title : `${title} | ${SITE_NAME}`;
  const canonicalUrl = canonical ? `${SITE_URL}${canonical}` : undefined;

  // Default Organization schema
  const organizationSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SITE_NAME,
    url: SITE_URL,
    logo: `${SITE_URL}/icon.svg`,
    sameAs: [
      'https://twitter.com/getanswers',
      'https://linkedin.com/company/getanswers',
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'customer service',
      email: 'support@getanswers.co',
    },
  };

  // Default WebSite schema for search engines
  const websiteSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: SITE_NAME,
    url: SITE_URL,
    description: 'AI-powered email automation that handles your inbox automatically',
    potentialAction: {
      '@type': 'SearchAction',
      target: `${SITE_URL}/search?q={search_term_string}`,
      'query-input': 'required name=search_term_string',
    },
  };

  // Combine all JSON-LD schemas
  const allSchemas = [
    organizationSchema,
    websiteSchema,
    ...(Array.isArray(jsonLd) ? jsonLd : jsonLd ? [jsonLd] : []),
  ];

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      {keywords.length > 0 && <meta name="keywords" content={keywords.join(', ')} />}
      {author && <meta name="author" content={author} />}

      {/* Robots */}
      {noindex ? (
        <meta name="robots" content="noindex, nofollow" />
      ) : (
        <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
      )}

      {/* Canonical */}
      {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:image:alt" content={imageAlt} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      {canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
      <meta property="og:locale" content="en_US" />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:site" content={TWITTER_HANDLE} />
      <meta name="twitter:creator" content={TWITTER_HANDLE} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
      <meta name="twitter:image:alt" content={imageAlt} />

      {/* Article specific */}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}

      {/* JSON-LD Structured Data */}
      <script type="application/ld+json">
        {JSON.stringify(allSchemas)}
      </script>
    </Helmet>
  );
}

// Pre-configured SEO components for common page types
export function HomeSEO() {
  const productSchema = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'GetAnswers',
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    description: 'AI-powered email automation platform that triages, categorizes, and handles your emails automatically. Save 2+ hours daily.',
    offers: {
      '@type': 'AggregateOffer',
      priceCurrency: 'USD',
      lowPrice: '29',
      highPrice: '79',
      offerCount: '3',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      ratingCount: '1250',
    },
    featureList: [
      'AI-Powered Email Triage',
      'Smart Categorization',
      'Automatic Responses',
      'Policy-Based Automation',
      'Gmail Integration',
      'Outlook Integration',
      'Real-time Dashboard',
    ],
  };

  return (
    <SEO
      title="AI Email Automation - Inbox on Autopilot"
      description="GetAnswers uses AI to triage, categorize, and handle your emails automatically. Save 2+ hours daily. Only see what truly needs your attention. Free 14-day trial."
      canonical="/"
      keywords={[
        'email automation',
        'AI email',
        'inbox management',
        'email productivity',
        'email triage',
        'automatic email responses',
        'email assistant',
        'inbox zero',
        'email AI',
        'smart inbox',
      ]}
      jsonLd={productSchema}
    />
  );
}

// SEO for comparison pages
interface ComparisonSEOProps {
  competitor: string;
  competitorDescription: string;
  slug: string;
}

export function ComparisonSEO({ competitor, competitorDescription, slug }: ComparisonSEOProps) {
  const comparisonSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: `GetAnswers vs ${competitor}`,
    description: `Compare GetAnswers with ${competitor}. ${competitorDescription}`,
    mainEntity: {
      '@type': 'ItemList',
      itemListElement: [
        {
          '@type': 'SoftwareApplication',
          name: 'GetAnswers',
          position: 1,
        },
        {
          '@type': 'SoftwareApplication',
          name: competitor,
          position: 2,
        },
      ],
    },
  };

  return (
    <SEO
      title={`GetAnswers vs ${competitor} - Email Automation Comparison`}
      description={`Compare GetAnswers vs ${competitor} for email automation. See features, pricing, and why teams choose GetAnswers for AI-powered inbox management. ${competitorDescription}`}
      canonical={`/compare/${slug}`}
      keywords={[
        `${competitor} alternative`,
        `${competitor} vs GetAnswers`,
        'email automation comparison',
        'inbox management tools',
        `best ${competitor} alternative`,
        'AI email comparison',
      ]}
      jsonLd={comparisonSchema}
    />
  );
}

// SEO for lead magnet pages
interface LeadMagnetSEOProps {
  title: string;
  description: string;
  slug: string;
  keywords?: string[];
}

export function LeadMagnetSEO({ title, description, slug, keywords = [] }: LeadMagnetSEOProps) {
  const downloadableSchema = {
    '@context': 'https://schema.org',
    '@type': 'DigitalDocument',
    name: title,
    description: description,
    provider: {
      '@type': 'Organization',
      name: 'GetAnswers',
    },
    isAccessibleForFree: true,
  };

  return (
    <SEO
      title={title}
      description={description}
      canonical={`/lead-magnets/${slug}`}
      keywords={[
        'email productivity',
        'inbox management',
        'email templates',
        'free download',
        ...keywords,
      ]}
      jsonLd={downloadableSchema}
    />
  );
}

// SEO for free tools
export function FreeToolsSEO() {
  const toolsSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'GetAnswers Free Email Tools',
    description: 'Free email productivity tools including email triage calculators, response templates, and inbox management resources.',
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
  };

  return (
    <SEO
      title="Free Email Productivity Tools & Resources"
      description="Free email productivity tools from GetAnswers. Calculate time savings, get email templates, and learn inbox management strategies. No signup required."
      canonical="/free-tools"
      keywords={[
        'free email tools',
        'email productivity calculator',
        'inbox management resources',
        'email templates free',
        'email time calculator',
      ]}
      jsonLd={toolsSchema}
    />
  );
}
