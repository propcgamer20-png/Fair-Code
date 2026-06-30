"""Render a ProfileResult to terminal text, JSON, or a standalone HTML report.

`report.py` is the only module that formats results, so terminal/JSON/HTML stay
in sync. Terminal output follows the existing audit aesthetic (``"=" * 60``
section banners, percentage formatting) so it feels native to the project.
"""

from __future__ import annotations

import html
import json

WIDTH = 62
DISPLAY_GROUPS = 12  # cap rows shown per dimension; full data stays in the result


def to_json(result: dict, indent: int = 2) -> str:
    return json.dumps(result, indent=indent)


def _bar(share: float, width: int = 24) -> str:
    filled = round(share * width)
    return "█" * filled + "·" * (width - filled)


def to_terminal(result: dict) -> str:
    lines: list[str] = []
    add = lines.append

    add("=" * WIDTH)
    add("FAIR CODE - DATASET REPRESENTATION PROFILE")
    add("=" * WIDTH)
    add("")
    add(f"  Rows: {result['n_rows']:,}    Columns: {result['n_cols']}")
    add(f"  Representation score: {result['overall_score']}/100  "
        f"(Grade {result['grade']})")
    add("")

    if not result["dimensions"]:
        add("  No demographic columns detected.")
        add("=" * WIDTH)
        return "\n".join(lines)

    for d in result["dimensions"]:
        add("-" * WIDTH)
        title = f"{d['name']}  [{d['kind']}]"
        add(f"{title}    score {d['dimension_score']}/100")
        add("-" * WIDTH)
        shown = d["groups"][:DISPLAY_GROUPS]
        for g in shown:
            mark = "  <- under-represented" if g["label"] in d["under_represented"] else ""
            add(f"  {g['label'][:18]:<18} {_bar(g['share'])} "
                f"{g['share'] * 100:5.1f}%  (n={g['count']:,}){mark}")
        if len(d["groups"]) > DISPLAY_GROUPS:
            add(f"  … and {len(d['groups']) - DISPLAY_GROUPS} more groups")
        meta = []
        if d["imbalance_ratio"] is not None:
            meta.append(f"imbalance {d['imbalance_ratio']:.1f}x")
        elif d["n_groups"] > 1:
            meta.append("imbalance inf (empty subgroup)")
        if d["missing_pct"] > 0:
            meta.append(f"missing {d['missing_pct'] * 100:.1f}%")
        if d["skewness"] is not None:
            meta.append(f"skew {d['skewness']:+.2f}")
        if meta:
            add(f"  ({'  '.join(meta)})")
        add("")

    if result["flags"]:
        add("=" * WIDTH)
        add("FLAGS")
        add("=" * WIDTH)
        for f in result["flags"]:
            add(f"  ! {f}")
        add("")

    add("=" * WIDTH)
    return "\n".join(lines)


def to_html(result: dict) -> str:
    """A self-contained HTML report echoing the 'Audit Ledger' palette."""
    def esc(s) -> str:
        return html.escape(str(s))

    dim_blocks = []
    for d in result["dimensions"]:
        rows = []
        for g in d["groups"][:DISPLAY_GROUPS]:
            under = "under" if g["label"] in d["under_represented"] else "ok"
            rows.append(
                f'<tr class="{under}"><td>{esc(g["label"])}</td>'
                f'<td class="num">{g["share"] * 100:.1f}%</td>'
                f'<td class="num">{g["count"]:,}</td>'
                f'<td class="bar"><span style="width:{g["share"] * 100:.1f}%"></span></td></tr>'
            )
        dim_blocks.append(
            f'<section class="dim"><h2>{esc(d["name"])} '
            f'<span class="kind">{esc(d["kind"])}</span> '
            f'<span class="score">{d["dimension_score"]}/100</span></h2>'
            f'<table>{"".join(rows)}</table></section>'
        )

    flag_html = ""
    if result["flags"]:
        items = "".join(f"<li>{esc(f)}</li>" for f in result["flags"])
        flag_html = f'<section class="flags"><h2>Flags</h2><ul>{items}</ul></section>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fair Code - Dataset Profile</title>
<style>
 :root {{ --bg:#f4f1e8; --surface:#ebe7d9; --border:#d9d3c0; --accent:#a63a22;
          --accent3:#2f6b4f; --text:#36321f; --muted:#7d7459; }}
 body {{ font-family:'Helvetica Neue',sans-serif; background:var(--bg); color:var(--text);
         max-width:820px; margin:0 auto; padding:48px 24px; }}
 h1 {{ font-family:Georgia,serif; }}
 .score {{ color:var(--accent3); font-size:.7em; font-weight:600; }}
 .kind {{ color:var(--muted); font-size:.6em; text-transform:uppercase; letter-spacing:.08em; }}
 .dim {{ background:var(--surface); border:1px solid var(--border); border-radius:8px;
         padding:16px 20px; margin:16px 0; }}
 table {{ width:100%; border-collapse:collapse; }}
 td {{ padding:4px 8px; font-size:14px; border-bottom:1px solid var(--border); }}
 td.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
 td.bar {{ width:40%; }}
 td.bar span {{ display:block; height:10px; background:var(--accent3); border-radius:3px; }}
 tr.under td.bar span {{ background:var(--accent); }}
 tr.under td:first-child::after {{ content:' (under-represented)'; color:var(--accent); font-size:11px; }}
 .flags ul {{ list-style:none; padding:0; }}
 .flags li {{ background:#fbeae3; border-left:3px solid var(--accent); padding:8px 12px; margin:6px 0; border-radius:0 4px 4px 0; }}
 .head {{ border-bottom:2px solid var(--accent); padding-bottom:12px; }}
</style></head><body>
<div class="head"><h1>Dataset Representation Profile</h1>
<p>{result['n_rows']:,} rows · {result['n_cols']} columns · Score
<strong>{result['overall_score']}/100</strong> (Grade {result['grade']})</p></div>
{"".join(dim_blocks)}
{flag_html}
<p style="color:var(--muted);font-size:12px;margin-top:32px">
Generated by <a href="https://github.com/yakew7/Fair-Code">Fair Code</a> - diagnostic only.</p>
</body></html>"""
