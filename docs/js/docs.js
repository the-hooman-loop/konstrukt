/* Konstrukt docs — shared chrome, theme switcher, and live token rendering. */
(function () {
  const NAV = [
    ['index.html', 'Overview'],
    ['tokens.html', 'Tokens'],
    ['typography.html', 'Typography'],
    ['components.html', 'Components'],
    ['text.html', 'Text'],
    ['ios.html', 'iOS'],
  ];

  function currentPage() {
    const path = location.pathname.split('/').pop();
    return path === '' ? 'index.html' : path;
  }

  function renderTopbar() {
    const here = currentPage();
    const links = NAV.map(
      ([href, label]) =>
        `<li><a href="${href}"${href === here ? ' class="active"' : ''}>${label}</a></li>`
    ).join('');
    const bar = document.createElement('header');
    bar.className = 'docs-topbar';
    bar.innerHTML = `
      <a class="brand" href="index.html">Konstrukt</a>
      <nav><ul class="docs-nav">${links}</ul></nav>
      <div class="docs-controls">
        <select id="palette-select" aria-label="Palette">
          <option value="atelier">Atelier</option>
          <option value="courage">Courage</option>
          <option value="minimal">Minimal</option>
          <option value="hl">The Hooman Loop</option>
          <option value="blueprint">Blueprint</option>
        </select>
        <button id="mode-toggle" aria-label="Toggle light/dark">Mode</button>
      </div>`;
    document.body.prepend(bar);

    const sel = bar.querySelector('#palette-select');
    const toggle = bar.querySelector('#mode-toggle');
    const theme = window.HLTheme;
    if (theme) {
      sel.value = theme.currentPalette();
      sel.addEventListener('change', () => {
        theme.setPalette(sel.value);
        document.dispatchEvent(new CustomEvent('konstrukt:themechange'));
      });
      toggle.addEventListener('click', () => {
        theme.toggleMode();
        document.dispatchEvent(new CustomEvent('konstrukt:themechange'));
      });
    }
  }

  let manifestPromise;
  function loadManifest() {
    if (!manifestPromise) {
      manifestPromise = fetch('assets/tokens.json').then((r) => r.json());
    }
    return manifestPromise;
  }

  function activeThemeKey() {
    const theme = window.HLTheme;
    const palette = theme ? theme.currentPalette() : 'atelier';
    const mode = theme ? theme.currentMode() : 'light';
    return `${palette}.${mode}`;
  }

  async function renderSwatches(containerId, filter) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const manifest = await loadManifest();
    const draw = () => {
      const tokens = manifest.themes[activeThemeKey()] || manifest.themes['atelier.light'];
      el.innerHTML = Object.entries(tokens)
        .filter(([name, t]) => t.type === 'color' && filter(name))
        .map(
          ([name, t]) => `
            <div class="swatch">
              <div class="swatch-chip" style="background:${t.value}"></div>
              <span class="swatch-name">--${name}</span>
              <span class="swatch-value">${t.value}</span>
            </div>`
        )
        .join('');
    };
    draw();
    document.addEventListener('konstrukt:themechange', draw);
  }

  async function renderScale(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const manifest = await loadManifest();
    const spacing = Object.entries(manifest.global)
      .filter(([name]) => name.startsWith('sp-'))
      .sort((a, b) => parseFloat(a[1].value) - parseFloat(b[1].value));
    el.innerHTML = spacing
      .map(
        ([name, t]) => `
          <div class="scale-row">
            <span class="scale-label">--${name} · ${t.value}</span>
            <span class="scale-bar" style="width:${t.value}"></span>
          </div>`
      )
      .join('');
  }

  window.KonstruktDocs = { renderSwatches, renderScale };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderTopbar);
  } else {
    renderTopbar();
  }
})();
