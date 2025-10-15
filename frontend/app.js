// Auto-detect API base: if accessed remotely (not localhost), use same origin
// EXPERIMENTAL V2 - PORT 5002
const REMOTE_API_BASE = 'https://loki-interceptor.vercel.app/api';

const API_BASE = (window.location.protocol === 'file:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:5002'  // Local development or Electron app - EXPERIMENTAL PORT
  : REMOTE_API_BASE;  // Remote access - use the hosted API base

const state = {
  provider: 'anthropic',
  apiKeys: {},
  modules: [],
  stats: { validated: 0, warnings: 0, blocked: 0 },
  analyticsWindow: 30,
  analytics: { loading: false, overview: null, trends: null, modules: null, error: null },
  lastValidation: { text: null, result: null }  // Store for correction feature
};

// Toggle experimental auto-correction feature
const ENABLE_CORRECTIONS = false;
let lastHandshakeAt = 0;
const HANDSHAKE_TTL_MS = 60_000;

// Professional Toast Notification System
function showToast(message, type = 'info', title = null) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;

  const icons = {
    error: '!',
    success: '✓',
    warning: '!',
    info: 'i'
  };

  const titles = {
    error: title || 'Error',
    success: title || 'Success',
    warning: title || 'Warning',
    info: title || 'Information'
  };

  toast.innerHTML = `
    <div class="toast__icon">${icons[type] || 'i'}</div>
    <div class="toast__body">
      <div class="toast__title">${titles[type]}</div>
      <div class="toast__message">${escapeHtml(message)}</div>
    </div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 200);
  }, 4000);
}

const storage = {
  get(key, fallback = []) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return fallback;
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : fallback;
    } catch {
      return fallback;
    }
  },
  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }
};

async function init() {
  bindNavigation();
  bindActions();
  await hydrateBackendStatus();
  await hydrateApiKeys();
  await loadModuleCatalog();
  renderModuleChips('modules-interceptor', 'mods-interceptor');
  renderModuleChips('modules-validator', 'mods-validator');
  renderOverviewModules();
  document.querySelectorAll('.qa[data-nav]').forEach(btn => {
    btn.addEventListener('click', () => switchView(btn.dataset.nav));
  });
}

function bindNavigation() {
  document.querySelectorAll('.nav__item').forEach(btn => {
    btn.addEventListener('click', () => switchView(btn.dataset.view));
  });
}

function bindActions() {
  document.getElementById('refresh-status')?.addEventListener('click', hydrateBackendStatus);
  document.getElementById('save-key-btn')?.addEventListener('click', saveApiKey);
  document.getElementById('provider-select')?.addEventListener('change', onProviderChange);
  document.getElementById('test-btn')?.addEventListener('click', handlePromptValidation);
  document.getElementById('validate-btn')?.addEventListener('click', handleDocumentValidation);
  document.getElementById('analytics-window')?.addEventListener('change', evt => {
    state.analyticsWindow = Number(evt.target.value) || 30;
    loadAnalytics(true);
  });
}

async function hydrateBackendStatus() {
  const pill = document.getElementById('backend-status');
  if (!pill) return;

  const setStatus = (isOnline) => {
    pill.textContent = isOnline ? 'ONLINE' : 'OFFLINE';
    pill.classList.toggle('offline', !isOnline);
  };

  try {
    // Try Electron API first (for local app)
    if (window.electronAPI?.getBackendStatus) {
      const status = await window.electronAPI.getBackendStatus();
      if (status?.online) {
        setStatus(true);
        return;
      }
    }

    // Fallback: Check backend health endpoint directly (for remote/browser access)
    let res = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      cache: 'no-store',
      headers: {
        'x-loki-health-check': Date.now().toString()
      },
      signal: AbortSignal.timeout(5000)  // 5 second timeout
    });

    if (!res.ok && shouldAttemptHandshake(res.status)) {
      const handshook = await performDeploymentHandshake(true);
      if (handshook) {
        res = await fetch(`${API_BASE}/health`, {
          method: 'GET',
          cache: 'no-store',
          headers: {
            'x-loki-health-check': `${Date.now()}-retry`
          },
          signal: AbortSignal.timeout(5000)
        });
      }
    }

    setStatus(res.ok);
  } catch {
    const recovered = await performDeploymentHandshake();
    if (recovered) {
      try {
        const retry = await fetch(`${API_BASE}/health`, {
          method: 'GET',
          cache: 'no-store',
          headers: {
            'x-loki-health-check': `${Date.now()}-fallback`
          },
          signal: AbortSignal.timeout(5000)
        });
        setStatus(retry.ok);
        return;
      } catch {
        // ignore secondary failure
      }
    }
    setStatus(false);
  }
}

async function hydrateApiKeys() {
  try {
    ['anthropic', 'openai', 'gemini'].forEach(async provider => {
      const key = await window.electronAPI?.getApiKey?.(provider);
      if (key) state.apiKeys[provider] = key;
    });
    const input = document.getElementById('api-key-input');
    if (input) input.value = state.apiKeys[state.provider] || '';
  } catch {
    // ignore
  }
}

async function loadModuleCatalog() {
  try {
    const res = await fetch(`${API_BASE}/modules`);
    const payload = await res.json();
    state.modules = Array.isArray(payload?.modules) ? payload.modules : [];
  } catch {
    const fallback = await window.electronAPI?.getModules?.();
    state.modules = Array.isArray(fallback?.modules) ? fallback.modules : [];
  }
}

function renderModuleChips(containerId, storageKey) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const selected = new Set(storage.get(storageKey, []));
  if (!state.modules.length) {
    container.innerHTML = '<p class="empty">No modules loaded from backend.</p>';
    return;
  }
  container.innerHTML = state.modules.map(mod => {
    const active = selected.size ? selected.has(mod.id) : ['fca_uk', 'gdpr_uk'].includes(mod.id);
    return `
      <label class="module-chip ${active ? 'active' : ''}">
        <input type="checkbox" data-mod value="${mod.id}" ${active ? 'checked' : ''}>
        <div class="module-chip__body">
          <span class="module-chip__title">${escapeHtml(mod.name || mod.id)}</span>
          <span class="module-chip__meta">${mod.gates ?? '—'} gates · v${escapeHtml(mod.version || '1.0.0')}</span>
        </div>
      </label>
    `;
  }).join('');

  container.querySelectorAll('input[data-mod]').forEach(cb => {
    cb.addEventListener('change', () => {
      cb.closest('.module-chip').classList.toggle('active', cb.checked);
      const chosen = Array.from(container.querySelectorAll('input[data-mod]:checked')).map(el => el.value);
      storage.set(storageKey, chosen);
      renderOverviewModules();
    });
  });
  renderOverviewModules();
}

function renderOverviewModules() {
  const list = document.getElementById('overview-modules');
  if (!list || !state.modules.length) return;
  list.innerHTML = state.modules.map(mod => `
    <div class="module-chip module-chip--overview">
      <div class="module-chip__body">
        <span class="module-chip__title">${escapeHtml(mod.name)}</span>
        <span class="module-chip__meta">${mod.gates ?? '—'} gates • v${escapeHtml(mod.version || '1.0.0')}</span>
      </div>
    </div>
  `).join('');
}

function switchView(view) {
  document.querySelectorAll('.nav__item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === view);
  });
  document.querySelectorAll('.view').forEach(section => {
    section.classList.toggle('view--active', section.id === `view-${view}`);
  });
  if (view === 'analytics') loadAnalytics();
}

async function saveApiKey() {
  const provider = document.getElementById('provider-select')?.value || 'anthropic';
  const key = document.getElementById('api-key-input')?.value.trim();
  if (!key) {
    showToast('Please enter an API key for the selected provider.', 'warning', 'Missing API Key');
    return;
  }
  try {
    await window.electronAPI?.saveApiKey?.(provider, key);
    state.apiKeys[provider] = key;
    showToast('API key has been saved successfully.', 'success', 'Saved');
  } catch (error) {
    showToast('Failed to save key: ' + (error?.message || error), 'error', 'Save Failed');
  }
}

function onProviderChange(evt) {
  state.provider = evt.target.value;
  const input = document.getElementById('api-key-input');
  if (!input) return;
  input.placeholder = state.provider === 'anthropic' ? 'sk-ant-...' : state.provider === 'openai' ? 'sk-...' : 'AIzaSy...';
  input.value = state.apiKeys[state.provider] || '';
}

async function handlePromptValidation() {
  const prompt = document.getElementById('test-prompt')?.value.trim();
  const btn = document.getElementById('test-btn');
  if (!prompt) {
    showToast('Please enter a prompt to validate.', 'warning', 'Missing Prompt');
    return;
  }

  const modules = getSelectedModules('mods-interceptor');
  if (!modules.length) {
    showToast('Please select at least one FCA validation module.', 'warning', 'No Modules Selected');
    return;
  }

  const apiKey = document.getElementById('api-key-input')?.value.trim() || state.apiKeys[state.provider];
  if (!apiKey) {
    showToast('Please configure the provider API key first.', 'error', 'Missing API Key');
    return;
  }

  if (btn) { btn.disabled = true; btn.textContent = 'Validating…'; }
  try {
    let payload;
    if (window.electronAPI?.proxyRequest) {
      payload = await window.electronAPI.proxyRequest(
        '/v1/messages',
        {
          model: 'claude-sonnet-4-20250514',
          max_tokens: 900,
          messages: [{ role: 'user', content: prompt }],
          modules
        },
        apiKey
      );
    } else {
      const res = await fetch(`${API_BASE}/v1/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 900,
          messages: [{ role: 'user', content: prompt }],
          modules
        })
      });
      payload = await res.json();
    }
    displayPromptResult(payload);
    recordMetrics(payload.loki?.risk || payload.risk || 'LOW');
    pushActivity(payload.loki?.risk || payload.risk || 'LOW', 'Prompt validation executed');
    showToast('Validation completed successfully.', 'success', 'Validation Complete');
  } catch (error) {
    showToast('Validation failed: ' + (error?.message || error), 'error', 'Validation Failed');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Send & Validate'; }
  }
}

async function handleDocumentValidation() {
  const text = document.getElementById('doc-text')?.value.trim();
  const btn = document.getElementById('validate-btn');

  if (!text) {
    showToast('Please paste the document content to validate.', 'warning', 'Missing Document');
    return;
  }

  const modules = getSelectedModules('mods-validator');
  if (!modules.length) {
    showToast('Please select at least one FCA validation module.', 'warning', 'No Modules Selected');
    return;
  }

  if (btn) { btn.disabled = true; btn.textContent = 'Analysing…'; }
  try {
    const res = await fetch(`${API_BASE}/validate-document`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, modules })
    });

    const payload = await res.json();

    if (ENABLE_CORRECTIONS) {
      // Store for correction feature only when enabled
      state.lastValidation = { text, result: payload };
    }

    displayDocumentResult(payload);
    recordMetrics(payload.risk || 'LOW');
    pushActivity(payload.risk || 'LOW', 'Document validation completed');
    showToast('Document validation completed successfully.', 'success', 'Validation Complete');
  } catch (error) {
    showToast('Validation failed: ' + (error?.message || error), 'error', 'Validation Failed');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Validate Document'; }
  }
}

function displayPromptResult(result) {
  const wrapper = document.getElementById('test-result');
  const body = document.getElementById('result-content');
  if (!wrapper || !body) return;
  const validation = result.loki?.validation || result.validation || {};
  const risk = (result.loki?.risk || 'LOW').toUpperCase();
  wrapper.classList.remove('result--hidden', 'blocked', 'warning');
  if (risk === 'CRITICAL') wrapper.classList.add('blocked');
  else if (risk === 'HIGH') wrapper.classList.add('warning');

  body.innerHTML = `
    ${renderResponseText(result)}
    ${renderSemanticSummary(validation.semantic)}
    ${renderModuleBlocks(validation.modules)}
    ${renderCrossFindings(validation.cross)}
  `;
}

function displayDocumentResult(result) {
  const wrapper = document.getElementById('validation-result');
  const body = document.getElementById('validation-content');
  if (!wrapper || !body) return;
  const risk = (result.risk || 'LOW').toUpperCase();
  wrapper.classList.remove('result--hidden', 'blocked', 'warning');
  if (risk === 'CRITICAL') wrapper.classList.add('blocked');
  else if (risk === 'HIGH') wrapper.classList.add('warning');

  // Auto-correction UI is disabled for this build
  const hasFails = ENABLE_CORRECTIONS && hasFailures(result.validation);
  const correctionBtn = hasFails ? `
    <div style="margin-bottom: 1rem; text-align: right;">
      <button id="apply-corrections-btn" class="btn btn--primary" style="background: #2563eb;">
        Apply Auto-Corrections
      </button>
    </div>
  ` : '';

  body.innerHTML = `
    ${correctionBtn}
    ${renderSemanticSummary(result.semantic)}
    ${renderModuleBlocks(result.validation?.modules)}
    ${renderCrossFindings(result.validation?.cross)}
  `;

  // Bind correction button
  if (hasFails) {
    document.getElementById('apply-corrections-btn')?.addEventListener('click', handleApplyCorrections);
  }
}

function renderResponseText(result) {
  const text = extractResponseText(result);
  if (!text) return '';
  return `
    <section class="section">
      <h3>Model Response</h3>
      <div class="response-text">${escapeHtml(text)}</div>
    </section>
  `;
}

function renderModuleBlocks(modules = {}) {
  if (!modules || !Object.keys(modules).length) {
    return '<section class="section"><p class="empty">No module output.</p></section>';
  }
  return Object.entries(modules).map(([moduleId, payload]) => {
    const meta = state.modules.find(m => m.id === moduleId);
    const title = meta?.name || moduleId.replace(/_/g, ' ').toUpperCase();
    const gates = payload?.gates || {};
    const summary = payload?.summary || {};
    const summaryHtml = Object.keys(summary).length ? `
      <div class="module-summary">
        <span>Pass: ${Number(summary.pass || 0).toLocaleString()}</span>
        <span>Fail: ${Number(summary.fail || 0).toLocaleString()}</span>
        <span>Warnings: ${Number(summary.warning || 0).toLocaleString()}</span>
        ${summary.semantic_hits ? `<span>Semantic hits: ${Number(summary.semantic_hits).toLocaleString()}</span>` : ''}
        ${summary.needs_review ? `<span class="module-summary__flag">Human review flags: ${Number(summary.needs_review).toLocaleString()}</span>` : ''}
      </div>
    ` : '';
    const rendered = Object.entries(gates).map(([gateId, gate]) => renderGateResult(gateId, gate)).join('');
    return `
      <section class="section">
        <h3>${escapeHtml(title)}</h3>
        ${summaryHtml}
        ${rendered || '<p class="empty">No findings for this module.</p>'}
      </section>
    `;
  }).join('');
}

function renderSemanticSummary(semantic) {
  if (!semantic) return '';
  const hits = Number(semantic.total_hits || 0);
  const needsReview = Number(semantic.needs_review || 0);
  if (!hits && !needsReview) return '';
  return `
    <section class="section semantic-summary">
      <h3>Semantic Coverage</h3>
      <div class="module-summary">
        <span>Total semantic hits: ${hits.toLocaleString()}</span>
        ${needsReview ? `<span class="module-summary__flag">Human review required for ${needsReview.toLocaleString()} gate${needsReview === 1 ? '' : 's'}</span>` : ''}
      </div>
    </section>
  `;
}

function renderGateResult(gateId, gate = {}) {
  const status = (gate.status || 'N/A').toUpperCase();
  const severity = (gate.severity || '').toUpperCase();
  const css = status === 'FAIL' ? 'fail' : status === 'WARNING' ? 'warning' : status === 'PASS' ? 'pass' : '';
  const label = gate.name || gateId.replace(/_/g, ' ');
  const suggestion = gate.suggestion ? `<div class="gate-source">Suggested fix: ${escapeHtml(gate.suggestion)}</div>` : '';
  const source = gate.legal_source ? `<div class="gate-source">${escapeHtml(gate.legal_source)}</div>` : '';
  const message = gate.message || (status === 'N/A' ? 'Not applicable' : '');
  const semanticNotes = Array.isArray(gate.semantic_notes) ? gate.semantic_notes : [];
  const semanticHits = Array.isArray(gate.semantic_hits) ? gate.semantic_hits : [];
  const needsReview = Boolean(gate.needs_human_review);
  const reviewBadge = needsReview ? '<div class="gate-note gate-note--review">Requires human compliance review</div>' : '';
  const notesBlock = semanticNotes.length ? `
    <div class="gate-note gate-note--semantic">
      <strong>Semantic findings:</strong>
      <ul>${semanticNotes.map(note => `<li>${escapeHtml(note)}</li>`).join('')}</ul>
    </div>
  ` : '';
  const hitsBlock = semanticHits.length ? `
    <div class="gate-note gate-note--semantic">
      <strong>Matches:</strong>
      <ul>
        ${semanticHits.map(hit => {
          const core = [hit.canonical, hit.message].filter(Boolean).map(escapeHtml).join(' • ');
          const typeLabel = hit.type ? `<em>${escapeHtml(hit.type)}</em>` : '';
          const humanFlag = hit.human_review ? ' <span class="gate-tag">review</span>' : '';
          return `<li>${core || typeLabel}${humanFlag}</li>`;
        }).join('')}
      </ul>
    </div>
  ` : '';
  return `
    <div class="gate-result ${css}">
      <strong>${escapeHtml(label)} — ${status}${severity && status !== 'PASS' ? ` (${severity})` : ''}</strong>
      <div>${escapeHtml(message)}</div>
      ${source}
      ${suggestion}
      ${reviewBadge}
      ${notesBlock}
      ${hitsBlock}
    </div>
  `;
}

function renderCrossFindings(cross) {
  const issues = cross?.issues || [];
  if (!issues.length) return '';
  return `
    <section class="section">
      <h3>Cross-Module Findings</h3>
      ${issues.map(issue => `
        <div class="gate-result warning">
          <strong>${escapeHtml(issue.id || 'cross_issue')} • ${escapeHtml(issue.severity || 'medium')}</strong>
          <div>${escapeHtml(issue.message || 'Cross-check identified')}</div>
        </div>
      `).join('')}
    </section>
  `;
}

function extractResponseText(result) {
  try {
    const blocks = result.response?.content || result.content;
    if (Array.isArray(blocks)) {
      return blocks.filter(b => b?.type === 'text').map(b => b.text || '').join('\n\n');
    }
    return result.response?.text || '';
  } catch {
    return '';
  }
}

function getSelectedModules(storageKey) {
  const stored = storage.get(storageKey, []);
  return stored.length ? stored : state.modules.map(m => m.id);
}

function recordMetrics(risk) {
  const upper = (risk || 'LOW').toUpperCase();
  state.stats.validated += 1;
  if (upper === 'CRITICAL') state.stats.blocked += 1;
  if (upper === 'HIGH') state.stats.warnings += 1;
  document.getElementById('stat-validated').textContent = state.stats.validated;
  document.getElementById('stat-warnings').textContent = state.stats.warnings;
  document.getElementById('stat-blocked').textContent = state.stats.blocked;
}

function pushActivity(risk, summary) {
  const feed = document.getElementById('activity-feed');
  if (!feed) return;
  const entry = document.createElement('div');
  const riskLevel = (risk || 'LOW').toUpperCase();
  entry.className = 'activity-item';
  entry.innerHTML = `
    <div class="activity-row">
      <span class="activity-risk" data-risk="${riskLevel}">${riskLevel}</span>
      <span class="activity-time">${formatDate(new Date())}</span>
    </div>
    <div class="meta">${escapeHtml(summary)}</div>
  `;
  const empty = feed.querySelector('.empty');
  if (empty) empty.remove();
  feed.prepend(entry);
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatDate(date) {
  try {
    return date.toLocaleString();
  } catch {
    return String(date);
  }
}

async function loadAnalytics(force = false) {
  if (!force && state.analytics.overview) return renderAnalytics();
  state.analytics.loading = true;
  state.analytics.error = null;
  renderAnalytics();
  try {
    const windowDays = state.analyticsWindow;
    const [overview, trends, modules] = await Promise.all([
      fetchJson(`${API_BASE}/analytics/overview?window=${windowDays}`),
      fetchJson(`${API_BASE}/analytics/trends?days=${windowDays}`),
      fetchJson(`${API_BASE}/analytics/modules?window=${windowDays}`)
    ]);
    state.analytics = { loading: false, error: null, overview, trends, modules, window: windowDays };
  } catch (error) {
    state.analytics = { loading: false, error: error.message || 'Analytics unavailable', overview: null, trends: null, modules: null };
  }
  renderAnalytics();
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function renderAnalytics() {
  const { loading, error, overview, trends, modules } = state.analytics;
  const overviewEl = document.getElementById('analytics-overview');
  const trendsEl = document.getElementById('analytics-trends');
  const universalEl = document.getElementById('analytics-universal');
  const modulesEl = document.getElementById('analytics-modules');
  const recentEl = document.getElementById('analytics-recent');
  const windowSelect = document.getElementById('analytics-window');
  if (windowSelect) windowSelect.value = String(state.analyticsWindow);
  if (!overviewEl || !trendsEl || !universalEl || !modulesEl || !recentEl) return;

  if (loading) {
    [overviewEl, trendsEl, universalEl, modulesEl, recentEl].forEach(el => el.innerHTML = '<p class="empty">Loading…</p>');
    return;
  }
  if (error) {
    [overviewEl, trendsEl, universalEl, modulesEl, recentEl].forEach(el => el.innerHTML = `<p class="empty">${escapeHtml(error)}</p>`);
    return;
  }
  if (!overview) {
    [overviewEl, trendsEl, universalEl, modulesEl, recentEl].forEach(el => el.innerHTML = '<p class="empty">No analytics data.</p>');
    return;
  }

  const stats = overview.stats || {};
  const breakdown = stats.risk_breakdown || {};
  overviewEl.innerHTML = [
    analyticsCard('Validations', stats.total_validations || 0),
    analyticsCard('Critical', breakdown.critical || 0),
    analyticsCard('High', breakdown.high || 0),
    analyticsCard('Low', breakdown.low || 0),
    analyticsCard('Module Packs', (overview.module_performance || []).length)
  ].join('');

  const trendData = trends?.timeline || [];
  trendsEl.innerHTML = trendData.length ? trendData.map(entry => `
    <div class="list-item">
      <strong>${escapeHtml(entry.date)}</strong>
      <div class="meta">Critical: ${entry.counts?.CRITICAL || 0} • High: ${entry.counts?.HIGH || 0} • Low: ${entry.counts?.LOW || 0}</div>
    </div>
  `).join('') : '<p class="empty">No trend data in this window.</p>';

  const universal = overview.universal_alerts || [];
  universalEl.innerHTML = universal.length ? universal.map(alert => `
    <div class="list-item">
      <strong>${escapeHtml(alert.detector)}</strong>
      <div class="meta">Alerts: ${alert.alerts || 0} • Severity ${escapeHtml(alert.severity || 'unknown')}</div>
    </div>
  `).join('') : '<p class="empty">No universal alerts recorded.</p>';

  const modulePerf = modules?.modules || overview.module_performance || [];
  modulesEl.innerHTML = modulePerf.length ? modulePerf.map(mod => `
    <div class="list-item">
      <strong>${escapeHtml(mod.module)}</strong>
      <div class="meta">Fail: ${mod.failures || 0} • Warn: ${mod.warnings || 0} • Pass: ${mod.passes || 0}</div>
    </div>
  `).join('') : '<p class="empty">No module telemetry yet.</p>';

  const recent = overview.recent_activity || [];
  recentEl.innerHTML = recent.length ? recent.map(item => `
    <div class="list-item">
      <strong>${escapeHtml(item.overall_risk || 'LOW')}</strong>
      <div class="meta">${escapeHtml(item.document_type || 'document')} • ${escapeHtml(formatDate(new Date(item.timestamp)))}
      </div>
    </div>
  `).join('') : '<p class="empty">No recent cases.</p>';
}

function analyticsCard(label, value) {
  return `
    <div class="module-chip module-chip--overview">
      <div class="module-chip__body">
        <span class="module-chip__title">${escapeHtml(label)}</span>
        <span class="module-chip__meta">${Number(value || 0).toLocaleString()}</span>
      </div>
    </div>
  `;
}

function shouldAttemptHandshake(status) {
  return status === 403 || status === 429 || status === 503;
}

async function performDeploymentHandshake(force = false) {
  const now = Date.now();
  if (!force && now - lastHandshakeAt < HANDSHAKE_TTL_MS) {
    return true;
  }

  try {
    const res = await fetch('/', {
      method: 'GET',
      cache: 'no-store',
      credentials: 'same-origin',
      headers: { 'x-loki-handshake': now.toString() }
    });
    if (res.ok) {
      lastHandshakeAt = now;
      return true;
    }
  } catch {
    // ignore handshake failures
  }

  return false;
}

// === DOCUMENT CORRECTION FEATURE ===

function hasFailures(validation) {
  if (!validation || !validation.modules) return false;
  return Object.values(validation.modules).some(mod => {
    const gates = mod?.gates || {};
    return Object.values(gates).some(gate => gate?.status === 'FAIL');
  });
}

async function handleApplyCorrections() {
  if (!ENABLE_CORRECTIONS) {
    showToast('Auto-corrections are disabled on this build.', 'info', 'Not Available');
    return;
  }

  const btn = document.getElementById('apply-corrections-btn');
  if (!state.lastValidation.text || !state.lastValidation.result) {
    showToast('No validation data available', 'error', 'Correction Failed');
    return;
  }

  console.log('Applying corrections...', {
    text: state.lastValidation.text.substring(0, 100),
    validation: state.lastValidation.result.validation
  });

  if (btn) { btn.disabled = true; btn.textContent = 'Applying Corrections…'; }

  try {
    const res = await fetch(`${API_BASE}/correct-document`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: state.lastValidation.text,
        validation_results: state.lastValidation.result.validation
      })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    }

    const correctionResult = await res.json();
    console.log('Correction result:', correctionResult);
    displayCorrectionComparison(correctionResult);
    showToast('Corrections applied successfully', 'success', 'Corrections Complete');
  } catch (error) {
    console.error('Correction error:', error);
    showToast('Correction failed: ' + (error?.message || error), 'error', 'Correction Failed');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Apply Auto-Corrections'; }
  }
}

function displayCorrectionComparison(correctionResult) {
  const body = document.getElementById('validation-content');
  if (!body) return;

  const original = state.lastValidation.text || '';
  const corrected = correctionResult.corrected_text || original;
  const changes = correctionResult.changes || [];
  const changeCount = correctionResult.changes_made || changes.length;

  body.innerHTML = `
    <div style="margin-bottom: 1.5rem;">
      <h3 style="margin-bottom: 0.5rem;">Document Comparison</h3>
      <p style="color: #64748b; font-size: 0.875rem;">${changeCount} correction${changeCount !== 1 ? 's' : ''} applied</p>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div>
        <h4 style="margin-bottom: 0.75rem; color: #ef4444;">Original Document</h4>
        <div style="background: #ffffff; border: 2px solid #ef4444; border-radius: 0.5rem; padding: 1rem; max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 0.875rem; line-height: 1.6; white-space: pre-wrap; color: #1e293b;">${escapeHtml(original)}</div>
      </div>
      <div>
        <h4 style="margin-bottom: 0.75rem; color: #10b981;">Corrected Document</h4>
        <div style="background: #ffffff; border: 2px solid #10b981; border-radius: 0.5rem; padding: 1rem; max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 0.875rem; line-height: 1.6; white-space: pre-wrap; color: #1e293b;">${highlightChanges(corrected, changes)}</div>
        <button id="copy-corrected-btn" class="btn btn--secondary" style="margin-top: 0.75rem;">Copy Corrected Text</button>
      </div>
    </div>

    <div style="margin-bottom: 1.5rem;">
      <h4 style="margin-bottom: 0.75rem;">Changes Applied</h4>
      ${renderChanges(changes)}
    </div>

    <div style="text-align: center; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
      <button id="back-to-validation-btn" class="btn btn--secondary">Back to Validation Results</button>
    </div>
  `;

  // Bind buttons
  document.getElementById('copy-corrected-btn')?.addEventListener('click', () => {
    navigator.clipboard.writeText(corrected);
    showToast('Corrected text copied to clipboard', 'success', 'Copied');
  });

  document.getElementById('back-to-validation-btn')?.addEventListener('click', () => {
    displayDocumentResult(state.lastValidation.result);
  });
}

function highlightChanges(text, changes) {
  // No inline highlighting - just show corrected text cleanly
  return escapeHtml(text);
}

function renderChanges(changes) {
  if (!changes || !changes.length) {
    return '<p class="empty">No specific changes tracked</p>';
  }

  return `
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem;">
      ${changes.map((change, idx) => `
        <div style="margin-bottom: ${idx < changes.length - 1 ? '1rem' : '0'}; padding-bottom: ${idx < changes.length - 1 ? '1rem' : '0'}; border-bottom: ${idx < changes.length - 1 ? '1px solid #e2e8f0' : 'none'};">
          <div style="font-weight: 600; margin-bottom: 0.25rem; color: #1e293b;">${escapeHtml(change.type || 'Correction')}</div>
          ${change.before ? `<div style="color: #ef4444; font-size: 0.875rem;"><strong>Before:</strong> ${escapeHtml(change.before)}</div>` : ''}
          ${change.after ? `<div style="color: #10b981; font-size: 0.875rem;"><strong>After:</strong> ${escapeHtml(change.after)}</div>` : ''}
          ${change.reason ? `<div style="color: #64748b; font-size: 0.875rem; margin-top: 0.25rem;"><em>${escapeHtml(change.reason)}</em></div>` : ''}
        </div>
      `).join('')}
    </div>
  `;
}

window.addEventListener('DOMContentLoaded', init);
