# Documentation Website Structure

Guide for setting up and hosting LOKI Interceptor documentation online.

## Overview

This documentation structure is designed to be hosted on:
- **GitHub Pages** (Free, default option)
- **MkDocs** (Local or cloud-hosted)
- **Readthedocs** (rtd.io)
- **Custom static hosting** (AWS S3, CloudFlare, etc.)

---

## File Structure

```
docs/
├── INDEX.md                      # Main documentation index
├── WEBSITE_STRUCTURE.md          # This file
├── api/                          # API Documentation
│   ├── README.md                # API Reference
│   ├── examples.md              # Integration Examples
│   ├── authentication.md        # Auth & Security
│   ├── openapi.yaml            # OpenAPI/Swagger spec
│   └── postman.json            # Postman collection
├── guides/                       # User & Developer Guides
│   ├── installation.md          # Installation guide
│   ├── configuration.md         # Configuration guide
│   ├── user-manual.md          # User manual
│   ├── developer-guide.md       # Developer guide
│   ├── development-workflow.md  # Development workflow
│   ├── document-types.md        # Document types
│   ├── compliance-modules.md    # Compliance modules
│   ├── best-practices.md        # Best practices
│   ├── patterns.md              # Pattern registry
│   └── custom-patterns.md       # Custom patterns
├── deployment/                   # Deployment Documentation
│   ├── README.md                # Deployment guide
│   ├── docker.md                # Docker deployment
│   ├── cloud.md                 # Cloud deployment
│   ├── configuration.md         # Production config
│   ├── performance.md           # Performance tuning
│   ├── release-notes.md         # Release notes
│   └── upgrade.md               # Upgrade guide
├── architecture/                # Architecture Documentation
│   ├── README.md                # Architecture overview
│   ├── code-structure.md        # Code organization
│   ├── design.md                # System design
│   ├── compliance-rules.md      # Rules documentation
│   └── database.md              # Database schema
├── troubleshooting/             # Troubleshooting Guides
│   ├── README.md                # Troubleshooting guide
│   ├── faq.md                   # FAQ
│   ├── logging.md               # Logging & debugging
│   ├── performance.md           # Performance issues
│   └── common-errors.md         # Common errors
└── examples/                     # Code Examples
    ├── python/                  # Python examples
    ├── javascript/              # JavaScript examples
    ├── curl/                    # cURL examples
    └── postman/                 # Postman examples
```

---

## Documentation Organization

### 1. Homepage (INDEX.md)

**Purpose**: Main entry point for documentation

**Content**:
- Quick navigation
- Key features
- Quick start
- By use case navigation
- Important links

**Audience**: All users

### 2. Getting Started Section

**Files**:
- `guides/installation.md` - Installation
- `guides/configuration.md` - Configuration
- `README.md` (main) - Quick start

**Purpose**: Help new users get started

**Audience**: New users, beginners

### 3. User Documentation

**Files**:
- `guides/user-manual.md` - User manual
- `guides/document-types.md` - Document types
- `guides/compliance-modules.md` - Modules explained
- `guides/best-practices.md` - Best practices

**Purpose**: How to use LOKI

**Audience**: End users, business users

### 4. API Documentation

**Files**:
- `api/README.md` - API reference
- `api/examples.md` - Code examples
- `api/authentication.md` - Auth & security
- `api/openapi.yaml` - OpenAPI spec

**Purpose**: API integration

**Audience**: API developers, integrators

### 5. Deployment & Operations

**Files**:
- `deployment/README.md` - Deployment guide
- `deployment/docker.md` - Docker setup
- `deployment/cloud.md` - Cloud deployment
- `deployment/configuration.md` - Production config
- `deployment/performance.md` - Tuning

**Purpose**: Deploy and operate LOKI

**Audience**: DevOps, sysadmins, ops teams

### 6. Developer Documentation

**Files**:
- `guides/developer-guide.md` - Development guide
- `guides/development-workflow.md` - Workflow
- `guides/patterns.md` - Pattern registry
- `guides/custom-patterns.md` - Custom patterns
- `architecture/README.md` - Architecture
- `architecture/code-structure.md` - Code org
- `architecture/design.md` - System design
- `CONTRIBUTING.md` - Contributing guidelines

**Purpose**: Extend and contribute to LOKI

**Audience**: Developers, contributors

### 7. Troubleshooting & Support

**Files**:
- `troubleshooting/README.md` - Guide
- `troubleshooting/faq.md` - FAQ
- `troubleshooting/logging.md` - Logging
- `troubleshooting/performance.md` - Performance issues
- `troubleshooting/common-errors.md` - Common errors

**Purpose**: Resolve issues

**Audience**: All users

### 8. Reference Documentation

**Files**:
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contributing
- `architecture/compliance-rules.md` - Rules
- `deployment/release-notes.md` - Releases

**Purpose**: Reference information

**Audience**: All users

---

## Website Setup Options

### Option 1: GitHub Pages (Recommended)

**Advantages**: Free, integrated with GitHub, easy updates

**Setup**:

1. Create `mkdocs.yml`:

```yaml
site_name: LOKI Interceptor
site_description: Enterprise compliance validation system
site_url: https://yourdomain.com
repo_url: https://github.com/Johnobhoy88/loki-interceptor
repo_name: loki-interceptor

theme:
  name: material
  logo: assets/logo.png
  favicon: assets/favicon.ico
  features:
    - navigation.instant
    - navigation.tabs
    - search.suggest

nav:
  - Home: index.md
  - Getting Started:
    - Installation: guides/installation.md
    - Configuration: guides/configuration.md
    - Quick Start: README.md
  - User Guide:
    - Manual: guides/user-manual.md
    - Document Types: guides/document-types.md
    - Compliance Modules: guides/compliance-modules.md
  - API Documentation:
    - Reference: api/README.md
    - Examples: api/examples.md
    - Authentication: api/authentication.md
  - Deployment:
    - Guide: deployment/README.md
    - Docker: deployment/docker.md
    - Cloud: deployment/cloud.md
  - Architecture:
    - Overview: architecture/README.md
    - Code Structure: architecture/code-structure.md
  - Troubleshooting:
    - Guide: troubleshooting/README.md
    - FAQ: troubleshooting/faq.md
  - Contributing: ../CONTRIBUTING.md
  - Changelog: ../CHANGELOG.md

plugins:
  - search
  - minify

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - toc:
      permalink: true
```

2. Install MkDocs:

```bash
pip install mkdocs mkdocs-material
```

3. Build and deploy:

```bash
# Build
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Option 2: MkDocs (Self-hosted)

**Advantages**: Full control, can self-host

**Setup**:

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Create site structure (see mkdocs.yml above)

# Build
mkdocs build

# Run locally
mkdocs serve

# Deploy to server
# Upload 'site/' directory to web server
```

### Option 3: Readthedocs

**Advantages**: Built for documentation, free hosting

**Setup**:

1. Create `.readthedocs.yaml`:

```yaml
version: 2
build:
  os: ubuntu-20.04
  tools:
    python: "3.10"

python:
  install:
    - requirements: requirements.txt

mkdocs:
  configuration: mkdocs.yml
```

2. Connect GitHub repo to readthedocs.org
3. Documentation auto-builds on push

### Option 4: Static Hosting

**Advantages**: Maximum control, can use any service

**Setup**:

```bash
# Build with MkDocs
mkdocs build

# Deploy to AWS S3
aws s3 sync site/ s3://my-bucket/

# Or CloudFlare Pages
# Connect GitHub repo and set build command to 'mkdocs build'
```

---

## Navigation Structure

### Main Navigation Path

```
Home (INDEX.md)
  ├─ Quick Start
  ├─ Installation
  ├─ Getting Started
  └─ By Use Case
      ├─ Business Users
      ├─ API Developers
      ├─ System Admins
      └─ Contributors
```

### Site Map

```
/
├─ index.md (home)
├─ guides/
│  ├─ installation.md
│  ├─ user-manual.md
│  ├─ developer-guide.md
│  └─ ...
├─ api/
│  ├─ README.md
│  ├─ examples.md
│  └─ ...
├─ deployment/
│  ├─ README.md
│  ├─ docker.md
│  └─ ...
├─ architecture/
│  ├─ README.md
│  └─ ...
├─ troubleshooting/
│  ├─ README.md
│  ├─ faq.md
│  └─ ...
├─ CONTRIBUTING.md
└─ CHANGELOG.md
```

---

## Search & Discoverability

### Search Implementation

**MkDocs Material** includes built-in search with:
- Full-text search
- Keyboard shortcuts
- Search suggestions
- Results preview

### SEO Optimization

Add to `mkdocs.yml`:

```yaml
extra:
  canonical_url: https://yourdomain.com

markdown_extensions:
  - meta
```

Add to page frontmatter:

```markdown
---
title: Installation Guide
description: Complete installation guide for LOKI Interceptor
keywords: installation, setup, getting started
---
```

### Cross-linking

Use relative links:

```markdown
- See [API Examples](../api/examples.md)
- Review [User Manual](./user-manual.md)
- Check [Deployment Guide](../deployment/README.md)
```

---

## Content Management

### Documentation Updates

1. **Make changes** in markdown files
2. **Run locally**: `mkdocs serve`
3. **Test** in browser
4. **Commit** and push
5. **Automatic deploy** (GitHub Pages/RTD)

### Adding New Sections

1. **Create markdown file**
2. **Add to mkdocs.yml nav**
3. **Add links** in INDEX.md
4. **Test** locally
5. **Deploy**

### Versioning

For versioned documentation, use mike:

```bash
# Install mike
pip install mike

# Deploy version
mike deploy 1.0 latest

# List versions
mike list
```

---

## Styling & Customization

### Theme Customization

Create `docs/stylesheets/extra.css`:

```css
:root {
  --md-primary-fg-color: #0066cc;
  --md-accent-fg-color: #00cc00;
}

.md-footer__copyright {
  margin-left: 0;
}
```

Reference in `mkdocs.yml`:

```yaml
extra_css:
  - stylesheets/extra.css
```

### Custom Logo

Add logo to `docs/assets/`:

```yaml
theme:
  logo: assets/logo.png
  favicon: assets/favicon.ico
```

---

## Analytics & Monitoring

### Google Analytics

Add to `mkdocs.yml`:

```yaml
extra:
  analytics:
    provider: google
    property: GA_MEASUREMENT_ID
```

### Traffic Monitoring

Use built-in server logs or third-party services:
- Google Analytics
- CloudFlare Analytics
- Plausible Analytics

---

## Documentation Maintenance Checklist

### Monthly
- [ ] Update examples
- [ ] Fix broken links
- [ ] Update statistics
- [ ] Review user feedback

### Quarterly
- [ ] Update screenshots
- [ ] Review architecture docs
- [ ] Update deployment guides
- [ ] Add new features docs

### Annually
- [ ] Full documentation review
- [ ] Update best practices
- [ ] Add API examples
- [ ] Reorganize if needed

---

## Access Control

### Public Documentation

Default for open-source projects:
- All docs publicly accessible
- GitHub source visible
- Community contributions welcome

### Private Documentation

For enterprise deployments:

```yaml
# .gitignore
private/

# mkdocs.yml - only build public
docs_dir: docs/public
```

---

## Performance Optimization

### Build Performance

```bash
# Build without plugins
mkdocs build --strict

# Check build time
mkdocs build --dirty

# Minify CSS/JS
pip install mkdocs-minify-plugin
```

### Hosting Performance

- Use CDN for static files
- Enable gzip compression
- Cache headers on web server
- Image optimization

---

## Common Deployment Targets

### GitHub Pages (Recommended)

```bash
mkdocs gh-deploy
```

**URL**: `https://yourusername.github.io/loki-interceptor`

### Netlify

1. Connect GitHub repo
2. Set build command: `mkdocs build`
3. Set publish dir: `site`

**URL**: `https://loki.netlify.app`

### Vercel

1. Connect GitHub repo
2. Set build command: `mkdocs build`
3. Set output: `site`

**URL**: `https://loki.vercel.app`

### Custom Domain

For GitHub Pages with custom domain:

1. Add `CNAME` file to `docs/`:

```
yourdomain.com
```

2. Configure DNS to point to GitHub Pages
3. Enable custom domain in repo settings

---

## Troubleshooting Website

### Build Errors

```bash
# Debug build
mkdocs build --verbose

# Check dependencies
pip list | grep mkdocs

# Rebuild from scratch
rm -rf site/
mkdocs build
```

### Navigation Issues

Check `mkdocs.yml` indentation and syntax:

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"
```

### Deployment Issues

1. Check branch: docs deploys from `main` by default
2. Verify build command in CI/CD
3. Check GitHub Actions logs

---

**See also**: [Documentation Index](INDEX.md) | [Installation Guide](guides/installation.md)

**Version**: 1.0.0
**Last Updated**: 2025-11-11
