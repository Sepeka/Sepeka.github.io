"""Theme-aware plot output and native marimo appearance links."""
import base64
from html import escape
from io import BytesIO
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


def binary_entropy_svg(probability):
    """Render the binary entropy curve as lightweight responsive SVG."""
    probability = float(probability)
    x = lambda value: 70 + 690 * value
    y = lambda value: 305 - 270 * value
    points = []
    for index in range(201):
        p = index / 200
        entropy = entropy_bits([p, 1 - p])
        points.append(f"{'M' if index == 0 else 'L'}{x(p):.2f},{y(entropy):.2f}")
    entropy = entropy_bits([probability, 1 - probability])
    px, py = x(probability), y(entropy)
    grid = []
    for index in range(6):
        value = index / 5
        grid.extend([
            f'<line x1="{x(value):.2f}" y1="25" x2="{x(value):.2f}" y2="305" />',
            f'<text x="{x(value):.2f}" y="329" text-anchor="middle">{value:.1f}</text>',
            f'<line x1="70" y1="{y(value):.2f}" x2="760" y2="{y(value):.2f}" />',
            f'<text x="55" y="{y(value) + 5:.2f}" text-anchor="end">{value:.1f}</text>',
        ])
    return f'''<style>
    .binary-entropy-svg {{width:100%;height:auto;display:block;color:var(--foreground,#263044);}}
    .binary-entropy-svg .grid line {{stroke:currentColor;opacity:.17}}
    .binary-entropy-svg text {{fill:currentColor;font:14px system-ui,sans-serif}}
    .binary-entropy-svg .axis-label {{font-size:16px}}
    </style><svg class="binary-entropy-svg" viewBox="0 0 800 365"
      role="img" aria-label="Binary entropy for the selected probability of heads">
      <g class="grid">{''.join(grid)}</g>
      <path d="{''.join(points)}" fill="none" stroke="#9b8af0" stroke-width="3.5" />
      <line x1="{px:.2f}" y1="{py:.2f}" x2="{px:.2f}" y2="305"
        stroke="#e04f4f" stroke-width="2" stroke-dasharray="7 6" />
      <line x1="70" y1="{py:.2f}" x2="{px:.2f}" y2="{py:.2f}"
        stroke="#e04f4f" stroke-width="2" stroke-dasharray="7 6" />
      <circle cx="{px:.2f}" cy="{py:.2f}" r="10" fill="#de704b" />
      <text class="axis-label" x="430" y="355" text-anchor="middle">Probability of heads</text>
      <text class="axis-label" transform="translate(18 165) rotate(-90)" text-anchor="middle">Entropy (bits)</text>
    </svg>'''


def scientific_code_html(probability):
    """Show the scientific Python calculation at the selected probability."""
    calculation = '''import math

def entropy_bits(probabilities):
    """Entropy in bits for a valid finite probability distribution."""
    return sum(-p * math.log2(p) for p in probabilities if p > 0)
'''
    example = (
        f"prob = {float(probability):.2f}\n"
        "probabilities = [prob, 1 - prob]\n"
        "entropy = entropy_bits(probabilities)"
    )
    formatter = HtmlFormatter(nowrap=True)
    result = entropy_bits([float(probability), 1 - float(probability)])
    return f'''<style>
    .entropy-code-panel {{border:1px solid #888;border-radius:8px;padding:16px;margin:20px 0;}}
    .entropy-code-panel p {{margin-bottom:22px;}}
    .entropy-python-code {{display:block;white-space:pre-wrap;padding:15px 18px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;color:#1f2328;overflow-x:auto;font:14px/1.65 ui-monospace,monospace;}}
    .entropy-python-code .k,.entropy-python-code .kn {{color:#0000ff}} .entropy-python-code .nf {{color:#795e26}}
    .entropy-python-code .nb {{color:#267f99}} .entropy-python-code .s,.entropy-python-code .sd {{color:#a31515}}
    .entropy-python-code .c,.entropy-python-code .c1 {{color:#008000;font-style:italic}} .entropy-python-code .mi,.entropy-python-code .mf {{color:#098658}}
    .dark .entropy-python-code {{background:#1e1e1e;color:#d4d4d4;border-color:#454545}}
    .dark .entropy-python-code .k,.dark .entropy-python-code .kn {{color:#c586c0}} .dark .entropy-python-code .nf {{color:#dcdcaa}}
    .dark .entropy-python-code .nb {{color:#4ec9b0}} .dark .entropy-python-code .s,.dark .entropy-python-code .sd {{color:#ce9178}}
    .dark .entropy-python-code .c,.dark .entropy-python-code .c1 {{color:#6a9955}} .dark .entropy-python-code .mi,.dark .entropy-python-code .mf {{color:#b5cea8}}
    </style><section class="entropy-code-panel">
    <strong>See the calculation in Python</strong>
    <p>This is the function used for the notebook's entropy calculations in bits. Zero-probability outcomes contribute zero.</p>
    <pre class="entropy-python-code">{highlight(calculation, PythonLexer(), formatter)}</pre>
    <pre class="entropy-python-code">{highlight(example, PythonLexer(), formatter)}</pre>
    <code>entropy = {result:.6f}  # bits</code>
    </section>'''


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


def view_control(params=None, browser_runtime=False, in_browser_editor=False):
    viewer_query = control_url(params, **{"view-as": "present"})
    editor_query = control_url(params, **{"view-as": "edit"})
    if browser_runtime:
        viewer = f"../{viewer_query}" if in_browser_editor else viewer_query
        editor = editor_query if in_browser_editor else f"edit/{editor_query}"
    else:
        viewer, editor = viewer_query, editor_query
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


def navigation_control(params=None, browser_runtime=False, in_browser_editor=False):
    """An iframe permits event handlers; marimo sanitizes them in plain Html."""
    return """<!doctype html><html><head><style>
    html {background:#ffffff;color-scheme:light;}
    html.dark {background:#171d19;color-scheme:dark;}
    body {margin:0;font:15px/1.4 system-ui,sans-serif;color:#263044;background:#ffffff;}
    body.dark {color:#e6e8f2;background:#171d19;}
    .entropy-view-switch {margin:0!important;}
    p {margin-bottom:0;}
    </style></head><body>""" + view_control(
        params, browser_runtime, in_browser_editor
    ) + appearance_control(params) + """
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
