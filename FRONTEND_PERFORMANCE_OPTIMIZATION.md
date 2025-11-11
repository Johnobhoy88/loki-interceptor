# Frontend Performance Optimization Guide

## LOKI Interceptor Frontend Performance Best Practices

Comprehensive guide for maintaining high performance standards in the frontend application.

---

## Table of Contents

1. [Performance Goals](#performance-goals)
2. [Core Web Vitals](#core-web-vitals)
3. [Optimization Strategies](#optimization-strategies)
4. [Monitoring](#monitoring)
5. [Common Issues](#common-issues)
6. [Checklist](#checklist)

---

## Performance Goals

### Target Metrics

| Metric | Target | Critical |
|--------|--------|----------|
| **First Contentful Paint (FCP)** | < 2.0s | < 1.8s |
| **Largest Contentful Paint (LCP)** | < 2.5s | < 2.0s |
| **Time to Interactive (TTI)** | < 3.5s | < 3.0s |
| **Total Blocking Time (TBT)** | < 300ms | < 200ms |
| **Cumulative Layout Shift (CLS)** | < 0.1 | < 0.05 |
| **Speed Index** | < 3.0s | < 2.5s |

### Resource Budgets

| Resource | Budget | Current |
|----------|--------|---------|
| JavaScript | 250 KB | ~90 KB ✓ |
| CSS | 100 KB | ~24 KB ✓ |
| HTML | 50 KB | ~9 KB ✓ |
| Total Page | 500 KB | ~123 KB ✓ |

### Lighthouse Scores

| Category | Target |
|----------|--------|
| Performance | 90+ |
| Accessibility | 95+ |
| Best Practices | 90+ |
| SEO | 90+ |

---

## Core Web Vitals

### 1. Largest Contentful Paint (LCP)

**What**: Time to render largest content element
**Target**: < 2.5s

#### Optimization Strategies

**Reduce Server Response Time**
```javascript
// Use CDN for static assets
// Enable HTTP/2
// Implement server-side caching
```

**Optimize Images**
```html
<!-- Use modern formats -->
<img src="logo.webp" alt="Logo" loading="lazy" />

<!-- Specify dimensions to prevent layout shift -->
<img src="hero.jpg" width="1200" height="600" alt="Hero" />
```

**Preload Critical Resources**
```html
<link rel="preload" href="app.js" as="script" />
<link rel="preload" href="style.css" as="style" />
<link rel="preconnect" href="https://api.example.com" />
```

**Remove Render-Blocking Resources**
```html
<!-- Defer non-critical JavaScript -->
<script src="analytics.js" defer></script>

<!-- Inline critical CSS -->
<style>
  /* Critical styles here */
</style>
<link rel="stylesheet" href="style.css" media="print" onload="this.media='all'" />
```

### 2. First Input Delay (FID)

**What**: Time from user interaction to browser response
**Target**: < 100ms

#### Optimization Strategies

**Break Up Long Tasks**
```javascript
// Bad: Long blocking task
function processLargeDataset(data) {
  data.forEach(item => heavyOperation(item));
}

// Good: Use requestIdleCallback
function processLargeDataset(data) {
  const chunk = 50;
  let index = 0;

  function processChunk() {
    const end = Math.min(index + chunk, data.length);
    for (let i = index; i < end; i++) {
      heavyOperation(data[i]);
    }
    index = end;

    if (index < data.length) {
      requestIdleCallback(processChunk);
    }
  }

  requestIdleCallback(processChunk);
}
```

**Use Web Workers for Heavy Computation**
```javascript
// worker.js
self.addEventListener('message', (e) => {
  const result = heavyComputation(e.data);
  self.postMessage(result);
});

// main.js
const worker = new Worker('worker.js');
worker.postMessage(data);
worker.addEventListener('message', (e) => {
  console.log('Result:', e.data);
});
```

**Debounce User Input**
```javascript
function debounce(fn, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
}

// Usage
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', debounce(handleSearch, 300));
```

### 3. Cumulative Layout Shift (CLS)

**What**: Visual stability - avoid unexpected layout shifts
**Target**: < 0.1

#### Optimization Strategies

**Always Specify Image Dimensions**
```html
<!-- Bad: No dimensions -->
<img src="photo.jpg" alt="Photo" />

<!-- Good: Explicit dimensions -->
<img src="photo.jpg" width="800" height="600" alt="Photo" />
```

**Reserve Space for Dynamic Content**
```css
.placeholder {
  min-height: 400px; /* Reserve space before content loads */
  background: #f0f0f0;
}
```

**Avoid Inserting Content Above Existing Content**
```javascript
// Bad: Prepends content, shifting everything down
container.insertBefore(newElement, container.firstChild);

// Good: Append to bottom or use fixed positioning
container.appendChild(newElement);
```

**Use CSS Transforms for Animations**
```css
/* Bad: Causes layout shift */
.element {
  transition: margin-left 0.3s;
}

/* Good: GPU-accelerated, no layout shift */
.element {
  transition: transform 0.3s;
  transform: translateX(0);
}
.element.moved {
  transform: translateX(100px);
}
```

---

## Optimization Strategies

### JavaScript Performance

#### 1. Minimize Bundle Size

**Code Splitting**
```javascript
// Dynamic imports
async function loadModule() {
  const module = await import('./heavy-module.js');
  module.init();
}
```

**Tree Shaking**
```javascript
// Use ES6 modules for better tree shaking
import { specificFunction } from './utils.js';

// Avoid namespace imports
// import * as utils from './utils.js'; // Bad
```

**Remove Console Logs in Production**
```javascript
// Use build-time removal
if (process.env.NODE_ENV !== 'production') {
  console.log('Debug info');
}
```

#### 2. Optimize Execution

**Avoid Unnecessary Recalculations**
```javascript
// Bad: Recalculates on every loop iteration
for (let i = 0; i < array.length; i++) {
  // ...
}

// Good: Cache length
const len = array.length;
for (let i = 0; i < len; i++) {
  // ...
}
```

**Use Event Delegation**
```javascript
// Bad: Multiple listeners
items.forEach(item => {
  item.addEventListener('click', handleClick);
});

// Good: Single listener on parent
container.addEventListener('click', (e) => {
  if (e.target.matches('.item')) {
    handleClick(e);
  }
});
```

**Batch DOM Updates**
```javascript
// Bad: Multiple reflows
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  div.textContent = `Item ${i}`;
  container.appendChild(div); // Reflow on each append
}

// Good: Single reflow
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  div.textContent = `Item ${i}`;
  fragment.appendChild(div);
}
container.appendChild(fragment); // Single reflow
```

### CSS Performance

#### 1. Minimize Reflows and Repaints

**Read Then Write**
```javascript
// Bad: Interleaved reads and writes
const width = element.offsetWidth; // Read
element.style.width = width + 10 + 'px'; // Write
const height = element.offsetHeight; // Read (causes reflow)
element.style.height = height + 10 + 'px'; // Write

// Good: Batch reads, then batch writes
const width = element.offsetWidth;
const height = element.offsetHeight;
element.style.width = width + 10 + 'px';
element.style.height = height + 10 + 'px';
```

**Use CSS Classes Instead of Inline Styles**
```javascript
// Bad: Multiple style changes
element.style.width = '100px';
element.style.height = '100px';
element.style.backgroundColor = 'red';

// Good: Single class change
element.classList.add('sized-box');
```

#### 2. Optimize Selectors

```css
/* Bad: Overly specific */
html body div.container ul li.item a.link {
  color: blue;
}

/* Good: Simple and specific */
.item-link {
  color: blue;
}
```

#### 3. Use CSS Containment

```css
.widget {
  /* Isolate layout calculations */
  contain: layout style paint;
}
```

### Network Performance

#### 1. Reduce HTTP Requests

**Combine Files**
```html
<!-- Bad: Multiple requests -->
<script src="utils.js"></script>
<script src="helpers.js"></script>
<script src="main.js"></script>

<!-- Good: Single bundle -->
<script src="app.bundle.js"></script>
```

**Use CSS Sprites for Icons**
```css
.icon {
  background-image: url('sprites.png');
  width: 32px;
  height: 32px;
}
.icon-home { background-position: 0 0; }
.icon-search { background-position: -32px 0; }
```

#### 2. Enable Compression

**Nginx Configuration**
```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

#### 3. Use Caching

**HTTP Headers**
```nginx
# Cache static assets
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

**Service Worker Caching**
```javascript
// service-worker.js
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

#### 4. Lazy Load Resources

**Images**
```html
<img src="placeholder.jpg" data-src="actual.jpg" loading="lazy" />
```

**JavaScript**
```javascript
// Load on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadHeavyFeature();
      observer.unobserve(entry.target);
    }
  });
});

observer.observe(document.querySelector('.feature-section'));
```

### Memory Management

#### 1. Avoid Memory Leaks

**Remove Event Listeners**
```javascript
// Bad: Never removed
element.addEventListener('click', handler);

// Good: Clean up
const controller = new AbortController();
element.addEventListener('click', handler, { signal: controller.signal });
// Later...
controller.abort(); // Removes listener
```

**Clear Intervals and Timeouts**
```javascript
const intervalId = setInterval(() => {
  // Do something
}, 1000);

// Clean up when done
clearInterval(intervalId);
```

**Avoid Global Variables**
```javascript
// Bad: Global scope pollution
var data = loadLargeDataset();

// Good: Scoped
(function() {
  const data = loadLargeDataset();
  // Use data...
})();
```

#### 2. Optimize Data Structures

**Use Maps for Large Datasets**
```javascript
// Faster lookups than objects for large datasets
const cache = new Map();
cache.set('key', 'value');
const value = cache.get('key');
```

**Use Sets for Unique Values**
```javascript
const uniqueIds = new Set();
uniqueIds.add(id);
if (uniqueIds.has(id)) {
  // Already exists
}
```

---

## Monitoring

### 1. Lighthouse CI

**Run Locally**
```bash
npm run test:performance
```

**View Reports**
```bash
# Open .lighthouseci/report.html
```

### 2. Real User Monitoring (RUM)

**Measure Core Web Vitals**
```javascript
// First Contentful Paint
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const fcp = entries[0];
  console.log('FCP:', fcp.startTime);
}).observe({ entryTypes: ['paint'] });

// Largest Contentful Paint
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lcp = entries[entries.length - 1];
  console.log('LCP:', lcp.renderTime || lcp.loadTime);
}).observe({ entryTypes: ['largest-contentful-paint'] });

// Cumulative Layout Shift
let clsScore = 0;
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) {
      clsScore += entry.value;
    }
  }
  console.log('CLS:', clsScore);
}).observe({ entryTypes: ['layout-shift'] });
```

### 3. Performance API

**Navigation Timing**
```javascript
const perfData = window.performance.timing;
const loadTime = perfData.loadEventEnd - perfData.navigationStart;
const domReady = perfData.domContentLoadedEventEnd - perfData.navigationStart;
const ttfb = perfData.responseStart - perfData.navigationStart;

console.log({
  loadTime,
  domReady,
  ttfb
});
```

**Resource Timing**
```javascript
const resources = performance.getEntriesByType('resource');
resources.forEach(resource => {
  console.log(resource.name, resource.duration);
});
```

### 4. Bundle Size Monitoring

```bash
# Generate bundle report
npm run analyze:bundle

# View at frontend/reports/bundle-analysis.html
```

---

## Common Issues

### Issue: Slow Initial Load

**Symptoms**: FCP > 3s, LCP > 4s

**Solutions**:
1. Enable text compression (gzip/brotli)
2. Minify CSS and JavaScript
3. Reduce bundle size
4. Use CDN for static assets
5. Implement HTTP/2 Server Push

### Issue: Janky Scrolling

**Symptoms**: Choppy scroll, frame drops

**Solutions**:
1. Use `will-change` for animated elements
2. Avoid layout-triggering properties in animations
3. Use CSS transforms instead of position changes
4. Implement virtualization for long lists
5. Reduce expensive paint operations

### Issue: High Memory Usage

**Symptoms**: Browser slowdown, crashes

**Solutions**:
1. Remove unused event listeners
2. Clear intervals/timeouts
3. Limit cache size
4. Implement pagination
5. Use WeakMap for object references

### Issue: Slow JavaScript Execution

**Symptoms**: TBT > 500ms, FID > 200ms

**Solutions**:
1. Break up long tasks
2. Use Web Workers
3. Defer non-critical scripts
4. Optimize algorithms
5. Reduce DOM manipulation

---

## Checklist

### Development Phase

- [ ] Minimize bundle size (< 250KB JS)
- [ ] Optimize images (WebP, lazy loading)
- [ ] Implement code splitting
- [ ] Use efficient algorithms
- [ ] Batch DOM updates
- [ ] Add performance budgets
- [ ] Profile with DevTools

### Pre-Deployment

- [ ] Run Lighthouse audit (90+ score)
- [ ] Check bundle size report
- [ ] Verify Core Web Vitals
- [ ] Test on slow 3G connection
- [ ] Test on low-end devices
- [ ] Review network waterfall
- [ ] Check accessibility (95+ score)

### Production Monitoring

- [ ] Monitor Core Web Vitals
- [ ] Track bundle size changes
- [ ] Monitor error rates
- [ ] Review RUM data
- [ ] Check CDN hit rates
- [ ] Monitor API response times
- [ ] Track user engagement metrics

---

## Performance Testing Commands

```bash
# Run all performance tests
npm run test:performance

# Local Lighthouse audit
npm run analyze:lighthouse

# Bundle size analysis
npm run analyze:bundle

# Serve and test locally
npm run serve
# Then run Lighthouse in Chrome DevTools
```

---

## Resources

### Tools

- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)

### Documentation

- [Web Vitals](https://web.dev/vitals/)
- [Performance Best Practices](https://web.dev/fast/)
- [MDN Performance](https://developer.mozilla.org/en-US/docs/Web/Performance)

### Benchmarks

- [HTTP Archive](https://httparchive.org/)
- [Chrome UX Report](https://developers.google.com/web/tools/chrome-user-experience-report)

---

## Summary

### Key Takeaways

1. **Measure First**: Use Lighthouse and RUM to identify issues
2. **Optimize Critical Path**: Focus on FCP and LCP
3. **Reduce JavaScript**: Code split and defer non-critical scripts
4. **Optimize Images**: Use modern formats and lazy loading
5. **Monitor Continuously**: Track metrics in CI/CD and production

### Quick Wins

- Enable compression (instant 60-80% reduction)
- Add `loading="lazy"` to images
- Defer non-critical JavaScript
- Use CDN for static assets
- Implement browser caching

### Long-term Improvements

- Implement code splitting
- Add service worker
- Optimize critical rendering path
- Use Web Workers for heavy tasks
- Implement virtual scrolling

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Maintained by**: LOKI Performance Team
