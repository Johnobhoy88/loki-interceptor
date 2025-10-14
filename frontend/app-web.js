// Dynamic backend URL getter - fetches from api.txt every time
const REMOTE_API_BASE = 'https://loki-interceptor-5hqwbuvs4-john-s-projects-2735c2d1.vercel.app';

async function getBackendUrl() {
  try {
    const response = await fetch('/api.txt?t=' + Date.now());
    if (response.ok) {
      const url = (await response.text()).trim();
      if (url) {
        console.log('[LOKI] Using backend URL:', url);
        return url;
      }
    }
  } catch (e) {
    console.warn('[LOKI] Failed to load backend URL from api.txt:', e);
  }
  console.log('[LOKI] Falling back to remote API base');
  return REMOTE_API_BASE;
}

// State management
const state = {
  apiKeys: {},
  modules: [],
  stats: { requests: 0, warnings: 0, blocked: 0 },
  activityLog: [],
  provider: 'anthropic',
  analyticsWindow: 30,
  analytics: {
    overview: null,
    trends: null,
    modules: null,
    loading: false,
    error: null
  }
};

// Web fallback for electronAPI
if (!window.electronAPI) {
  window.electronAPI = {
    getBackendStatus: async () => {
      const backendUrl = await getBackendUrl();
      try {
        const resp = await fetch(`${backendUrl}/health`);
        return { online: resp.ok };
      } catch {
        return { online: false };
      }
    },
    getModules: async () => {
      const backendUrl = await getBackendUrl();
      try {
        const resp = await fetch(`${backendUrl}/modules`);
        const data = await resp.json();
        return data;
      } catch {
        return { modules: [
          { id: 'hr_scottish', name: 'HR & Employment', version: '2.0.0', gates: 16 },
          { id: 'gdpr_uk', name: 'GDPR UK', version: '2.0.0', gates: 15 },
          { id: 'nda_uk', name: 'NDA UK/EU', version: '1.0.0', gates: 14 },
          { id: 'tax_uk', name: 'Tax & Financial', version: '1.0.0', gates: 15 },
          { id: 'fca_uk', name: 'FCA Financial Conduct', version: '1.0.0', gates: 25 }
        ] };
      }
    },
    getApiKey: async (provider) => localStorage.getItem(`api_key_${provider}`) || '',
    saveApiKey: async (provider, key) => {
      localStorage.setItem(`api_key_${provider}`, key);
      return {};
    },
    proxyRequest: async (endpoint, payload, apiKey) => {
      const backendUrl = await getBackendUrl();
      try {
        const resp = await fetch(`${backendUrl}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey || ''
          },
          body: JSON.stringify(payload)
        });
        return await resp.json();
      } catch (e) {
        return { error: e.message };
      }
    }
  };
}

// Initialize app
async function init() {
  await checkBackendStatus();
  await loadConfig();
  setupEventListeners();
  initProviderUI();
  // Render modules dynamically from backend for both panels
  renderModulesUI();

  // Fix textarea keyboard input in Electron - keep them permanently enabled
  setInterval(() => {
    const testPrompt = document.getElementById('test-prompt');
    const docText = document.getElementById('doc-text');
    if (testPrompt) {
      testPrompt.removeAttribute('readonly');
      testPrompt.removeAttribute('disabled');
    }
    if (docText) {
      docText.removeAttribute('readonly');
      docText.removeAttribute('disabled');
    }
  }, 500);

  // Check if first launch
  const hasAnthropic = await window.electronAPI.getApiKey('anthropic');
  const hasOpenAI = await window.electronAPI.getApiKey('openai');
  const hasGemini = await window.electronAPI.getApiKey('gemini');
  if (hasAnthropic) state.apiKeys.anthropic = hasAnthropic;
  if (hasOpenAI) state.apiKeys.openai = hasOpenAI;
  if (hasGemini) state.apiKeys.gemini = hasGemini;
}

async function checkBackendStatus() {
  const status = await window.electronAPI.getBackendStatus();
  const statusEl = document.getElementById('backend-status');

  if (status.online) {
    statusEl.textContent = '🟢 Backend Online';
    statusEl.style.background = '#27ae60';
  } else {
    statusEl.textContent = '🔴 Backend Offline';
    statusEl.style.background = '#e74c3c';
  }
}

async function loadConfig() {
  const modules = await window.electronAPI.getModules();
  if (modules?.modules) {
    state.modules = modules.modules;
  } else if (modules?.available) {
    state.modules = modules.available;
  } else {
    state.modules = [];
  }
}

function setupEventListeners() {
  const saveKeyBtn = document.getElementById('save-key-btn');
  if (saveKeyBtn) saveKeyBtn.addEventListener('click', saveKey);
  document.getElementById('test-btn').addEventListener('click', testRequest);
  const validateBtn = document.getElementById('validate-btn');
  if (validateBtn) validateBtn.addEventListener('click', validateDocument);
  const sendBtn = document.getElementById('send-btn');
  if (sendBtn) sendBtn.addEventListener('click', sendToApi);
  const refreshBtn = document.getElementById('refresh-status');
  if (refreshBtn) refreshBtn.addEventListener('click', checkBackendStatus);

  // Navigation switching
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  const providerSelect = document.getElementById('provider-select');
  if (providerSelect) providerSelect.addEventListener('change', onProviderChange);

  const analyticsWindowSelect = document.getElementById('analytics-window');
  if (analyticsWindowSelect) analyticsWindowSelect.addEventListener('change', onAnalyticsWindowChange);

}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      'bypass-tunnel-reminder': 'true'
    }
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text || response.statusText}`);
  }
  return response.json();
}

function onAnalyticsWindowChange(event) {
  const value = Number(event?.target?.value) || 30;
  state.analyticsWindow = value;
  loadAnalytics(value, true);
}

async function loadAnalytics(windowDays, force = false) {
  const targetWindow = Number(windowDays) || state.analyticsWindow || 30;

  if (!force && state.analytics.overview && state.analyticsWindow === targetWindow && !state.analytics.error) {
    renderAnalytics();
    return;
  }

  state.analyticsWindow = targetWindow;
  state.analytics.loading = true;
  state.analytics.error = null;
  renderAnalytics();

  try {
    const backendUrl = await getBackendUrl();
    const [overview, trends, modules] = await Promise.all([
      fetchJson(`${backendUrl}/analytics/overview?window=${targetWindow}`),
      fetchJson(`${backendUrl}/analytics/trends?days=${targetWindow}`),
      fetchJson(`${backendUrl}/analytics/modules?window=${targetWindow}`)
    ]);

    state.analytics.overview = overview;
    state.analytics.trends = trends;
    state.analytics.modules = modules;
    state.analytics.loading = false;
    state.analytics.error = null;
  } catch (error) {
    console.error('Analytics load failed', error);
    state.analytics.loading = false;
    state.analytics.error = error?.message || 'Failed to load analytics';
    state.analytics.overview = null;
    state.analytics.trends = null;
    state.analytics.modules = null;
  }

  renderAnalytics();
}

function renderAnalytics() {
  const overviewEl = document.getElementById('analytics-overview');
  const trendsEl = document.getElementById('analytics-trends');
  const universalEl = document.getElementById('analytics-universal');
  const modulesEl = document.getElementById('analytics-modules');
  const recentEl = document.getElementById('analytics-recent');
  const windowSelect = document.getElementById('analytics-window');

  if (windowSelect) {
    windowSelect.value = String(state.analyticsWindow);
  }

  if (!overviewEl || !trendsEl || !universalEl || !modulesEl || !recentEl) {
    return;
  }

  const { loading, error, overview, trends, modules } = state.analytics;

  if (loading) {
    const loadingHtml = '<p class="empty-state">Loading analytics…</p>';
    overviewEl.innerHTML = loadingHtml;
    trendsEl.innerHTML = loadingHtml;
    universalEl.innerHTML = loadingHtml;
    modulesEl.innerHTML = loadingHtml;
    recentEl.innerHTML = loadingHtml;
    return;
  }

  if (error) {
    const errorHtml = `<p class="empty-state">${escapeHtml(error)}</p>`;
    overviewEl.innerHTML = errorHtml;
    trendsEl.innerHTML = errorHtml;
    universalEl.innerHTML = errorHtml;
    modulesEl.innerHTML = errorHtml;
    recentEl.innerHTML = errorHtml;
    return;
  }

  if (!overview) {
    const emptyHtml = '<p class="empty-state">No analytics data yet.</p>';
    overviewEl.innerHTML = emptyHtml;
    trendsEl.innerHTML = emptyHtml;
    universalEl.innerHTML = emptyHtml;
    modulesEl.innerHTML = emptyHtml;
    recentEl.innerHTML = emptyHtml;
    return;
  }

  const stats = overview.stats || {};
  const breakdown = stats.risk_breakdown || {};
  const moduleCount = (overview.module_performance || []).length;
  const cards = [
    { label: 'Validations', value: stats.total_validations || 0, color: '#6c5ce7' },
    { label: 'Critical Risk', value: breakdown.critical || 0, color: '#ef4444' },
    { label: 'High Risk', value: breakdown.high || 0, color: '#f59e0b' },
    { label: 'Low Risk', value: breakdown.low || 0, color: '#27ae60' },
    { label: 'Modules Active', value: moduleCount, color: '#3498db' }
  ];

  overviewEl.innerHTML = cards.map(card => {
    return `
      <div class="analytics-stat">
        <span class="label">${escapeHtml(card.label)}</span>
        <span class="value" style="color:${card.color}">${formatNumber(card.value)}</span>
      </div>
    `;
  }).join('');

  const trendData = (trends && trends.timeline) || [];
  if (!trendData.length) {
    trendsEl.innerHTML = '<p class="empty-state">No trend data for the selected window.</p>';
  } else {
    trendsEl.innerHTML = trendData.map(entry => {
      const counts = entry.counts || {};
      return `
        <div class="analytics-trend">
          <strong>${escapeHtml(entry.date)}</strong>
          <div>Critical: <span style="color:#ef4444">${formatNumber(counts.CRITICAL)}</span></div>
          <div>High: <span style="color:#f59e0b">${formatNumber(counts.HIGH)}</span></div>
          <div>Low: <span style="color:#27ae60">${formatNumber(counts.LOW)}</span></div>
        </div>
      `;
    }).join('');
  }

  const universalAlerts = overview.universal_alerts || [];
  if (!universalAlerts.length) {
    universalEl.innerHTML = '<p class="empty-state">No universal alerts recorded.</p>';
  } else {
    universalEl.innerHTML = universalAlerts.map(alert => {
      return `
        <div class="list-item">
          <strong>${escapeHtml(alert.detector)}</strong>
          <div class="meta">${formatNumber(alert.alerts)} alerts • Severity ${escapeHtml(alert.severity || 'unknown')}</div>
        </div>
      `;
    }).join('');
  }

  const modulePerformance = (modules && modules.modules) || overview.module_performance || [];
  if (!modulePerformance.length) {
    modulesEl.innerHTML = '<p class="empty-state">No module executions captured yet.</p>';
  } else {
    modulesEl.innerHTML = modulePerformance.map(mod => {
      return `
        <div class="list-item">
          <strong>${escapeHtml(mod.module)}</strong>
          <div class="meta">Fail: ${formatNumber(mod.failures || 0)} • Warn: ${formatNumber(mod.warnings || 0)} • Pass: ${formatNumber(mod.passes || 0)}</div>
        </div>
      `;
    }).join('');
  }

  const recent = overview.recent_activity || [];
  if (!recent.length) {
    recentEl.innerHTML = '<p class="empty-state">No recent validations logged.</p>';
  } else {
    recentEl.innerHTML = recent.map(entry => {
      const risk = (entry.overall_risk || 'UNKNOWN').toUpperCase();
      const color = risk === 'CRITICAL' ? '#ef4444' : risk === 'HIGH' ? '#f59e0b' : '#6c5ce7';
      return `
        <div class="list-item">
          <strong style="color:${color}">${escapeHtml(risk)}</strong>
          <div class="meta">${escapeHtml(entry.document_type || 'document')} • ${formatDateTime(entry.timestamp)}</div>
        </div>
      `;
    }).join('');
  }
}

function formatNumber(value) {
  const num = Number(value || 0);
  return Number.isNaN(num) ? '0' : num.toLocaleString();
}

function formatDateTime(isoString) {
  if (!isoString) return 'unknown time';
  const dt = new Date(isoString);
  if (Number.isNaN(dt.getTime())) return escapeHtml(String(isoString));
  return escapeHtml(dt.toLocaleString());
}

async function saveKey() {
  const providerSelect = document.getElementById('provider-select');
  const provider = providerSelect ? providerSelect.value : 'anthropic';
  const keyInput = document.getElementById('api-key-input');
  const key = keyInput ? keyInput.value.trim() : '';
  const saveBtn = document.getElementById('save-key-btn');

  if (!key) {
    if (saveBtn) saveBtn.textContent = '❌ Enter API key';
    setTimeout(() => { if (saveBtn) saveBtn.textContent = 'Save Credentials'; }, 2000);
    return;
  }

  try {
    if (saveBtn) saveBtn.textContent = 'Saving...';
    await window.electronAPI.saveApiKey(provider, key);
    state.apiKeys[provider] = key;
    state.provider = provider;
    if (saveBtn) saveBtn.textContent = '✅ Saved';
    setTimeout(() => { if (saveBtn) saveBtn.textContent = 'Save Credentials'; }, 2000);
  } catch (e) {
    if (saveBtn) saveBtn.textContent = '❌ Failed';
    setTimeout(() => { if (saveBtn) saveBtn.textContent = 'Save Credentials'; }, 2000);
  }
}

async function testRequest() {
  const prompt = document.getElementById('test-prompt').value;
  if (!prompt) return;

  const testBtn = document.getElementById('test-btn');
  testBtn.disabled = true;
  testBtn.textContent = 'Processing...';

  try {
    let result;
    const providerSel = document.getElementById('provider-select');
    const provider = providerSel ? providerSel.value : state.provider;
    const keyInput = document.getElementById('api-key-input');
    const currentKey = keyInput ? keyInput.value.trim() : (state.apiKeys[provider] || '');

    // Selected modules (optional). If none selected, backend will use defaults.
    const selectedModules = getSelectedModules(false);

    if (provider === 'anthropic') {
      result = await window.electronAPI.proxyRequest(
        '/v1/messages',
        {
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1024,
          messages: [{ role: 'user', content: prompt }],
          ...(selectedModules.length ? { modules: selectedModules } : {})
        },
        currentKey
      );
    } else {
      const payload = { provider };
      if (provider === 'openai') {
        payload.model = 'gpt-4';
        payload.max_tokens = 1024;
        payload.messages = [{ role: 'user', content: prompt }];
      } else if (provider === 'gemini') {
        payload.model = 'gemini-1.5-flash';
        payload.prompt = prompt;
      }
      if (selectedModules.length) payload.modules = selectedModules;
      const headers = { 'Content-Type': 'application/json' };
      if (provider === 'openai') headers['openai-api-key'] = currentKey || '';
      if (provider === 'gemini') headers['gemini-api-key'] = currentKey || '';
      const backendUrl = await getBackendUrl();
      const resp = await fetch(`${backendUrl}/proxy`, { method: 'POST', headers, body: JSON.stringify(payload) });
      result = await resp.json();
    }

    displayResult(result);
    updateStats(result);
    addActivityItem(result);

  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    testBtn.disabled = false;
    testBtn.textContent = 'Send to Claude';
  }
}

function getSelectedModules(forValidator = false) {
  const mods = [];
  try {
    const container = forValidator
      ? document.getElementById('modules-validator')
      : document.getElementById('modules-interceptor');

    if (!container) return [];

    const checkboxes = container.querySelectorAll('input[type="checkbox"][data-mod]:checked');
    checkboxes.forEach(cb => {
      const moduleId = cb.value || cb.getAttribute('value');
      if (moduleId) mods.push(moduleId);
    });

    // Fallback to old ID system if new one doesn't work
    if (mods.length === 0) {
      const prefix = forValidator ? 'v-mod' : 'mod';
      const hr = document.getElementById(`${prefix}-hr_scottish`);
      const gdpr = document.getElementById(`${prefix}-gdpr_uk`);
      const nda = document.getElementById(`${prefix}-nda_uk`);
      const tax = document.getElementById(`${prefix}-tax_uk`);
      if (hr && hr.checked) mods.push('hr_scottish');
      if (gdpr && gdpr.checked) mods.push('gdpr_uk');
      if (nda && nda.checked) mods.push('nda_uk');
      if (tax && tax.checked) mods.push('tax_uk');
    }
  } catch {}
  return mods;
}

function displayResult(result) {
  const resultBox = document.getElementById('test-result') || document.getElementById('result-box');
  const contentEl = document.getElementById('result-content');

  resultBox.classList.remove('hidden', 'blocked', 'warning');
  const risk = result.loki?.risk || result.validation?.overall_risk || 'LOW';
  if (risk !== 'LOW') resultBox.classList.add('warning');

  // Extract response text from either shape
  let responseText = '';
  try {
    const blocks = (result.response && result.response.content) || result.content || [];
    if (Array.isArray(blocks)) {
      responseText = blocks.filter(b => b && b.type === 'text').map(b => b.text || '').join('\n\n');
    }
  } catch {}

  const validation = result.loki?.validation || result.validation || {};

  // Build UI: Model Response + Validation Issues
  let html = '';
  if (result.error) {
    html += `<div class="gate-result fail"><h4>Provider Error</h4><p>${result.error}</p>${result.reason ? `<p>${result.reason}</p>` : ''}</div>`;
  }
  html += `<h4>Model Response</h4>`;
  const highlighted = highlightViolations(responseText || '', validation);
  html += `<div class="response-text">${highlighted || '(no text content)'}</div>`;

  // Add legend for highlights if any spans present
  const hasPiISpans = Array.isArray(validation?.universal?.pii?.spans) && validation.universal.pii.spans.length > 0;
  const hasGateSpans = !!(validation?.modules && Object.values(validation.modules).some(m => Object.values(m.gates || {}).some(g => Array.isArray(g.spans) && g.spans.length > 0)));
  if (hasPiISpans || hasGateSpans) {
    html += `
      <div class="highlight-legend" style="margin: 0.5rem 0 0.25rem; display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
        <span style="font-size: 0.85rem; color: var(--text-secondary);">Highlights:</span>
        <span><mark class="violation-highlight" style="background-color: #ef444420; color: #ef4444; border-bottom: 2px solid #ef4444;">Critical</mark></span>
        <span><mark class="violation-highlight" style="background-color: #f59e0b20; color: #f59e0b; border-bottom: 2px solid #f59e0b;">High</mark></span>
        <span><mark class="violation-highlight" style="background-color: #6366f120; color: #6366f1; border-bottom: 2px solid #6366f1;">Medium</mark></span>
      </div>
    `;
  }

  html += `<h4 style="margin-top:1rem;">Validation Issues (Risk: ${risk})</h4>`;

  // Universal checks
  const u = validation.universal || {};
  if (u.pii && (u.pii.status !== 'PASS')) {
    html += `<div class="gate-result ${u.pii.severity === 'critical' ? 'fail' : 'pass'}"><h4>PII</h4><p>${u.pii.message || ''}</p></div>`;
  }
  if (u.contradictions && (u.contradictions.status !== 'PASS')) {
    html += `<div class="gate-result ${u.contradictions.severity === 'high' ? 'fail' : 'pass'}"><h4>Contradictions</h4><p>${u.contradictions.message || ''}</p></div>`;
  }
  if (u.hallucinations && ((u.hallucinations.status || '').toUpperCase() === 'WARNING')) {
    html += `<div class="gate-result warning"><h4>Hallucination Markers</h4><p>${u.hallucinations.message || ''}</p></div>`;
  }

  // Domain gates: HR and GDPR — only FAIL gates
  const modules = (validation.modules) || {};
  const hr = modules.hr_scottish && modules.hr_scottish.gates ? modules.hr_scottish.gates : null;
  const gdpr = modules.gdpr_uk && modules.gdpr_uk.gates ? modules.gdpr_uk.gates : null;
  if (hr) {
    html += '<h4 style="margin-top:1rem;">HR Compliance</h4><div class="gates-list">';
    for (const [gateName, gate] of Object.entries(hr)) {
      if (!gate || gate.status === 'N/A' || gate.status === 'PASS') continue;
      html += `
        <div class="gate-result fail">
          <h4>❌ ${gateName.replace(/_/g, ' ').toUpperCase()}</h4>
          <p>${gate.message || ''}</p>
          ${gate.suggestion ? `<p><strong>Fix:</strong> ${gate.suggestion}</p>` : ''}
          ${gate.legal_source ? `<p><em>${gate.legal_source}</em></p>` : ''}
        </div>`;
    }
    html += '</div>';
  }
  if (gdpr) {
    html += '<h4 style="margin-top:1rem;">GDPR Compliance</h4><div class="gates-list">';
    for (const [gateName, gate] of Object.entries(gdpr)) {
      if (!gate || gate.status === 'N/A' || gate.status === 'PASS') continue;
      html += `
        <div class="gate-result fail">
          <h4>❌ ${gateName.replace(/_/g, ' ').toUpperCase()}</h4>
          <p>${gate.message || ''}</p>
          ${gate.suggestion ? `<p><strong>Fix:</strong> ${gate.suggestion}</p>` : ''}
          ${gate.legal_source ? `<p><em>${gate.legal_source}</em></p>` : ''}
        </div>`;
    }
    html += '</div>';
  }

  // Fallback: if nothing to show, include JSON details
  if (!u.pii && !u.contradictions && !u.hallucinations && !hr && !gdpr) {
    html += `<details><summary>Validation Details</summary><pre>${JSON.stringify(validation, null, 2)}</pre></details>`;
  }

  contentEl.innerHTML = html;

  resultBox.classList.remove('hidden');
}

// Standalone API send (simple /v1/messages flow)
async function sendToApi() {
  const promptEl = document.getElementById('api-prompt') || document.getElementById('test-prompt');
  const prompt = (promptEl?.value || '').trim();
  const sendBtn = document.getElementById('send-btn');

  if (!prompt) {
    alert('Please enter a prompt');
    return;
  }

  // Gather modules from API page checkboxes
  const modules = [];
  const apiHr = document.getElementById('api-module-hr');
  const apiGdpr = document.getElementById('api-module-gdpr');
  const apiNda = document.getElementById('api-module-nda');
  const apiTax = document.getElementById('api-module-tax');
  if (apiHr && apiHr.checked) modules.push('hr_scottish');
  if (apiGdpr && apiGdpr.checked) modules.push('gdpr_uk');
  if (apiNda && apiNda.checked) modules.push('nda_uk');
  if (apiTax && apiTax.checked) modules.push('tax_uk');

  if (modules.length === 0) {
    alert('Please select at least one validation module');
    return;
  }

  // API key sources: localStorage fallback or input
  const keyFromStorage = localStorage.getItem('claude_api_key') || '';
  const keyInput = document.getElementById('api-key-input');
  const apiKey = (keyInput?.value || keyFromStorage || '').trim();

  if (!apiKey) {
    alert('Please configure your API key first');
    return;
  }

  if (sendBtn) { sendBtn.disabled = true; sendBtn.textContent = 'Sending...'; }
  try {
    const backendUrl = await getBackendUrl();
    const resp = await fetch(`${backendUrl}/v1/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1024,
        messages: [{ role: 'user', content: prompt }],
        modules
      })
    });
    const result = await resp.json();
    displayResult(result);
    updateStats(result);
    addActivityItem(result);
  } catch (e) {
    alert('Error sending to API: ' + (e?.message || e));
  } finally {
    if (sendBtn) { sendBtn.disabled = false; sendBtn.textContent = 'Send & Validate'; }
  }
}

// --- Inline Highlighter ---
function highlightResponseText(text, validation) {
  if (!text) return '';

  // Build highlight patterns from analyzers + universal checks
  const patterns = [];

  // PII entities from analyzer (most precise)
  try {
    const entities = validation?.analyzers?.pii?.entities || [];
    entities.forEach(e => {
      const m = (e.match || '').trim();
      if (!m) return;
      const cls = e.type === 'credit_card' ? 'hl-critical'
                : (e.type === 'ni_number' || e.type === 'nhs_number' || e.type === 'ssn') ? 'hl-high'
                : 'hl-medium';
      patterns.push({ regex: new RegExp(escapeRegExp(m), 'g'), cls });
    });
  } catch {}

  // Contradiction sentences from universal detectors
  try {
    const contras = validation?.universal?.contradictions?.contradictions || [];
    contras.forEach(c => {
      const s1 = (c.sentence_1 || '').trim();
      const s2 = (c.sentence_2 || '').trim();
      if (s1) patterns.push({ regex: new RegExp(escapeRegExp(s1), 'g'), cls: 'hl-contradiction' });
      if (s2) patterns.push({ regex: new RegExp(escapeRegExp(s2), 'g'), cls: 'hl-contradiction' });
    });
  } catch {}

  // Prohibited/absolute terms (heuristic)
  const prohibited = [
    /\balways\b/gi,
    /\bnever\b/gi,
    /\bguaranteed\b/gi,
    /\bproven\s+fact\b/gi,
    /\bimpossible\b/gi
  ];
  prohibited.forEach(rx => patterns.push({ regex: rx, cls: 'hl-prohibited' }));

  // Apply highlighting safely: replace with placeholders, then escape and inject spans
  let working = String(text);
  const marks = [];

  // Sort patterns to highlight longer matches first (reduce overlaps)
  // For regexes without source length (like with modifiers), we skip sorting complexity
  // and rely on iteration order.

  patterns.forEach((p, idx) => {
    const token = `[[HL${idx}]]`;
    try {
      working = working.replace(p.regex, (m) => {
        marks.push({ token, text: m, cls: p.cls });
        return token;
      });
    } catch {}
  });

  // Escape entire text
  let escaped = escapeHtml(working);

  // Inject spans for placeholders
  marks.forEach(mark => {
    const safeInner = escapeHtml(mark.text);
    const span = `<span class="hl ${mark.cls}">${safeInner}</span>`;
    escaped = escaped.split(mark.token).join(span);
  });

  return escaped;
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function updateStats(result) {
  state.stats.requests++;

  if (result.blocked) {
    state.stats.blocked++;
  } else if (result.loki?.risk === 'HIGH' || result.loki?.risk === 'CRITICAL') {
    state.stats.warnings++;
  }

  document.getElementById('stat-requests').textContent = state.stats.requests;
  document.getElementById('stat-warnings').textContent = state.stats.warnings;
  document.getElementById('stat-blocked').textContent = state.stats.blocked;
}

function addActivityItem(result) {
  const feed = document.getElementById('activity-feed');
  if (!feed) return;

  const risk = (result.blocked ? 'CRITICAL' : (result.loki?.risk || 'LOW')).toUpperCase();
  const icon = risk === 'CRITICAL' ? '🚫' : risk === 'HIGH' ? '⚠️' : risk === 'LOW' ? '✅' : 'ℹ️';
  let summary;
  if (result.blocked || risk === 'CRITICAL') {
    summary = 'Response blocked due to critical compliance findings.';
  } else if (risk === 'HIGH') {
    summary = 'High severity issues detected; manual review required.';
  } else if (risk === 'LOW') {
    summary = 'Validation passed with no major issues.';
  } else {
    summary = `Validation completed with outcome: ${risk}.`;
  }

  const item = document.createElement('div');
  item.className = 'activity-item';
  item.innerHTML = `
    <div class="activity-row">
      <span class="activity-risk" data-risk="${risk}">${icon} ${risk}</span>
      <span class="activity-time">${formatDateTime(new Date().toISOString())}</span>
    </div>
    <div class="meta">${escapeHtml(summary)}</div>
  `;

  feed.prepend(item);

  const emptyState = feed.querySelector('.empty-state');
  if (emptyState) emptyState.remove();
}

// showScreen removed (single dashboard view)

// Start app
init();

function switchTab(tabName) {
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.remove('active');
  });

  const targetPanel = document.getElementById(`${tabName}-tab`);
  if (targetPanel) targetPanel.classList.add('active');

  if (tabName === 'analytics') {
    loadAnalytics(state.analyticsWindow);
  }
}

async function validateDocument() {
  const text = document.getElementById('doc-text').value;

  if (!text.trim()) {
    alert('Please paste a document to validate');
    return;
  }

  const modules = getSelectedModules(true);

  if (modules.length === 0) {
    alert('Please select at least one validation module');
    return;
  }

  const validateBtn = document.getElementById('validate-btn');
  validateBtn.disabled = true;
  validateBtn.textContent = 'Checking...';

  try {
    const backendUrl = await getBackendUrl();
    const response = await fetch(`${backendUrl}/validate-document`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        modules: modules
      })
    });

    const result = await response.json();
    displayValidationResult(result);
    updateStatsFromValidation(result);

  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    validateBtn.disabled = false;
    validateBtn.textContent = 'Validate Document';
  }
}

function displayValidationResult(result) {
  const resultBox = document.getElementById('validation-result');
  const contentEl = document.getElementById('validation-content');

  resultBox.classList.remove('hidden', 'blocked', 'warning');

  const risk = result.risk;
  if (risk === 'CRITICAL') {
    resultBox.classList.add('blocked');
  } else if (risk === 'HIGH') {
    resultBox.classList.add('warning');
  }

  let html = `<h4>Risk Level: ${risk}</h4>`;

  // Show original document with inline highlighting
  const docText = document.getElementById('doc-text')?.value || '';
  if (docText && result.validation) {
    const highlighted = highlightViolations(docText, result.validation);
    const hasSpans = result.validation?.universal?.pii?.spans?.length > 0 ||
                     Object.values(result.validation?.modules || {}).some(m =>
                       Object.values(m.gates || {}).some(g => g.spans?.length > 0));

    if (hasSpans) {
      html += '<h4 style="margin-top: 1.5rem;">Document with Violations Highlighted</h4>';
      html += `<div class="response-text">${highlighted}</div>`;
      html += `
        <div class="highlight-legend" style="margin: 0.5rem 0 1rem; display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
          <span style="font-size: 0.85rem; color: var(--text-secondary);">Highlights:</span>
          <span><mark class="violation-highlight" style="background-color: #ef444420; color: #ef4444; border-bottom: 2px solid #ef4444;">Critical</mark></span>
          <span><mark class="violation-highlight" style="background-color: #f59e0b20; color: #f59e0b; border-bottom: 2px solid #f59e0b;">High</mark></span>
          <span><mark class="violation-highlight" style="background-color: #6366f120; color: #6366f1; border-bottom: 2px solid #6366f1;">Medium</mark></span>
        </div>
      `;
    }
  }

  // Universal checks
  if (result.validation && result.validation.universal) {
    html += '<h4>Universal Safety Checks</h4>';
    const u = result.validation.universal;
    if (u.pii) {
      html += `<div class="check-result ${u.pii.status === 'FAIL' ? 'fail' : 'pass'}">`;
      html += `<strong>PII Detection:</strong> ${u.pii.message}`;
      if (u.pii.findings && u.pii.findings.length > 0) {
        html += '<ul>';
        u.pii.findings.forEach(f => { html += `<li>${f.type}: ${f.count} instances (${f.severity} risk)</li>`; });
        html += '</ul>';
      }
      html += '</div>';
    }
    if (u.contradictions) {
      html += `<div class="check-result ${u.contradictions.status === 'FAIL' ? 'fail' : 'pass'}">`;
      html += `<strong>Contradictions:</strong> ${u.contradictions.message}`;
      if (u.contradictions.contradictions && u.contradictions.contradictions.length > 0) {
        html += '<ul>';
        u.contradictions.contradictions.forEach(c => { html += `<li>"${(c.sentence_1||'').slice(0,120)}" vs "${(c.sentence_2||'').slice(0,120)}"</li>`; });
        html += '</ul>';
      }
      html += '</div>';
    }
    if (u.hallucinations) {
      const warn = (u.hallucinations.status || '').toUpperCase() === 'WARNING';
      html += `<div class="check-result ${warn ? 'fail' : 'pass'}">`;
      html += `<strong>Hallucination Markers:</strong> ${u.hallucinations.message}`;
      if (u.hallucinations.markers && u.hallucinations.markers.length > 0) {
        html += '<ul>';
        u.hallucinations.markers.forEach(m => { html += `<li>${m}</li>`; });
        html += '</ul>';
      }
      html += '</div>';
    }
  }

  // Display gate results dynamically for ALL modules - SKIP N/A gates
  const modules = result.validation && result.validation.modules ? result.validation.modules : {};
  const moduleDisplayNames = {
    'hr_scottish': 'HR & Employment (Scottish Law)',
    'gdpr_uk': 'GDPR UK Compliance',
    'nda_uk': 'UK/EU NDA Compliance',
    'tax_uk': 'Tax & Financial (UK SME)',
    'fca_uk': 'FCA Financial Conduct'
  };

  for (const [moduleId, moduleData] of Object.entries(modules)) {
    if (!moduleData || !moduleData.gates) continue;

    const moduleName = moduleDisplayNames[moduleId] || moduleData.name || moduleId.replace(/_/g, ' ').toUpperCase();

    html += `<h4 style="margin-top: 1.5rem;">${moduleName}</h4>`;
    html += '<div class="gates-list">';

    for (const [gateName, gateResult] of Object.entries(moduleData.gates)) {
      if (gateResult.status === 'N/A') continue;
      const status = gateResult.status;
      const statusClass = status === 'FAIL' ? 'fail' : status === 'WARNING' ? 'warning' : status === 'PASS' ? 'pass' : '';
      const icon = status === 'FAIL' ? '❌' : status === 'WARNING' ? '⚠️' : status === 'PASS' ? '✅' : 'ℹ️';
      html += `
        <div class="gate-result ${statusClass}">
          <h4>${icon} ${gateName.replace(/_/g, ' ').toUpperCase()}</h4>
          <p>${gateResult.message || ''}</p>
          ${gateResult.details && Array.isArray(gateResult.details) ? `<ul>${gateResult.details.map(d => `<li>${escapeHtml(d)}</li>`).join('')}</ul>` : ''}
          ${gateResult.suggestion ? `<p><strong>Fix:</strong> ${gateResult.suggestion}</p>` : ''}
          ${gateResult.legal_source ? `<p><em>${gateResult.legal_source}</em></p>` : ''}
        </div>
      `;
    }
    html += '</div>';
  }
  // Cross-Module Issues
  const cross = result.validation?.cross || {};
  const crossIssues = Array.isArray(cross.issues) ? cross.issues : [];
  if (crossIssues.length) {
    html += '<h4 style="margin-top: 1rem;">Cross-Module Issues</h4>';
    crossIssues.forEach(issue => {
      const sev = (issue.severity || 'medium').toLowerCase();
      const cls = sev === 'critical' ? 'fail' : (sev === 'high' ? 'warning' : '');
      html += `
        <div class="gate-result ${cls}">
          <h4>${issue.id || 'cross_issue'} (${issue.severity || 'medium'})</h4>
          <p>${issue.message || ''}</p>
        </div>
      `;
    });
  }


  contentEl.innerHTML = html;
  resultBox.classList.remove('hidden');
}

// Dynamic modules rendering from backend
async function renderModulesUI() {
  try {
    let modules = Array.isArray(state.modules) && state.modules.length ? state.modules : [];
    if (!modules.length) {
      const backendUrl = await getBackendUrl();
      const res = await fetch(`${backendUrl}/modules`);
      const data = await res.json();
      modules = Array.isArray(data?.modules) ? data.modules : [];
      state.modules = modules;
    }

    if (!modules.length) return;

    const interceptEl = document.getElementById('modules-interceptor');
    const validatorEl = document.getElementById('modules-validator');
    const savedInterceptor = safeParse(localStorage.getItem('mods-interceptor'));
    const savedValidator = safeParse(localStorage.getItem('mods-validator'));

    if (interceptEl) {
      interceptEl.innerHTML = modules.map(mod => renderModuleChip(mod, savedInterceptor, false)).join('');
      attachModuleListeners(interceptEl);
    }

    if (validatorEl) {
      validatorEl.innerHTML = modules.map(mod => renderModuleChip(mod, savedValidator, true)).join('');
      attachModuleListeners(validatorEl);
    }

    persistSelectedModules();
  } catch (e) {
    console.warn('Failed to load module catalog', e);
  }
}

function renderModuleChip(module, savedList, forValidator) {
  const defaultSelected = ['hr_scottish', 'gdpr_uk'];
  const stored = Array.isArray(savedList) ? savedList : [];
  const isChecked = stored.length ? stored.includes(module.id) : defaultSelected.includes(module.id);
  const id = `${forValidator ? 'v-' : ''}mod-${module.id}`;
  const version = module.version || '1.0.0';
  const gates = module.gates != null ? module.gates : '—';

  return `
    <label class="module-chip ${isChecked ? 'active' : ''}">
      <input type="checkbox" id="${id}" data-mod value="${module.id}" ${isChecked ? 'checked' : ''}>
      <div class="module-chip__body">
        <span class="module-chip__title">${escapeHtml(module.name || module.id)}</span>
        <span class="module-chip__meta">${gates} gates · v${escapeHtml(version)}</span>
      </div>
    </label>
  `;
}

function attachModuleListeners(container) {
  if (!container) return;
  container.querySelectorAll('input[type="checkbox"][data-mod]').forEach(cb => {
    const label = cb.closest('.module-chip');
    if (label) label.classList.toggle('active', cb.checked);
    cb.addEventListener('change', () => {
      const lbl = cb.closest('.module-chip');
      if (lbl) lbl.classList.toggle('active', cb.checked);
      persistSelectedModules();
    });
  });
}

function safeParse(value) {
  try {
    const parsed = JSON.parse(value || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

function persistSelectedModules() {
  const mi = document.getElementById('modules-interceptor');
  const mv = document.getElementById('modules-validator');
  if (mi) {
    const sel = Array.from(mi.querySelectorAll('input[type="checkbox"][data-mod]:checked')).map(cb => cb.value);
    localStorage.setItem('mods-interceptor', JSON.stringify(sel));
  }
  if (mv) {
    const sel = Array.from(mv.querySelectorAll('input[type="checkbox"][data-mod]:checked')).map(cb => cb.value);
    localStorage.setItem('mods-validator', JSON.stringify(sel));
  }
}

function updateStatsFromValidation(result) {
  state.stats.requests++;

  if (result.risk === 'CRITICAL') {
    state.stats.blocked++;
  } else if (result.risk === 'HIGH') {
    state.stats.warnings++;
  }

  document.getElementById('stat-requests').textContent = state.stats.requests;
  document.getElementById('stat-warnings').textContent = state.stats.warnings;
  document.getElementById('stat-blocked').textContent = state.stats.blocked;
}

function initProviderUI() {
  onProviderChange();
}

function onProviderChange() {
  const provider = document.getElementById('provider-select')?.value || 'anthropic';
  state.provider = provider;
  const input = document.getElementById('api-key-input');
  if (!input) return;
  if (provider === 'anthropic') input.placeholder = 'sk-ant-...';
  else if (provider === 'openai') input.placeholder = 'sk-...';
  else if (provider === 'gemini') input.placeholder = 'AIzaSy...';
}

// Highlight violations from backend spans (universal + gates)
function highlightViolations(text, validation) {
  const source = text || '';
  const allSpans = [];

  try {
    const universal = validation?.universal || {};
    if (Array.isArray(universal.pii?.spans)) allSpans.push(...universal.pii.spans);
    if (Array.isArray(universal.contradictions?.spans)) allSpans.push(...universal.contradictions.spans);
  } catch {}

  try {
    const modules = validation?.modules || {};
    Object.keys(modules).forEach(mod => {
      const gates = modules[mod]?.gates || {};
      Object.keys(gates).forEach(g => {
        const spans = gates[g]?.spans || [];
        if (Array.isArray(spans) && spans.length) allSpans.push(...spans);
      });
    });
  } catch {}

  if (!allSpans.length) return escapeHtml(source);

  allSpans.sort((a, b) => a.start - b.start);

  let result = '';
  let last = 0;
  for (const span of allSpans) {
    const s = Math.max(0, span.start|0);
    const e = Math.max(s, span.end|0);
    if (s < last) continue; // skip overlapping regions already highlighted
    result += escapeHtml(source.substring(last, s));
    const color = span.severity === 'critical' ? '#ef4444' : span.severity === 'high' ? '#f59e0b' : '#6366f1';
    result += `<mark class="violation-highlight" style="background-color: ${color}20; color: ${color}; border-bottom: 2px solid ${color};" title="${escapeHtml(String(span.type||''))}">${escapeHtml(source.substring(s, e))}</mark>`;
    last = e;
  }
  result += escapeHtml(source.substring(last));
  return result;
}
