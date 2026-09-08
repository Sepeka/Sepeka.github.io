"""Theme-aware plot output and native marimo appearance links."""
import base64
from html import escape
import inspect
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from scientific import entropy_bits


THEME_STYLES = '''<style>
.entropy-appearance {display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:10px 0 20px;}
.entropy-appearance a {display:inline-block;border:1px solid #a9a3bf;padding:6px 15px;border-radius:20px;text-decoration:none;color:inherit;font:14px system-ui,sans-serif;}
.entropy-appearance a:focus-visible {outline:3px solid #a99aff;outline-offset:2px;}
.entropy-appearance .entropy-theme-light {background:#6554c0;color:white;border-color:#6554c0;}
.entropy-figure img {display:block;max-width:100%;height:auto;}
.entropy-figure .entropy-figure-dark {display:none;}
.dark .entropy-theme-light {background:transparent;color:inherit;border-color:#a9a3bf;}
.dark .entropy-theme-dark {background:#a99aff;color:#171723;border-color:#a99aff;}
.dark .entropy-figure-light {display:none;}
.dark .entropy-figure .entropy-figure-dark {display:block;}
:host-context(.dark) .entropy-theme-light {background:transparent;color:inherit;border-color:#a9a3bf;}
:host-context(.dark) .entropy-theme-dark {background:#a99aff;color:#171723;border-color:#a99aff;}
:host-context(.dark) .entropy-figure-light {display:none;}
:host-context(.dark) .entropy-figure .entropy-figure-dark {display:block;}
</style>'''


def interactive_entropy_html(probability):
    """Return a browser-native draggable entropy explorer.

    Its iframe writes changes into marimo's built-in probability input, which
    keeps the interaction compatible with local Python and browser WebAssembly.
    """
    template = Path(__file__).with_name("entropy_explorer.html").read_text()
    calculation = "import math\n\n" + inspect.getsource(entropy_bits)
    example = "probabilities = [prob, 1 - prob]\nentropy = entropy_bits(probabilities)"
    formatter = HtmlFormatter(nowrap=True)
    return (
        template.replace("__INITIAL_PROBABILITY__", f"{float(probability):.2f}")
        .replace("__CALCULATION_HTML__", highlight(calculation, PythonLexer(), formatter))
        .replace("__EXAMPLE_HTML__", highlight(example, PythonLexer(), formatter))
    )


def control_url(params, **changes):
    """Change only the requested URL setting; retain other view/session settings."""
    updated = dict(params or {})
    updated.update(changes)
    return escape("?" + urlencode(updated, doseq=True), quote=True)


def appearance_control(params=None):
    # Native marimo theme query parameters: applies to editor and reader views.
    light = control_url(params, theme='light')
    dark = control_url(params, theme='dark')
    return THEME_STYLES + f'''<nav class="entropy-appearance" aria-label="Appearance">
    <span>Appearance</span>
    <a class="entropy-theme-light" href="{light}" aria-label="Use light mode">☀ Light</a>
    <a class="entropy-theme-dark" href="{dark}" aria-label="Use dark mode">☾ Dark</a>
    </nav>'''


def figure_html(fig, description):
    """Render both palettes once so frontend theme changes need no Python rerun."""
    from matplotlib.text import Text
    from matplotlib.lines import Line2D
    images = []
    for mode in ('light', 'dark'):
        dark = mode == 'dark'
        background = '#191b23' if dark else '#ffffff'
        foreground = '#e6e8f2' if dark else '#263044'
        muted = '#788099' if dark else '#d0d4de'
        fig.set_facecolor(background)
        for ax in fig.axes:
            ax.set_facecolor(background)
            ax.tick_params(colors=foreground)
            for spine in ax.spines.values():
                spine.set_edgecolor(muted)
            for grid in ax.get_xgridlines() + ax.get_ygridlines():
                grid.set_color(muted)
                grid.set_alpha(.3)
        for text in fig.findobj(Text):
            text.set_color(foreground)
            box = text.get_bbox_patch()
            if box is not None:
                box.set_facecolor('#302c48' if dark else '#f0edff')
                box.set_edgecolor('#a99aff' if dark else '#6554c0')
        for line in fig.findobj(Line2D):
            if line.get_color() in ('#6554c0', '#a99aff'):
                line.set_color('#a99aff' if dark else '#6554c0')
        data = BytesIO()
        fig.savefig(data, format='png', dpi=120, bbox_inches='tight', facecolor=background)
        images.append(f'<img class="entropy-figure-{mode}" alt="{escape(description, quote=True)}" '
                      f'src="data:image/png;base64,{base64.b64encode(data.getvalue()).decode()}" />')
    return THEME_STYLES + '<div class="entropy-figure">' + ''.join(images) + '</div>'


def view_control(params=None):
    viewer = control_url(params, **{"view-as": "present"})
    editor = control_url(params, **{"view-as": "edit"})
    return """<style>
    .entropy-view-switch {border:2px solid #6554c0;border-radius:10px;padding:16px;margin:8px 0;}
    .entropy-view-switch nav {display:flex;flex-wrap:wrap;gap:12px;margin-top:10px;}
    .entropy-view-switch a {display:inline-block;padding:12px 22px;border-radius:7px;background:#6554c0;color:white;text-decoration:none;font:bold 16px system-ui,sans-serif;}
    .entropy-view-switch a:focus-visible {outline:3px solid #a99aff;outline-offset:3px;}
    </style><section class="entropy-view-switch" aria-label="Notebook view">
    <strong>Choose how to explore this notebook</strong>
    <nav><a href="__VIEWER__" aria-label="Viewer mode — hide code">▶ Viewer mode · Hide code</a>
    <a href="__EDITOR__" aria-label="Edit mode — show code">✎ Edit mode · Show code</a></nav>
    <p>Viewer mode keeps the interactive experiments visible. Edit mode also shows the Python code.</p>
    </section>""".replace("__VIEWER__", viewer).replace("__EDITOR__", editor)


def navigation_control(params=None):
    """An iframe permits event handlers; marimo sanitizes them in plain Html."""
    return """<!doctype html><html><head><style>
    html {background:#ffffff;color-scheme:light;}
    html.dark {background:#171d19;color-scheme:dark;}
    body {margin:0;font:15px/1.4 system-ui,sans-serif;color:#263044;background:#ffffff;}
    body.dark {color:#e6e8f2;background:#171d19;}
    .entropy-view-switch {margin:0!important;}
    p {margin-bottom:0;}
    </style></head><body>""" + view_control(params) + appearance_control(params) + """
    <script>
    const parentWindow = window.parent;
    const sync = () => {
      const dark = parentWindow.document.body.classList.contains('dark');
      document.documentElement.classList.toggle('dark', dark);
      document.body.classList.toggle('dark', dark);
      const parentBackground = parentWindow.getComputedStyle(parentWindow.document.body).backgroundColor;
      if (parentBackground !== 'rgba(0, 0, 0, 0)' && parentBackground !== 'transparent') {
        document.documentElement.style.backgroundColor = parentBackground;
        document.body.style.backgroundColor = parentBackground;
      }
      document.querySelectorAll('a').forEach(link => {
        const source = new URL(link.getAttribute('href'), parentWindow.location.href);
        if (!link.dataset.setting) {
          link.dataset.setting = link.closest('.entropy-appearance') ? 'theme' : 'view-as';
          link.dataset.value = source.searchParams.get(link.dataset.setting);
        }
        const target = new URL(parentWindow.location.href);
        target.searchParams.set(link.dataset.setting, link.dataset.value);
        // The local reader executes on the server; the editor has its own session.
        if (link.dataset.setting === 'view-as' &&
            ['localhost', '127.0.0.1'].includes(target.hostname) &&
            ['2718', '2720'].includes(target.port)) {
          target.port = link.dataset.value === 'edit' ? '2720' : '2718';
        } else if (link.dataset.setting === 'view-as') {
          const parts = target.pathname.split('/').filter(Boolean);
          if (link.dataset.value === 'edit' && parts.at(-1) !== 'edit') {
            parts.push('edit');
          }
          if (link.dataset.value === 'present' && parts.at(-1) === 'edit') {
            parts.pop();
          }
          target.pathname = '/' + parts.join('/') + '/';
        }
        link.href = target.href;
        link.target = '_parent';
      });
    };
    sync();
    document.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link) return;
      sync();
      event.preventDefault();
      parentWindow.location.assign(link.href);
    });
    new MutationObserver(sync).observe(parentWindow.document.body, {attributes:true,attributeFilter:['class']});
    </script></body></html>"""
