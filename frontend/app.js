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

// Toggle deterministic synthesis for document validation
const ENABLE_CORRECTIONS = true;
const DEFAULT_SYNTHESIS_CONTEXT = {
  firm_name: 'Highland AI',
  contact_details: 'compliance@highland-ai.com',
  url: 'https://highland-ai.com/privacy',
  dpo_email: 'dpo@highland-ai.com'
};
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
  document.getElementById('aggregate-btn')?.addEventListener('click', handleAggregateValidation);
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

  const provider = state.provider || 'anthropic';

  const summaryEl = document.getElementById('aggregation-summary');
  if (summaryEl) {
    summaryEl.style.display = 'none';
    summaryEl.innerHTML = '';
  }

  if (btn) { btn.disabled = true; btn.textContent = 'Validating…'; }
  try {
    let payload;
    if (provider === 'anthropic') {
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
    } else {
      const headers = { 'Content-Type': 'application/json' };
      if (provider === 'openai') {
        headers['openai-api-key'] = apiKey;
        headers['x-api-key'] = apiKey;
      } else if (provider === 'gemini') {
        headers['gemini-api-key'] = apiKey;
      }

      const body = provider === 'openai'
        ? {
            provider,
            modules,
            model: 'gpt-5-mini',
            max_tokens: 900,
            messages: [{ role: 'user', content: prompt }]
          }
        : {
            provider,
            modules,
            model: 'gemini-2.5-flash',
            prompt
          };

      const res = await fetch(`${API_BASE}/proxy`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body)
      });
      payload = await res.json();
    }

    displayPromptResult(payload);
    const computedRisk = deriveRisk(payload);
    recordMetrics(computedRisk);
    pushActivity(computedRisk, 'Prompt validation executed');
    showToast('Validation completed successfully.', 'success', 'Validation Complete');
  } catch (error) {
    showToast('Validation failed: ' + (error?.message || error), 'error', 'Validation Failed');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Send & Validate'; }
  }
}

async function handleAggregateValidation() {
  const prompt = document.getElementById('test-prompt')?.value.trim();
  const btn = document.getElementById('aggregate-btn');
  if (!prompt) {
    showToast('Please enter a prompt to validate.', 'warning', 'Missing Prompt');
    return;
  }

  const modules = getSelectedModules('mods-interceptor');
  if (!modules.length) {
    showToast('Please select at least one FCA validation module.', 'warning', 'No Modules Selected');
    return;
  }

  const providerSpecs = ['anthropic', 'openai', 'gemini'].map(name => {
    const stored = state.apiKeys[name];
    const inlineKey = name === state.provider ? document.getElementById('api-key-input')?.value.trim() : '';
    const apiKey = stored || inlineKey || '';
    if (!apiKey) return null;
    return {
      name,
      api_key: apiKey
    };
  }).filter(Boolean);

  if (!providerSpecs.length) {
    showToast('Please configure at least one provider API key before aggregating.', 'error', 'Missing API Keys');
    return;
  }

  if (btn) { btn.disabled = true; btn.textContent = 'Aggregating…'; }
  try {
    const res = await fetch(`${API_BASE}/aggregate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        modules,
        providers: providerSpecs
      })
    });
    const payload = await res.json();
    if (!res.ok) {
      throw new Error(payload?.message || payload?.error || `HTTP ${res.status}`);
    }
    displayAggregationResult(payload);
    const selectedRisk = deriveRisk(payload?.selected);
    recordMetrics(selectedRisk);
    pushActivity(selectedRisk, 'Aggregated prompt validation completed');
    showToast('Aggregated validation completed successfully.', 'success', 'Aggregation Complete');

    // Auto-generate System Draft if there are failures
    if (selectedRisk === 'CRITICAL' || selectedRisk === 'HIGH') {
      await generateSystemDraft(payload);
    }
  } catch (error) {
    showToast('Aggregation failed: ' + (error?.message || error), 'error', 'Aggregation Failed');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Aggregate Providers'; }
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
      state.lastValidation = { text, result: payload, modules };
    }

    displayDocumentResult(payload);
    const docRisk = deriveRisk(payload);
    recordMetrics(docRisk);
    pushActivity(docRisk, 'Document validation completed');
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
  const validation = result.loki?.validation || result.validation || result.loki_validation || {};
  const risk = deriveRisk(result);
  wrapper.classList.remove('result--hidden', 'blocked', 'warning');
  if (risk === 'CRITICAL') wrapper.classList.add('blocked');
  else if (risk === 'HIGH') wrapper.classList.add('warning');

  body.innerHTML = `
    ${renderResponseText(result)}
    ${renderModuleBlocks(validation.modules)}
    ${renderCrossFindings(validation.cross)}
  `;
}

function displayAggregationResult(result) {
  if (!result) return;
  const selected = result.selected;
  const selectionMeta = result.selection || {};
  const allRefused = Boolean(result.all_refused);

  if (selected) {
    const synthetic = {
      response: {
        content: [{ type: 'text', text: selected.response_text }]
      },
      loki: {
        risk: selected.risk,
        validation: selected.validation || {}
      }
    };
    displayPromptResult(synthetic);
  } else if (allRefused) {
    const wrapper = document.getElementById('test-result');
    const body = document.getElementById('result-content');
    if (wrapper && body) {
      wrapper.classList.remove('result--hidden', 'blocked', 'warning');
      body.innerHTML = `
        <section class="section">
          <h3>Provider Responses</h3>
          <div class="gate-result warning">
            <strong>All providers refused</strong>
            <div>The selected models declined to generate this content. Revise the prompt to request compliant marketing material.</div>
          </div>
        </section>
      `;
    }
  }

  const summaryEl = document.getElementById('aggregation-summary');
  if (!summaryEl) return;

  const providers = Array.isArray(result.providers) ? result.providers : [];
  if (!providers.length) {
    summaryEl.style.display = 'none';
    summaryEl.innerHTML = '';
    return;
  }

  summaryEl.style.display = 'block';
  const selectedName = selected?.provider;
  const rows = providers.map(provider => {
    const statusLabel = provider.blocked ? 'BLOCKED' : (provider.error ? provider.error : '');
    const refusalLabel = provider.is_refusal ? 'REFUSAL' : '';
    const previewSource = provider.response_text || provider.error || '';
    const preview = previewSource.slice(0, 120);
    const hasDetails = Boolean(provider.response_text) || Boolean(provider.error);
    const fullResponse = hasDetails ? `
      <details class="aggregation-summary__details ${provider.blocked ? 'aggregation-summary__details--blocked' : ''}">
        <summary>${provider.blocked ? 'View error details' : 'View response'}</summary>
        <pre>${escapeHtml(provider.response_text || provider.error || 'No response returned')}</pre>
      </details>
    ` : '';
    return `
      <div class=\"aggregation-summary__provider\">
        <strong>${escapeHtml(provider.provider || 'unknown')}</strong>
        <span class=\"aggregation-summary__badge\" data-risk=\"${escapeHtml(provider.risk || 'LOW')}\">
          ${escapeHtml(provider.risk || 'LOW')}
        </span>
        <span>Fail: ${Number(provider.failures || 0)}</span>
        <span>Warn: ${Number(provider.warnings || 0)}</span>
        <span class=\"aggregation-summary__status\">${escapeHtml(statusLabel)}</span>
        ${refusalLabel ? `<span class="aggregation-summary__status aggregation-summary__status--refusal">${escapeHtml(refusalLabel)}</span>` : ''}
        <span class=\"aggregation-summary__preview\">${escapeHtml(preview)}</span>
        ${fullResponse}
      </div>
    `;
  }).join('');

  summaryEl.innerHTML = `
    <div class=\"aggregation-summary__header\">
      <strong>Provider comparison</strong>
      <span>Selected: ${selectedName ? selectedName.toUpperCase() : (allRefused ? 'NONE (REFUSED)' : '—')}</span>
    </div>
    ${selectionMeta.used_blocked_provider ? `<div class="aggregation-summary__notice">Primary provider refused. Using ${escapeHtml(selectedName || 'alternate')} output with deterministic compliance sanitisation.</div>` : ''}
    ${allRefused ? '<div class="aggregation-summary__notice aggregation-summary__notice--error">All providers refused to produce content for this prompt.</div>' : ''}
    ${rows}
  `;
}

async function generateSystemDraft(aggregatorResult) {
  const draftContainer = document.getElementById('system-draft-container');
  if (!draftContainer) return;

  if (aggregatorResult?.all_refused) {
    draftContainer.style.display = 'block';
    draftContainer.innerHTML = `
      <p class="empty" style="color: #ef4444;">
        All providers refused to generate content for this prompt. Revise the prompt and try again.
      </p>
    `;
    return;
  }

  draftContainer.style.display = 'block';
  draftContainer.innerHTML = '<p class="empty">Generating compliant system draft...</p>';

  try {
    const res = await fetch(`${API_BASE}/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        aggregator_result: aggregatorResult,
        context: DEFAULT_SYNTHESIS_CONTEXT
      })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const synthesisResult = await res.json();
    synthesisResult.selection = aggregatorResult?.selection || {};
    synthesisResult.selected_provider = aggregatorResult?.selected?.provider;
    synthesisResult.selected_blocked = aggregatorResult?.selected?.blocked;
    displaySystemDraft(synthesisResult);
    showToast('System draft generated successfully', 'success', 'Draft Generated');
  } catch (error) {
    draftContainer.innerHTML = `<p class="empty" style="color: #ef4444;">Failed to generate draft: ${escapeHtml(error.message)}</p>`;
    showToast('Failed to generate system draft: ' + (error?.message || error), 'error', 'Draft Generation Failed');
  }
}

function displaySystemDraft(synthesisResult) {
  const draftContainer = document.getElementById('system-draft-container');
  if (!draftContainer) return;

  const success = synthesisResult.success;
  const finalRisk = synthesisResult.final_validation?.overall_risk || 'UNKNOWN';
  const snippetsApplied = synthesisResult.snippets_applied || [];
  const synthesizedText = synthesisResult.synthesized_text || '';
  const originalText = synthesisResult.original_text || '';
  const iterations = synthesisResult.iterations || 0;
  const selection = synthesisResult.selection || {};
  const selectedProvider = synthesisResult.selected_provider || 'unknown';
  const usedBlockedProvider = Boolean(synthesisResult.selected_blocked);
  const sanitization = synthesisResult.sanitization || {};
  const sanitizationActions = Array.isArray(sanitization.actions) ? sanitization.actions : [];

  const statusBadge = success
    ? '<span style="color: #10b981; font-weight: 600;">✓ ALL GATES PASSED</span>'
    : '<span style="color: #ef4444; font-weight: 600;">⚠ SOME FAILURES REMAIN</span>';

  const providerNotice = selection?.reason === 'non_refusal_selected' && (selection.fallback_from_refusal || usedBlockedProvider)
    ? `
        <div class="validation-synthesis__notice">
          <strong>Notice:</strong> Primary provider response was unavailable. Using ${escapeHtml(selectedProvider.toUpperCase())}'s draft with deterministic compliance sanitisation.
        </div>
      `
    : '';

  const failingGates = [];
  const modules = synthesisResult.final_validation?.modules || {};
  Object.entries(modules).forEach(([moduleId, modulePayload]) => {
    const gates = modulePayload?.gates || {};
    Object.entries(gates).forEach(([gateId, gate]) => {
      if ((gate?.status || '').toUpperCase() === 'FAIL') {
        failingGates.push({
          module: moduleId,
          gate: gateId,
          message: gate?.message || '',
          severity: (gate?.severity || '').toUpperCase()
        });
      }
    });
  });

  const needsReviewBlock = !success && failingGates.length ? `
    <div class="validation-synthesis__needs-review">
      <h4>Manual Review Required</h4>
      <p>The following gates still require attention:</p>
      <ul>
        ${failingGates.slice(0, 10).map(gate => `
          <li>
            <strong>${escapeHtml(gate.module)}:${escapeHtml(gate.gate)}</strong>
            <span class="needs-review__severity needs-review__severity--${escapeHtml(gate.severity || 'medium').toLowerCase()}">${escapeHtml(gate.severity || 'MEDIUM')}</span>
            <div>${escapeHtml(gate.message || 'Issue detected')}</div>
          </li>
        `).join('')}
      </ul>
      ${failingGates.length > 10 ? '<p class="needs-review__more">Additional failures not shown. See full validation report.</p>' : ''}
    </div>
  ` : '';

  const comparisonBlock = `
    <div class="system-draft__comparison">
      ${
        originalText
          ? `
            <details class="system-draft__details">
              <summary>View Original Text</summary>
              <pre>${escapeHtml(originalText)}</pre>
            </details>
          `
          : ''
      }
      <details class="system-draft__details" open>
        <summary>View Synthesized Text</summary>
        <pre>${escapeHtml(synthesizedText)}</pre>
      </details>
      <div class="system-draft__actions">
        <button id="copy-draft-btn" class="btn btn--secondary">Copy Synthesized Draft</button>
      </div>
    </div>
  `;

  const snippetsHtml = snippetsApplied.length > 0
    ? `
      <div style="margin-top: 1rem;">
        <h4 style="margin-bottom: 0.5rem; color: #475569;">Compliance Snippets Applied:</h4>
        <div class="system-draft__snippet-list">
          ${snippetsApplied.map((snippet, idx) => `
            <details class="system-draft__snippet"${snippetsApplied.length === 1 ? ' open' : ''}>
              <summary>
                <div class="system-draft__snippet-head">
                  <div>
                    <strong>${escapeHtml(snippet.module_id)}:${escapeHtml(snippet.gate_id)}</strong>
                    <span class="system-draft__severity">${escapeHtml(snippet.severity)}</span>
                  </div>
                  <div class="system-draft__snippet-meta">
                    <span>Iteration ${snippet.iteration || 1}</span>
                    <span>#${snippet.order || idx + 1}</span>
                  </div>
                </div>
                <div class="system-draft__snippet-sub">
                  Insertion: ${escapeHtml(snippet.insertion_point)}${snippet.section_header ? ` · ${escapeHtml(snippet.section_header)}` : ''}
                </div>
              </summary>
              ${
                snippet.text_added
                  ? `<pre class="system-draft__snippet-text">${escapeHtml(snippet.text_added)}</pre>`
                  : '<p class="system-draft__snippet-text system-draft__snippet-text--empty">Snippet applied without text payload.</p>'
              }
            </details>
          `).join('')}
        </div>
      </div>
    `
    : '<p style="color: #64748b; margin-top: 1rem;">No compliance snippets were needed.</p>';

  draftContainer.innerHTML = `
    <div style="background: white; border: 2px solid ${success ? '#10b981' : '#f59e0b'}; border-radius: 0.5rem; padding: 1.5rem; margin-bottom: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 style="margin: 0; color: #1e293b;">System Draft (Deterministic Synthesis)</h3>
        ${statusBadge}
      </div>
      <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 1rem;">
        Final Risk: <strong style="color: ${finalRisk === 'LOW' ? '#10b981' : finalRisk === 'HIGH' ? '#f59e0b' : '#ef4444'};">${escapeHtml(finalRisk)}</strong>
        • Iterations: ${iterations}
        • Snippets: ${snippetsApplied.length}
      </div>
      ${providerNotice}
      ${comparisonBlock}

      ${snippetsHtml}

      ${sanitizationActions.length ? `
        <div class="validation-synthesis__notice">
          <strong>Sanitisation applied:</strong>
          <ul>
            ${sanitizationActions.slice(0, 5).map(action => `
              <li>${escapeHtml(action.replacement || 'Updated text')} <span class="needs-review__severity needs-review__severity--medium">${escapeHtml(String(action.count || 1))}×</span></li>
            `).join('')}
          </ul>
          ${sanitizationActions.length > 5 ? '<p class="needs-review__more">Additional sanitisation actions applied.</p>' : ''}
        </div>
      ` : ''}

      ${needsReviewBlock}

      <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; font-size: 0.875rem; color: #64748b; font-style: italic;">
        Note: This draft was generated using deterministic compliance snippets. No AI was used in the synthesis process.
        ${success ? 'All compliance gates have been satisfied.' : 'Manual review is recommended for remaining issues.'}
      </div>
    </div>
  `;

  // Bind copy button
  document.getElementById('copy-draft-btn')?.addEventListener('click', () => {
    navigator.clipboard.writeText(synthesizedText);
    showToast('Draft copied to clipboard', 'success', 'Copied');
  });
}

function displayDocumentResult(result) {
  const wrapper = document.getElementById('validation-result');
  const body = document.getElementById('validation-content');
  if (!wrapper || !body) return;
  const risk = deriveRisk(result);
  wrapper.classList.remove('result--hidden', 'blocked', 'warning');
  if (risk === 'CRITICAL') wrapper.classList.add('blocked');
  else if (risk === 'HIGH') wrapper.classList.add('warning');

  // Deterministic corrections available when failures detected
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
    const rendered = Object.entries(gates).map(([gateId, gate]) => renderGateResult(gateId, gate)).join('');
    return `
      <section class="section">
        <h3>${escapeHtml(title)}</h3>
        ${rendered || '<p class="empty">No findings for this module.</p>'}
      </section>
    `;
  }).join('');
}

function renderGateResult(gateId, gate = {}) {
  const status = (gate.status || 'N/A').toUpperCase();
  const severity = (gate.severity || '').toUpperCase();
  const css = status === 'FAIL' ? 'fail' : status === 'WARNING' ? 'warning' : status === 'PASS' ? 'pass' : '';
  const label = gate.name || gateId.replace(/_/g, ' ');
  const suggestion = gate.suggestion ? `<div class="gate-source">Suggested fix: ${escapeHtml(gate.suggestion)}</div>` : '';
  const source = gate.legal_source ? `<div class="gate-source">${escapeHtml(gate.legal_source)}</div>` : '';
  const message = gate.message || (status === 'N/A' ? 'Not applicable' : '');
  return `
    <div class="gate-result ${css}">
      <strong>${escapeHtml(label)} — ${status}${severity && status !== 'PASS' ? ` (${severity})` : ''}</strong>
      <div>${escapeHtml(message)}</div>
      ${source}
      ${suggestion}
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
    if (typeof result.response?.text === 'string') {
      return result.response.text;
    }
    if (Array.isArray(result.choices)) {
      const combined = result.choices
        .map(choice => choice?.message?.content || '')
        .filter(Boolean)
        .join('\n\n');
      if (combined) return combined;
    }
    if (typeof result.output_text === 'string') {
      return result.output_text;
    }
    return '';
  } catch {
    return '';
  }
}

function getSelectedModules(storageKey) {
  const stored = storage.get(storageKey, []);
  return stored.length ? stored : state.modules.map(m => m.id);
}

function deriveRisk(result) {
  if (!result) return 'LOW';
  const direct = result.loki?.risk || result.risk;
  if (direct) return String(direct).toUpperCase();
  const validation = result.loki?.validation || result.validation || result.loki_validation;
  if (validation && typeof validation === 'object' && validation.overall_risk) {
    return String(validation.overall_risk).toUpperCase();
  }
  return 'LOW';
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
    const res = await fetch(`${API_BASE}/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_text: state.lastValidation.text,
        validation: state.lastValidation.result.validation,
        context: DEFAULT_SYNTHESIS_CONTEXT,
        modules: state.lastValidation.modules
      })
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    }

    const synthesisResult = await res.json();
    state.lastValidation.synthesis = synthesisResult;
    displayValidationSynthesis(synthesisResult);
    showToast('Deterministic draft generated', 'success', 'Corrections Complete');
  } catch (error) {
    console.error('Correction error:', error);
    showToast('Correction failed: ' + (error?.message || error), 'error', 'Correction Failed');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'Apply Auto-Corrections'; }
  }
}

function displayValidationSynthesis(synthesisResult) {
  const body = document.getElementById('validation-content');
  if (!body) return;

  const original = state.lastValidation.text || '';
  const synthesized = synthesisResult.synthesized_text || '';
  const success = synthesisResult.success;
  const finalRisk = synthesisResult.final_validation?.overall_risk || 'UNKNOWN';
  const snippets = synthesisResult.snippets_applied || [];
  const iterations = synthesisResult.iterations || 0;

  body.innerHTML = `
    <div class="validation-synthesis">
      <div class="validation-synthesis__header">
        <h3>Deterministic Compliance Draft</h3>
        <div class="validation-synthesis__status">
          <span class="validation-synthesis__risk">Final Risk: ${escapeHtml(finalRisk)}</span>
          <span>Iterations: ${iterations}</span>
          <span>Snippets: ${snippets.length}</span>
          <span class="${success ? 'validation-synthesis__badge--pass' : 'validation-synthesis__badge--warn'}">
            ${success ? '✓ All gates passed' : '⚠ Further review required'}
          </span>
        </div>
      </div>

      <div class="validation-synthesis__columns">
        <div>
          <h4 class="validation-synthesis__title validation-synthesis__title--original">Original Document</h4>
          <div class="validation-synthesis__text validation-synthesis__text--original">
            ${escapeHtml(original)}
          </div>
        </div>
        <div>
          <h4 class="validation-synthesis__title validation-synthesis__title--synth">Synthesized Draft</h4>
          <div class="validation-synthesis__text validation-synthesis__text--synth">
            ${escapeHtml(synthesized)}
          </div>
          <div class="validation-synthesis__actions">
            <button id="copy-corrected-btn" class="btn btn--secondary">Copy Synthesized Draft</button>
          </div>
        </div>
      </div>

      <div class="validation-synthesis__snippets">
        <h4>Compliance Snippets Applied</h4>
        ${snippets.length ? `
          <div class="system-draft__snippet-list">
            ${snippets.map((snippet, idx) => `
              <details class="system-draft__snippet"${snippets.length === 1 ? ' open' : ''}>
                <summary>
                  <div class="system-draft__snippet-head">
                    <div>
                      <strong>${escapeHtml(snippet.module_id)}:${escapeHtml(snippet.gate_id)}</strong>
                      <span class="system-draft__severity">${escapeHtml(snippet.severity)}</span>
                    </div>
                    <div class="system-draft__snippet-meta">
                      <span>Iteration ${snippet.iteration || 1}</span>
                      <span>#${snippet.order || idx + 1}</span>
                    </div>
                  </div>
                  <div class="system-draft__snippet-sub">
                    Insertion: ${escapeHtml(snippet.insertion_point)}${snippet.section_header ? ` · ${escapeHtml(snippet.section_header)}` : ''}
                  </div>
                </summary>
                ${
                  snippet.text_added
                    ? `<pre class="system-draft__snippet-text">${escapeHtml(snippet.text_added)}</pre>`
                    : '<p class="system-draft__snippet-text system-draft__snippet-text--empty">Snippet applied without text payload.</p>'
                }
              </details>
            `).join('')}
          </div>
        ` : '<p class="validation-synthesis__empty">No snippets were required for this draft.</p>'}
      </div>

      <div class="validation-synthesis__footer">
        <button id="back-to-validation-btn" class="btn btn--secondary">Back to Validation Results</button>
      </div>
    </div>
  `;

  // Bind buttons
  document.getElementById('copy-corrected-btn')?.addEventListener('click', () => {
    navigator.clipboard.writeText(synthesized);
    showToast('Synthesized draft copied to clipboard', 'success', 'Copied');
  });

  document.getElementById('back-to-validation-btn')?.addEventListener('click', () => {
    displayDocumentResult(state.lastValidation.result);
  });
}

window.addEventListener('DOMContentLoaded', init);
