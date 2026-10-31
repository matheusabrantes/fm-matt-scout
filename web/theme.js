(() => {
  const key = 'fmscout.theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const valid = value => value === 'light' || value === 'dark';
  let chosen = null;
  try { chosen = localStorage.getItem(key); } catch {}
  if (!valid(chosen)) chosen = valid(window.fmscoutNativeTheme) ? window.fmscoutNativeTheme : null;
  const sun = '<circle cx="8" cy="8" r="3"/><path d="M8 1v1.2M8 13.8V15M1 8h1.2M13.8 8H15M3.05 3.05l.85.85M12.1 12.1l.85.85M3.05 12.95l.85-.85M12.1 3.9l.85-.85"/>';
  const moon = '<path d="M13.8 9.4A6 6 0 0 1 6.6 2.2a6 6 0 1 0 7.2 7.2Z"/>';
  function apply(theme) {
    document.documentElement.dataset.theme = theme;
    const button = document.getElementById('theme-toggle');
    if (!button) return;
    const dark = theme === 'dark', label = `${dark ? 'Modo claro' : 'Modo escuro'} (⇧⌘L)`;
    button.title = label;
    button.setAttribute('aria-label', label);
    button.setAttribute('aria-pressed', String(dark));
    button.innerHTML = `<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${dark ? moon : sun}</svg>`;
  }
  function toggle() {
    chosen = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    apply(chosen);
    try { localStorage.setItem(key, chosen); } catch {}
    window.webkit?.messageHandlers?.themePreference?.postMessage(chosen);
  }
  apply(chosen || (system.matches ? 'dark' : 'light'));
  system.addEventListener('change', () => { if (!chosen) apply(system.matches ? 'dark' : 'light'); });
  document.addEventListener('DOMContentLoaded', () => {
    apply(document.documentElement.dataset.theme);
    document.getElementById('theme-toggle').addEventListener('click', toggle);
  });
  const mac = /Mac|iPhone|iPad/.test(navigator.platform);
  document.addEventListener('keydown', event => {
    if (event.key.toLowerCase() === 'l' && event.shiftKey && (mac ? event.metaKey : event.ctrlKey) && !event.altKey && !event.repeat) {
      event.preventDefault();
      toggle();
    }
  });
})();
