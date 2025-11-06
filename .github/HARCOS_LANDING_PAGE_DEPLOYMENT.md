---
title: "HARCOS Landing Page Deployment Guide"
description: "Instructions for deploying the HARCOS landing page on GitHub Pages"
type: "guide"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "HARCOS Team"
---

# HARCOS Landing Page Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the HARCOS landing page on GitHub Pages.

## Files Created

- **`HARCOS_LANDING_PAGE.html`** - Complete interactive landing page with:
  - Deep Blue (#003DA5) + Warm Orange (#FF6B35) branding
  - Hero section with call-to-action buttons
  - Projects showcase (CDE-Orchestrator-MCP, Agent-Framework, LLM-Eval-Toolkit)
  - Benefits grid (open source, community-driven, production-ready)
  - Enterprise services section ($2,000+/month)
  - Support tiers ($5/mo - $100+/mo)
  - Responsive design (mobile-friendly)

## Deployment Options

### Option 1: GitHub Pages (Recommended for Organization)

**Step 1**: Create `docs/index.html` in HARCOS/docs repository

```bash
# Navigate to HARCOS/docs repository (after creation)
cd /path/to/HARCOS/docs

# Copy landing page
cp ../CDE-Orchestrator-MCP/.github/HARCOS_LANDING_PAGE.html index.html

# Or create from scratch
# (Copy contents of HARCOS_LANDING_PAGE.html into docs/index.html)
```

**Step 2**: Enable GitHub Pages

1. Go to **HARCOS/docs** repository
2. Settings → Pages
3. Source: Deploy from branch
4. Branch: `main`, folder: `/root` or `/docs`
5. Save

**Step 3**: Configure custom domain (Optional)

```bash
# Create CNAME file in docs/
echo "harcos.ai" > docs/CNAME

# Commit and push
git add docs/CNAME
git commit -m "Configure custom domain harcos.ai"
git push
```

**Step 4**: Verify deployment

- Default: https://harcos-ai.github.io/docs
- With CNAME: https://harcos.ai (after DNS configuration)

### Option 2: Vercel or Netlify (Alternative)

**Vercel**:
1. Connect HARCOS/docs repository to Vercel
2. Set Build Command: (leave empty - static HTML)
3. Set Output Directory: `/`
4. Deploy

**Netlify**:
1. Connect HARCOS/docs repository to Netlify
2. Build & Deploy Settings:
   - Build command: (leave empty)
   - Publish directory: `/`
3. Deploy

### Option 3: Self-Hosted

```bash
# Copy file to web server
scp HARCOS_LANDING_PAGE.html user@harcos.ai:/var/www/html/index.html

# Or in a Docker container
# FROM nginx:latest
# COPY HARCOS_LANDING_PAGE.html /usr/share/nginx/html/index.html
```

## Landing Page Features

### Sections

1. **Header Navigation**
   - Logo: `◇ HARCOS`
   - Links: Projects, Why HARCOS, Enterprise, Support, GitHub
   - CTA: Sponsor button

2. **Hero Section**
   - Title: "HARCOS - Human-AI Research Community Open Source"
   - Tagline: "Open tools for symbiotic intelligence"
   - Buttons: Get Started (CDE-Orchestrator-MCP repo), Explore Projects

3. **Projects Grid**
   - CDE Orchestrator MCP (Active) - 309/312 tests, 97% coverage
   - Agent Framework (Coming Soon)
   - LLM Eval Toolkit (Coming Soon)

4. **Why HARCOS? Benefits**
   - 100% Open Source
   - Community-Driven
   - Production-Ready
   - Research-Focused
   - Ethical Monetization (Fair Source)
   - Comprehensive Documentation

5. **Enterprise Services**
   - Starting at $2,000/month
   - Managed cloud hosting
   - 24×7 support with SLA
   - Dedicated infrastructure & RAG services
   - Contact: enterprise@harcos.ai

6. **Support Tiers**
   - Supporter: $5+/mo
   - Contributor: $25+/mo
   - Partner: $50+/mo
   - Sponsor: $100+/mo
   - Links to: GitHub Sponsors, Open Collective

7. **Footer**
   - Copyright: © 2025 HARCOS Contributors
   - License: Fair Source License 1.0
   - Links: GitHub, Sponsor, Contact, License

## Customization

### Update Organization Links

Replace in the HTML:
```html
<!-- Current -->
<a href="https://github.com/HARCOS-AI/CDE-Orchestrator-MCP">...</a>

<!-- After HARCOS-AI organization creation, update to actual URL if different -->
```

### Update Branding Colors

```css
/* In <style> section */
:root {
    --deep-blue: #003DA5;        /* Primary color */
    --warm-orange: #FF6B35;      /* Accent color */
    --neutral-gray: #4A4A4A;     /* Text color */
    --light-gray: #F5F5F5;       /* Background */
}
```

### Update Contact Email

```html
<!-- Replace enterprise@harcos.ai with actual email -->
<a href="mailto:enterprise@harcos.ai">Get a Quote</a>
```

### Update Open Collective Link

```html
<!-- Replace with actual Open Collective username/URL -->
<a href="https://opencollective.com/harcos-ai">Open Collective</a>
```

## Performance Optimization

### Current Performance

- **Size**: ~15 KB (uncompressed)
- **Load time**: <100ms (on modern connections)
- **No external dependencies** (fully self-contained)
- **No JavaScript required** (pure CSS + HTML)
- **Responsive**: Works on mobile, tablet, desktop

### Optimization Tips

1. **Enable Gzip compression** on web server
2. **Set cache headers** for static content
3. **Use CDN** for global distribution (Cloudflare, etc.)
4. **Consider Lighthouse** optimization for Core Web Vitals

## Integration with HARCOS Organization

### After Organization Creation

1. **Transfer CDE-Orchestrator-MCP** to HARCOS-AI organization
2. **Create HARCOS/docs** repository
3. **Copy landing page** to docs/index.html
4. **Enable GitHub Pages** on HARCOS/docs
5. **Update all project READMEs** to link to https://harcos.ai or https://harcos-ai.github.io

### GitHub Actions CI/CD (Optional)

```yaml
# .github/workflows/deploy-landing-page.yml
name: Deploy Landing Page

on:
  push:
    branches: [main]
    paths: ['docs/index.html']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## Testing

### Local Testing

```bash
# Option 1: Python SimpleHTTPServer
cd .github
python -m http.server 8000
# Open: http://localhost:8000/HARCOS_LANDING_PAGE.html

# Option 2: Node.js http-server
npm install -g http-server
cd .github
http-server
# Open: http://localhost:8080/HARCOS_LANDING_PAGE.html

# Option 3: Live Server (VS Code Extension)
# Right-click on HARCOS_LANDING_PAGE.html → Open with Live Server
```

### Responsive Testing

1. **Desktop**: 1920x1080, 1366x768, 1024x768
2. **Tablet**: iPad (768x1024), iPad Pro (1024x1366)
3. **Mobile**: iPhone 12 (390x844), Android (375x667)

Tools:
- Chrome DevTools (F12 → Device Emulation)
- Responsive Design Mode (Ctrl+Shift+M)
- BrowserStack (cloud testing)

### SEO Testing

```bash
# Install lighthouse
npm install -g lighthouse

# Run audit
lighthouse https://harcos.ai --view

# Check Core Web Vitals
# Performance: >90
# Accessibility: >90
# Best Practices: >90
# SEO: >90
```

## Monitoring

### Google Analytics (Optional)

Add to `<head>` section:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
```

### Uptime Monitoring

Use services like:
- UptimeRobot
- Pingdom
- Statuspage.io

## Maintenance

### Regular Updates

- **Monthly**: Update project status (Active/Coming Soon)
- **Quarterly**: Review branding consistency
- **Annually**: Full accessibility audit

### Version Control

```bash
# Track changes to landing page
git log --oneline .github/HARCOS_LANDING_PAGE.html

# Compare versions
git diff v1.0..v1.1 .github/HARCOS_LANDING_PAGE.html
```

## Troubleshooting

### GitHub Pages Not Publishing

**Issue**: Changes not visible after push

**Solution**:
1. Check: Settings → Pages → Source is correct
2. Check: Branch is `main` (or configured branch)
3. Check: File path is `docs/index.html` or `index.html`
4. Wait: GitHub Pages can take 1-5 minutes to deploy
5. Clear cache: Ctrl+Shift+Delete in browser

### Custom Domain Not Working

**Issue**: harcos.ai shows 404

**Solution**:
1. Check: CNAME file exists in repository root
2. Check: DNS records point to GitHub Pages:
   - Type A: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
   - Or Type CNAME: `<org>.github.io`
3. Wait: DNS propagation can take 24-48 hours

### Styling Not Loading

**Issue**: Landing page shows without colors/formatting

**Solution**:
- All CSS is inline (no external files needed)
- Check browser console (F12) for errors
- Verify HTML file encoding is UTF-8

## Next Steps

1. **Create HARCOS organization** (Phase 1 of HARCOS_ORGANIZATION_SETUP.md)
2. **Deploy landing page** using Option 1 (GitHub Pages)
3. **Configure custom domain** (harcos.ai)
4. **Add Google Analytics** for traffic tracking
5. **Monitor uptime** and performance metrics
6. **Link from all projects** to landing page

## References

- GitHub Pages: https://pages.github.com/
- Vercel: https://vercel.com/
- Netlify: https://netlify.com/
- Custom domains: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site
- SEO Best Practices: https://developers.google.com/search

---

**Created**: 2025-11-05
**Updated**: 2025-11-05
**Status**: Active
**Owner**: HARCOS Team
