"""Build the static SVG charts that site pages show.

Run from the repository root:

    python3 scripts/build_charts.py

It writes a light and a dark SVG for each chart to docs/.gitbook/assets/.
A page shows them with a <picture> element, so GitBook picks the variant
that matches the reader's theme. GitBook strips scripts, so the charts are
static. The Markdown table next to each chart is its table view.

The data below is copied from the pages that show each chart. When a value
changes on a page, change it here, run this script, and commit the SVGs.

Palette: the dataviz reference palette, blue ordinal ramp. The ramps were
checked with validate_palette.js --ordinal in both modes (all checks pass).
"""

import pathlib

OUT = pathlib.Path("docs/.gitbook/assets")

THEMES = {
    "light": {
        "surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
        "grid": "#e1e0d9", "axis": "#c3c2b7",
        "ramp2": ["#86b6ef", "#2a78d6"],
        "ramp3": ["#86b6ef", "#3987e5", "#1c5cab"],
    },
    "dark": {
        "surface": "#1a1a19", "ink": "#ffffff", "ink2": "#c3c2b7", "muted": "#898781",
        "grid": "#2c2c2a", "axis": "#383835",
        "ramp2": ["#184f95", "#3987e5"],
        "ramp3": ["#184f95", "#2a78d6", "#6da7ec"],
    },
}

FONT = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'
MONO = 'font-family="ui-monospace, SFMono-Regular, Menlo, monospace"'


def bar(x0: float, y: float, w: float, h: float, fill: str, r: float = 4) -> str:
    """A horizontal bar: square at the baseline, 4px rounded data-end."""
    r = min(r, w, h / 2)
    return (f'<path d="M{x0:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} '
            f'a{r},{r} 0 0 1 -{r},{r} h-{w - r:.1f} z" fill="{fill}"/>')


def text(x: float, y: float, s: str, fill: str, size: int = 13, anchor: str = "start",
         weight: int = 400, font: str = FONT) -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" {font} font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{s}</text>')


def svg(width: int, height: int, title: str, desc: str, body: list[str], t: dict) -> str:
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">',
        f"<title id=\"t\">{title}</title>",
        f"<desc id=\"d\">{desc}</desc>",
        f'<rect width="{width}" height="{height}" rx="8" fill="{t["surface"]}"/>',
        *body,
        "</svg>",
        "",
    ])


# ---------------------------------------------------------------------------
# Chart 1: rows per class, frozen v8 against v9.2.
# Source: docs/mailroom-dataset/mailroom-dataset.md ("Classes at a glance").
# v8 rows = v9.2 rows minus the stated delta.
DATASET = [  # class, v8 rows, v9.2 rows, v9.2 share
    ("insurance_claim", 950, 1100, "33.3%"),
    ("correspondence", 350, 1000, "30.3%"),
    ("contract", 509, 600, "18.2%"),
    ("corporate_record", 39, 450, "13.6%"),
    ("merger_agreement", 152, 152, "4.6%"),
]


def dataset_chart(t: dict) -> str:
    W, x0, x1, vmax = 720, 176, 600, 1200
    sx = lambda v: x0 + (x1 - x0) * v / vmax  # noqa: E731
    body = [
        text(24, 34, "Rows per class: frozen v8 against v9.2", t["ink"], 16, weight=600),
        text(24, 56, "mailroom-dataset, 2,000 rows in v8 and 3,302 rows in v9.2", t["ink2"], 13),
    ]
    # Legend (two series, so a legend is always present).
    lx = 24
    for label, color in (("v8 (frozen parent)", t["ramp2"][0]), ("v9.2 (current pin)", t["ramp2"][1])):
        body.append(f'<rect x="{lx}" y="72" width="12" height="12" rx="3" fill="{color}"/>')
        body.append(text(lx + 18, 82, label, t["ink2"], 12))
        lx += 160
    top, group, bh, gap = 112, 52, 14, 2
    bottom = top + group * len(DATASET) - 14
    for v in range(0, vmax + 1, 300):
        x = sx(v)
        body.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bottom}" stroke="{t["grid"]}" stroke-width="1"/>')
        body.append(text(x, bottom + 18, f"{v:,}", t["muted"], 11, "middle"))
    body.append(f'<line x1="{x0}" y1="{top - 8}" x2="{x0}" y2="{bottom}" stroke="{t["axis"]}" stroke-width="1"/>')
    for i, (name, v8, v92, share) in enumerate(DATASET):
        y = top + i * group
        body.append(text(x0 - 10, y + bh + 6, name, t["ink"], 12, "end", font=MONO))
        body.append(bar(x0, y, sx(v8) - x0, bh, t["ramp2"][0]))
        body.append(text(sx(v8) + 6, y + 11, f"{v8:,}", t["muted"], 11))
        y2 = y + bh + gap
        body.append(bar(x0, y2, sx(v92) - x0, bh, t["ramp2"][1]))
        delta = v92 - v8
        note = f"  (+{delta:,})" if delta else "  (no change)"
        body.append(text(sx(v92) + 6, y2 + 11, f"{v92:,} · {share}{note}", t["ink"], 12, weight=600))
    body.append(text(24, bottom + 40, "Source: Classes at a glance table on this page. "
                     "v8 rows = v9.2 rows minus the change. As of 2026-10-07.", t["muted"], 11))
    return svg(W, bottom + 56, "Rows per class: frozen v8 against v9.2",
               "Horizontal bars. insurance_claim 950 to 1,100; correspondence 350 to 1,000; "
               "contract 509 to 600; corporate_record 39 to 450; merger_agreement 152 to 152.",
               body, t)


# ---------------------------------------------------------------------------
# Chart 2: extraction confidence routing bands per class.
# Source: llm-mailroom src/config/taxonomy.yaml confidence block, read at
# origin/main c6476f7 (2026-10-07). Same values as the table in
# docs/the-pipeline-in-depth/scoring-and-metrics.md.
ROUTING = [  # scope, low, judge_band_high
    ("global fallback", 0.88, 0.95),
    ("contract", 0.90, 0.97),
    ("merger_agreement", 0.90, 0.97),
    ("insurance_claim", 0.90, 0.97),
    ("corporate_record", 0.86, 0.94),
    ("correspondence", 0.85, 0.92),
]


def routing_chart(t: dict) -> str:
    W, x0, x1, lo, hi = 720, 176, 680, 0.80, 1.00
    sx = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)  # noqa: E731
    body = [
        text(24, 34, "Where extraction confidence routes a document", t["ink"], 16, weight=600),
        text(24, 56, "Per-class thresholds from taxonomy.yaml. The axis starts at 0.80; "
             "a score below 0.80 also retries.", t["ink2"], 13),
    ]
    lx, ly = 24, 72
    zones = (("Retry extraction (below low)", t["ramp3"][0]),
             ("LLM judge, Lane B (low to judge_band_high)", t["ramp3"][1]),
             ("Accept (judge_band_high and up)", t["ramp3"][2]))
    for label, color in zones:
        width = 18 + len(label) * 6.6 + 22  # conservative text width at 12px
        if lx + width > W - 24:  # wrap the legend, never clip it
            lx, ly = 24, ly + 22
        body.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="3" fill="{color}"/>')
        body.append(text(lx + 18, ly + 10, label, t["ink2"], 12))
        lx += width
    top, row, bh = ly + 44, 44, 18
    bottom = top + row * len(ROUTING) - 12
    for i, v in enumerate((0.80, 0.85, 0.90, 0.95, 1.00)):
        x = sx(v)
        body.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{bottom}" stroke="{t["grid"]}" stroke-width="1"/>')
        body.append(text(x, bottom + 18, f"{v:.2f}", t["muted"], 11, "middle"))
    for i, (scope, low, jbh) in enumerate(ROUTING):
        y = top + i * row
        body.append(text(x0 - 10, y + 13, scope, t["ink"], 12, "end",
                         font=FONT if scope.startswith("global") else MONO))
        g = 1  # half of the 2px surface gap
        body.append(f'<rect x="{x0}" y="{y}" width="{sx(low) - x0 - g:.1f}" height="{bh}" fill="{t["ramp3"][0]}"/>')
        body.append(f'<rect x="{sx(low) + g:.1f}" y="{y}" width="{sx(jbh) - sx(low) - 2 * g:.1f}" height="{bh}" fill="{t["ramp3"][1]}"/>')
        body.append(bar(sx(jbh) + g, y, x1 - sx(jbh) - g, bh, t["ramp3"][2]))
        body.append(text(sx(low), y + bh + 13, f"{low:.2f}", t["ink2"], 11, "middle"))
        body.append(text(sx(jbh), y + bh + 13, f"{jbh:.2f}", t["ink2"], 11, "middle"))
    body.append(text(24, bottom + 40, "Source: llm-mailroom src/config/taxonomy.yaml at main c6476f7 "
                     "(2026-10-07). Classification uses the separate high threshold.", t["muted"], 11))
    return svg(W, bottom + 56, "Where extraction confidence routes a document",
               "Banded bars per class on a 0.80 to 1.00 axis. Below low: retry. Low to judge_band_high: "
               "judge. At or above judge_band_high: accept. contract, merger_agreement, insurance_claim "
               "0.90 and 0.97; global 0.88 and 0.95; corporate_record 0.86 and 0.94; correspondence 0.85 and 0.92.",
               body, t)


CHARTS = {"chart-dataset-classes": dataset_chart, "chart-extraction-routing": routing_chart}

if __name__ == "__main__":
    if not pathlib.Path("docs").is_dir():
        raise SystemExit("Run this from the repository root (the folder that holds docs/).")
    for name, build in CHARTS.items():
        for mode, theme in THEMES.items():
            path = OUT / f"{name}-{mode}.svg"
            path.write_text(build(theme))
            print("wrote", path)
