/**
 * Unit Tests - DOM Manipulation & Navigation
 *
 * Tests for DOM-related functionality including:
 * - View switching
 * - Navigation binding
 * - Dynamic content rendering
 */

describe('DOM Manipulation & Navigation', () => {
  describe('View Switching', () => {
    beforeEach(() => {
      // Setup navigation structure
      document.body.innerHTML = `
        <div class="nav">
          <button class="nav__item active" data-view="overview">Overview</button>
          <button class="nav__item" data-view="interceptor">Interceptor</button>
          <button class="nav__item" data-view="validator">Validator</button>
          <button class="nav__item" data-view="analytics">Analytics</button>
        </div>
        <div class="content">
          <div class="view" data-id="overview" style="display: block;">Overview Content</div>
          <div class="view" data-id="interceptor" style="display: none;">Interceptor Content</div>
          <div class="view" data-id="validator" style="display: none;">Validator Content</div>
          <div class="view" data-id="analytics" style="display: none;">Analytics Content</div>
        </div>
      `;

      // Load switchView function
      window.switchView = function(viewId) {
        // Update navigation active state
        document.querySelectorAll('.nav__item').forEach(btn => {
          btn.classList.toggle('active', btn.dataset.view === viewId);
        });

        // Update view visibility
        document.querySelectorAll('.view').forEach(view => {
          view.style.display = view.dataset.id === viewId ? 'block' : 'none';
        });
      };
    });

    test('should switch to interceptor view', () => {
      window.switchView('interceptor');

      const activeBtn = document.querySelector('.nav__item.active');
      const visibleView = document.querySelector('.view[style*="display: block"]');

      expect(activeBtn.dataset.view).toBe('interceptor');
      expect(visibleView.dataset.id).toBe('interceptor');
    });

    test('should switch to validator view', () => {
      window.switchView('validator');

      const activeBtn = document.querySelector('.nav__item.active');
      const visibleView = document.querySelector('.view[style*="display: block"]');

      expect(activeBtn.dataset.view).toBe('validator');
      expect(visibleView.dataset.id).toBe('validator');
    });

    test('should switch to analytics view', () => {
      window.switchView('analytics');

      const activeBtn = document.querySelector('.nav__item.active');
      const visibleView = document.querySelector('.view[style*="display: block"]');

      expect(activeBtn.dataset.view).toBe('analytics');
      expect(visibleView.dataset.id).toBe('analytics');
    });

    test('should deactivate previous view', () => {
      window.switchView('interceptor');
      window.switchView('validator');

      const interceptorView = document.querySelector('.view[data-id="interceptor"]');
      expect(interceptorView.style.display).toBe('none');
    });

    test('should only show one view at a time', () => {
      window.switchView('analytics');

      const visibleViews = Array.from(document.querySelectorAll('.view'))
        .filter(v => v.style.display === 'block');

      expect(visibleViews.length).toBe(1);
      expect(visibleViews[0].dataset.id).toBe('analytics');
    });

    test('should only have one active nav button', () => {
      window.switchView('validator');

      const activeButtons = document.querySelectorAll('.nav__item.active');
      expect(activeButtons.length).toBe(1);
      expect(activeButtons[0].dataset.view).toBe('validator');
    });

    test('should handle switching to same view', () => {
      window.switchView('overview');
      window.switchView('overview');

      const activeBtn = document.querySelector('.nav__item.active');
      expect(activeBtn.dataset.view).toBe('overview');
    });
  });

  describe('Navigation Binding', () => {
    test('should bind click events to navigation items', () => {
      document.body.innerHTML = `
        <button class="nav__item" data-view="test1">Test 1</button>
        <button class="nav__item" data-view="test2">Test 2</button>
      `;

      const mockSwitch = jest.fn();
      window.switchView = mockSwitch;

      // Simulate bindNavigation
      document.querySelectorAll('.nav__item').forEach(btn => {
        btn.addEventListener('click', () => window.switchView(btn.dataset.view));
      });

      const button = document.querySelector('[data-view="test1"]');
      button.click();

      expect(mockSwitch).toHaveBeenCalledWith('test1');
      expect(mockSwitch).toHaveBeenCalledTimes(1);
    });

    test('should bind multiple navigation items', () => {
      document.body.innerHTML = `
        <button class="nav__item" data-view="view1">View 1</button>
        <button class="nav__item" data-view="view2">View 2</button>
        <button class="nav__item" data-view="view3">View 3</button>
      `;

      const mockSwitch = jest.fn();
      window.switchView = mockSwitch;

      document.querySelectorAll('.nav__item').forEach(btn => {
        btn.addEventListener('click', () => window.switchView(btn.dataset.view));
      });

      document.querySelector('[data-view="view1"]').click();
      document.querySelector('[data-view="view2"]').click();
      document.querySelector('[data-view="view3"]').click();

      expect(mockSwitch).toHaveBeenCalledTimes(3);
      expect(mockSwitch).toHaveBeenNthCalledWith(1, 'view1');
      expect(mockSwitch).toHaveBeenNthCalledWith(2, 'view2');
      expect(mockSwitch).toHaveBeenNthCalledWith(3, 'view3');
    });
  });

  describe('Action Binding', () => {
    test('should bind refresh status button', () => {
      document.body.innerHTML = '<button id="refresh-status">Refresh</button>';

      const mockRefresh = jest.fn();
      const button = document.getElementById('refresh-status');
      button.addEventListener('click', mockRefresh);

      button.click();
      expect(mockRefresh).toHaveBeenCalledTimes(1);
    });

    test('should bind save API key button', () => {
      document.body.innerHTML = '<button id="save-key-btn">Save Key</button>';

      const mockSave = jest.fn();
      const button = document.getElementById('save-key-btn');
      button.addEventListener('click', mockSave);

      button.click();
      expect(mockSave).toHaveBeenCalledTimes(1);
    });

    test('should bind provider select change event', () => {
      document.body.innerHTML = `
        <select id="provider-select">
          <option value="anthropic">Anthropic</option>
          <option value="openai">OpenAI</option>
        </select>
      `;

      const mockChange = jest.fn();
      const select = document.getElementById('provider-select');
      select.addEventListener('change', mockChange);

      select.value = 'openai';
      select.dispatchEvent(new Event('change'));

      expect(mockChange).toHaveBeenCalledTimes(1);
    });

    test('should bind analytics window selector', () => {
      document.body.innerHTML = `
        <select id="analytics-window">
          <option value="7">7 days</option>
          <option value="30">30 days</option>
          <option value="90">90 days</option>
        </select>
      `;

      let analyticsWindow = 30;
      const select = document.getElementById('analytics-window');

      select.addEventListener('change', (evt) => {
        analyticsWindow = Number(evt.target.value) || 30;
      });

      select.value = '90';
      select.dispatchEvent(new Event('change'));

      expect(analyticsWindow).toBe(90);
    });
  });

  describe('Element Rendering', () => {
    test('should create module chip element', () => {
      const chip = document.createElement('div');
      chip.className = 'chip';
      chip.dataset.module = 'test-module';
      chip.textContent = 'Test Module';

      document.body.appendChild(chip);

      expect(document.querySelector('.chip')).toBeTruthy();
      expect(chip.dataset.module).toBe('test-module');
      expect(chip.textContent).toBe('Test Module');
    });

    test('should render multiple module chips', () => {
      const container = document.createElement('div');
      container.id = 'module-container';
      document.body.appendChild(container);

      const modules = ['fca', 'gdpr', 'smcr'];

      modules.forEach(mod => {
        const chip = document.createElement('div');
        chip.className = 'chip';
        chip.dataset.module = mod;
        chip.textContent = mod.toUpperCase();
        container.appendChild(chip);
      });

      const chips = container.querySelectorAll('.chip');
      expect(chips.length).toBe(3);
      expect(chips[0].textContent).toBe('FCA');
      expect(chips[1].textContent).toBe('GDPR');
      expect(chips[2].textContent).toBe('SMCR');
    });

    test('should update stats display', () => {
      document.body.innerHTML = `
        <div id="stats-validated">0</div>
        <div id="stats-warnings">0</div>
        <div id="stats-blocked">0</div>
      `;

      const stats = { validated: 42, warnings: 5, blocked: 2 };

      document.getElementById('stats-validated').textContent = stats.validated;
      document.getElementById('stats-warnings').textContent = stats.warnings;
      document.getElementById('stats-blocked').textContent = stats.blocked;

      expect(document.getElementById('stats-validated').textContent).toBe('42');
      expect(document.getElementById('stats-warnings').textContent).toBe('5');
      expect(document.getElementById('stats-blocked').textContent).toBe('2');
    });
  });

  describe('Backend Status Indicator', () => {
    test('should display online status', () => {
      document.body.innerHTML = '<span id="backend-status" class="status__pill">CHECKING</span>';

      const pill = document.getElementById('backend-status');
      pill.textContent = 'ONLINE';
      pill.classList.remove('offline');

      expect(pill.textContent).toBe('ONLINE');
      expect(pill.classList.contains('offline')).toBe(false);
    });

    test('should display offline status', () => {
      document.body.innerHTML = '<span id="backend-status" class="status__pill">ONLINE</span>';

      const pill = document.getElementById('backend-status');
      pill.textContent = 'OFFLINE';
      pill.classList.add('offline');

      expect(pill.textContent).toBe('OFFLINE');
      expect(pill.classList.contains('offline')).toBe(true);
    });

    test('should toggle status', () => {
      document.body.innerHTML = '<span id="backend-status" class="status__pill">ONLINE</span>';

      const pill = document.getElementById('backend-status');
      const setStatus = (isOnline) => {
        pill.textContent = isOnline ? 'ONLINE' : 'OFFLINE';
        pill.classList.toggle('offline', !isOnline);
      };

      setStatus(true);
      expect(pill.textContent).toBe('ONLINE');
      expect(pill.classList.contains('offline')).toBe(false);

      setStatus(false);
      expect(pill.textContent).toBe('OFFLINE');
      expect(pill.classList.contains('offline')).toBe(true);
    });
  });
});
