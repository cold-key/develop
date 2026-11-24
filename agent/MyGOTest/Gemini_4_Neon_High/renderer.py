"""
Pure-Python anti-aliased renderer and interactive HTML5/Desmos exporter.
Every rendered pixel is generated STRICTLY by evaluating the mathematical equations
f_k(x) = g_k(y) (never copying raw skeleton pixels).
"""

from __future__ import annotations

import base64
import json
import math
import os
from typing import Dict, List, Tuple

from image_extract import save_png_rgb
from math_methods import FunctionCurve, math_to_px


METHOD_COLORS_RGB: Dict[str, Tuple[int, int, int]] = {
    "lagrange_x": (29, 78, 216),     # Cobalt Blue:  y = L_n(x)
    "lagrange_y": (225, 29, 72),     # Crimson Rose: x = L_n(y)
    "ellipse": (5, 150, 105),        # Emerald:      ((x-x0)/a)^2 = 1 - ((y-y0)/b)^2
    "hermite": (217, 119, 6),        # Amber:        Cubic Hermite
    "least_squares": (234, 88, 12),  # Orange:       Least-Squares Poly
    "linear": (124, 58, 237),        # Violet:       Linear
}


def curve_color_key(c: FunctionCurve) -> str:
    if c.method == "lagrange":
        return "lagrange_x" if c.axis == "x" else "lagrange_y"
    return c.method if c.method in METHOD_COLORS_RGB else "linear"


def _blend_pixel(
    buf: bytearray, w: int, h: int, x: int, y: int, rgb: Tuple[int, int, int], alpha: float
) -> None:
    if 0 <= x < w and 0 <= y < h and alpha > 0.0:
        a = 1.0 if alpha > 1.0 else alpha
        idx = (y * w + x) * 3
        inv = 1.0 - a
        buf[idx] = int(buf[idx] * inv + rgb[0] * a + 0.5)
        buf[idx + 1] = int(buf[idx + 1] * inv + rgb[1] * a + 0.5)
        buf[idx + 2] = int(buf[idx + 2] * inv + rgb[2] * a + 0.5)


def draw_aa_segment(
    buf: bytearray,
    w: int,
    h: int,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    rgb: Tuple[int, int, int],
    radius: float = 0.85,
    opacity: float = 1.0,
) -> None:
    """Draw a smooth anti-aliased line segment using exact point-to-segment distance."""
    min_x = max(0, int(math.floor(min(x0, x1) - radius - 1)))
    max_x = min(w - 1, int(math.ceil(max(x0, x1) + radius + 1)))
    min_y = max(0, int(math.floor(min(y0, y1) - radius - 1)))
    max_y = min(h - 1, int(math.ceil(max(y0, y1) + radius + 1)))

    dx = x1 - x0
    dy = y1 - y0
    len2 = dx * dx + dy * dy
    edge = radius + 0.65

    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            if len2 < 1e-9:
                d = math.hypot(px - x0, py - y0)
            else:
                t = ((px - x0) * dx + (py - y0) * dy) / len2
                if t < 0.0:
                    t = 0.0
                elif t > 1.0:
                    t = 1.0
                cx = x0 + t * dx
                cy = y0 + t * dy
                d = math.hypot(px - cx, py - cy)
            if d < edge:
                cov = 1.0 if d <= radius - 0.35 else max(0.0, (edge - d) / 1.0)
                _blend_pixel(buf, w, h, px, py, rgb, cov * opacity)


def draw_cartesian_grid(buf: bytearray, w: int, h: int) -> None:
    """Draw subtle mathematical grid lines and x/y axes on [-4, 4] x [-3, 3]."""
    grid_rgb = (232, 236, 242)
    axis_rgb = (180, 190, 205)

    # Vertical grid lines x = -3..3
    for gx in range(-3, 4):
        u, _ = math_to_px(float(gx), 0.0, w, h)
        col = axis_rgb if gx == 0 else grid_rgb
        xi = int(round(u))
        if 0 <= xi < w:
            for py in range(h):
                _blend_pixel(buf, w, h, xi, py, col, 0.85 if gx == 0 else 0.7)

    # Horizontal grid lines y = -2..2
    for gy in range(-2, 3):
        _, v = math_to_px(0.0, float(gy), w, h)
        col = axis_rgb if gy == 0 else grid_rgb
        yi = int(round(v))
        if 0 <= yi < h:
            for px in range(w):
                _blend_pixel(buf, w, h, px, yi, col, 0.85 if gy == 0 else 0.7)

    # Small tick marks along axes
    _, y_axis_v = math_to_px(0.0, 0.0, w, h)
    x_axis_u, _ = math_to_px(0.0, 0.0, w, h)
    for gx in range(-3, 4):
        if gx == 0:
            continue
        u, _ = math_to_px(float(gx), 0.0, w, h)
        for dy in range(-5, 6):
            _blend_pixel(buf, w, h, int(round(u)), int(round(y_axis_v)) + dy, (130, 142, 160), 0.9)
    for gy in range(-2, 3):
        if gy == 0:
            continue
        _, v = math_to_px(0.0, float(gy), w, h)
        for dx in range(-5, 6):
            _blend_pixel(buf, w, h, int(round(x_axis_u)) + dx, int(round(v)), (130, 142, 160), 0.9)


def render_pure_function_plot(
    curves: List[FunctionCurve],
    w: int,
    h: int,
    out_path: str,
    color_by_method: bool = False,
    show_grid: bool = True,
) -> bytearray:
    """Render f_k(x) = g_k(y) purely from mathematical evaluation onto a crisp white canvas."""
    buf = bytearray([252] * (w * h * 3))
    if show_grid:
        draw_cartesian_grid(buf, w, h)

    ink_rgb = (24, 24, 36)
    for c in curves:
        pts = c.sample_points(step_math=0.0065)
        rgb = METHOD_COLORS_RGB[curve_color_key(c)] if color_by_method else ink_rgb
        px_pts = [math_to_px(x, y, w, h) for (x, y) in pts]
        for i in range(len(px_pts) - 1):
            x0, y0 = px_pts[i]
            x1, y1 = px_pts[i + 1]
            # Safety guard against absurd segments outside canvas
            if math.hypot(x1 - x0, y1 - y0) > 40.0:
                continue
            draw_aa_segment(buf, w, h, x0, y0, x1, y1, rgb, radius=0.95, opacity=0.96)

    save_png_rgb(out_path, w, h, buf)
    return buf


def render_overlay_plot(
    curves: List[FunctionCurve],
    orig_rgb: bytes,
    w: int,
    h: int,
    out_path: str,
) -> bytearray:
    """Render color-coded f_k(x) = g_k(y) curves directly over faded original image."""
    buf = bytearray(w * h * 3)
    # Fade original toward white (55% white + 45% original) so colored curves pop clearly
    for i in range(w * h * 3):
        buf[i] = int(orig_rgb[i] * 0.45 + 255 * 0.55)

    for c in curves:
        pts = c.sample_points(step_math=0.0065)
        rgb = METHOD_COLORS_RGB[curve_color_key(c)]
        px_pts = [math_to_px(x, y, w, h) for (x, y) in pts]
        for i in range(len(px_pts) - 1):
            x0, y0 = px_pts[i]
            x1, y1 = px_pts[i + 1]
            if math.hypot(x1 - x0, y1 - y0) > 40.0:
                continue
            draw_aa_segment(buf, w, h, x0, y0, x1, y1, rgb, radius=1.05, opacity=0.95)

    save_png_rgb(out_path, w, h, buf)
    return buf


def render_side_by_side(
    orig_rgb: bytes,
    plot_rgb: bytearray,
    w: int,
    h: int,
    out_path: str,
) -> None:
    """Save side-by-side comparison PNG: Original (left) vs Pure f(x)=g(y) Plot (right)."""
    gap = 12
    out_w = w * 2 + gap
    buf = bytearray([235] * (out_w * h * 3))
    row_bytes = w * 3
    out_row = out_w * 3

    for y in range(h):
        src_off = y * row_bytes
        dst_left = y * out_row
        dst_right = dst_left + (w + gap) * 3
        buf[dst_left:dst_left + row_bytes] = orig_rgb[src_off:src_off + row_bytes]
        buf[dst_right:dst_right + row_bytes] = plot_rgb[src_off:src_off + row_bytes]

    save_png_rgb(out_path, out_w, h, buf)


def export_equations_files(
    curves: List[FunctionCurve],
    out_dir: str,
    stats: Dict,
) -> None:
    """Write equations.json and equations_desmos.txt."""
    json_path = os.path.join(out_dir, "equations.json")
    payload = {
        "title": "千早爱音 (Anon Chihaya) — f(x) = g(y) Mathematical Contour Reconstruction",
        "model": "Gemini 4 Neon (High)",
        "coordinate_domain": {"x": [-4.0, 4.0], "y": [-3.0, 3.0]},
        "statistics": stats,
        "curves": [c.to_dict() for c in curves],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    desmos_path = os.path.join(out_dir, "equations_desmos.txt")
    lines = [
        "# 千早爱音 (Anon Chihaya) — f(x) = g(y) Mathematical Function Drawing",
        "# Coordinate System: x in [-4, 4], y in [-3, 3] (1:1 isotropic aspect ratio)",
        f"# Total Curves: {len(curves)}",
        "# Every equation strictly satisfies the variable-separated form f_k(x) = g_k(y).",
        "# Paste any line below directly into Desmos (https://www.desmos.com/calculator)!",
        "",
    ]
    for c in curves:
        lines.append(f"# [{c.curve_id:03d}] {c.method} (deg={c.degree}, axis={c.axis}, max_err={c.max_error:.4f})")
        lines.append(c.to_desmos_latex())
    with open(desmos_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def export_interactive_html(
    curves: List[FunctionCurve],
    orig_image_path: str,
    stats: Dict,
    out_path: str,
) -> None:
    """
    Generate a completely self-contained interactive HTML5 viewer that plots
    千早爱音 LIVE in the browser by evaluating every f_k(x) = g_k(y) formula,
    with hover inspection, Chebyshev node visualization, method filter, and animation!
    """
    with open(orig_image_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("ascii")

    # Compact curve payload for fast client-side evaluation
    js_curves = []
    for c in curves:
        js_curves.append({
            "id": c.curve_id,
            "m": c.method,
            "ax": c.axis,
            "d": c.degree,
            "t0": round(c.t_min, 5),
            "t1": round(c.t_max, 5),
            "tc": round(c.t_center, 5),
            "c": [round(v, 6) for v in c.coeffs],
            "nd": [[round(p[0], 4), round(p[1], 4)] for p in c.nodes],
            "err": round(c.max_error * 136.5, 2),  # in pixels
            "eq": c.to_equation_str(),
            "lag": c.to_lagrange_basis_str() if c.method == "lagrange" else "",
            "des": c.to_desmos_latex(),
        })

    curves_json = json.dumps(js_curves, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>千早爱音 — f(x) = g(y) 拉格朗日函数描图 (Gemini 4 Neon High)</title>
<style>
  :root {{
    --bg: #0f172a;
    --panel: #1e293b;
    --border: #334155;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --accent: #f472b6;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    background: var(--bg); color: var(--text);
    display: grid; grid-template-columns: 1fr 370px; height: 100vh; overflow: hidden;
  }}
  #stage-wrap {{
    position: relative; display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
    overflow: hidden;
  }}
  canvas {{
    background: #ffffff; border-radius: 10px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    max-width: 96%; max-height: 94%; cursor: crosshair;
  }}
  aside {{
    background: var(--panel); border-left: 1px solid var(--border);
    padding: 18px; display: flex; flex-direction: column; gap: 14px; overflow-y: auto;
  }}
  h1 {{ font-size: 1.15rem; margin: 0; color: var(--accent); }}
  .subtitle {{ font-size: 0.82rem; color: var(--muted); margin-top: 3px; }}
  .card {{
    background: rgba(15,23,42,0.6); border: 1px solid var(--border);
    border-radius: 8px; padding: 12px;
  }}
  .card h2 {{ font-size: 0.85rem; margin: 0 0 8px 0; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.04em; }}
  .ctrl {{ display: flex; align-items: center; justify-content: space-between; margin: 7px 0; font-size: 0.85rem; }}
  input[type="range"] {{ width: 145px; accent-color: var(--accent); }}
  .btn-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }}
  button {{
    background: #334155; color: #f8fafc; border: 1px solid #475569;
    padding: 6px 11px; border-radius: 6px; font-size: 0.82rem; cursor: pointer;
  }}
  button:hover {{ background: #475569; }}
  button.primary {{ background: #ec4899; border-color: #f472b6; font-weight: 600; }}
  button.primary:hover {{ background: #db2777; }}
  .legend {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.78rem; }}
  .leg-item {{ display: flex; align-items: center; gap: 6px; }}
  .swatch {{ width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }}
  .formula-box {{
    font-family: "Consolas", "Fira Code", monospace; font-size: 0.76rem;
    background: #0b1120; border: 1px solid #334155; border-radius: 6px;
    padding: 9px; color: #e2e8f0; word-break: break-all; max-height: 150px; overflow-y: auto;
  }}
  .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.8rem; }}
  .stat-val {{ font-size: 1.05rem; font-weight: 700; color: #f8fafc; }}
  .stat-lbl {{ font-size: 0.72rem; color: var(--muted); }}
</style>
</head>
<body>
  <div id="stage-wrap">
    <canvas id="canvas" width="1092" height="819"></canvas>
  </div>
  <aside>
    <div>
      <h1>千早爱音 · f(x) = g(y) 函数描图</h1>
      <div class="subtitle">Gemini 4 Neon (High) · Chebyshev-Lobatto 拉格朗日插值 + 分离变量圆锥曲线 + 埃尔米特/最小二乘</div>
    </div>

    <div class="card">
      <h2>数学统计指标</h2>
      <div class="stat-grid" id="stats-grid"></div>
    </div>

    <div class="card">
      <h2>可视化控制</h2>
      <div class="ctrl">
        <label>原图叠加透明度</label>
        <input id="bgOpacity" type="range" min="0" max="100" value="18" />
      </div>
      <div class="ctrl">
        <label>按数学方法着色</label>
        <input id="colorByMethod" type="checkbox" checked />
      </div>
      <div class="ctrl">
        <label>显示切比雪夫插值节点</label>
        <input id="showNodes" type="checkbox" />
      </div>
      <div class="ctrl">
        <label>显示直角坐标系网格</label>
        <input id="showGrid" type="checkbox" checked />
      </div>
      <div class="ctrl">
        <label>线宽</label>
        <input id="lineWidth" type="range" min="10" max="35" value="19" />
      </div>
      <div class="btn-row">
        <button class="primary" id="btnAnimate">▶ 逐步绘制动画</button>
        <button id="btnShowAll">全部显示</button>
      </div>
    </div>

    <div class="card">
      <h2>方法图例 (均为 f(x) = g(y))</h2>
      <div class="legend">
        <div class="leg-item"><span class="swatch" style="background:#1d4ed8"></span>Lagrange y = L(x)</div>
        <div class="leg-item"><span class="swatch" style="background:#e11d48"></span>Lagrange x = L(y)</div>
        <div class="leg-item"><span class="swatch" style="background:#059669"></span>分离椭圆 f(x)=g(y)</div>
        <div class="leg-item"><span class="swatch" style="background:#d97706"></span>三次 Hermite</div>
        <div class="leg-item"><span class="swatch" style="background:#ea580c"></span>最小二乘多项式</div>
        <div class="leg-item"><span class="swatch" style="background:#7c3aed"></span>线性段 f(x)=g(y)</div>
      </div>
    </div>

    <div class="card">
      <h2>曲线公式检查器 (悬停或点击曲线)</h2>
      <div id="hover-meta" style="font-size:0.78rem; color:#94a3b8; margin-bottom:6px;">
        将鼠标移到画布上任意曲线查看其 f(x) = g(y) 解析式与切比雪夫插值节点。
      </div>
      <div class="formula-box" id="hover-eq">f(x) = g(y)</div>
      <div id="hover-lag-wrap" style="display:none; margin-top:8px;">
        <div style="font-size:0.74rem; color:#f472b6; margin-bottom:4px;">拉格朗日基函数展开式：</div>
        <div class="formula-box" id="hover-lag"></div>
      </div>
    </div>
  </aside>

<script>
const CURVES = {curves_json};
const STATS = {stats_json};
const ORIG_SRC = "data:image/jpeg;base64,{b64_img}";

const W = 1092, H = 819, SCALE = (W / 2) / 4.0;
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const COLORS = {{
  lagrange_x: "#1d4ed8",
  lagrange_y: "#e11d48",
  ellipse: "#059669",
  hermite: "#d97706",
  least_squares: "#ea580c",
  linear: "#7c3aed",
}};

const origImg = new Image();
let imgReady = false;
origImg.onload = () => {{ imgReady = true; render(); }};
origImg.src = ORIG_SRC;

// Populate stats
const sg = document.getElementById("stats-grid");
const lagCnt = (STATS.method_counts.lagrange || 0);
const lagPct = ((lagCnt / STATS.total_curves) * 100).toFixed(1);
sg.innerHTML = `
  <div><div class="stat-val">${{STATS.total_curves}}</div><div class="stat-lbl">f(x)=g(y) 方程总数</div></div>
  <div><div class="stat-val">${{lagCnt}} (${{lagPct}}%)</div><div class="stat-lbl">拉格朗日插值曲线</div></div>
  <div><div class="stat-val">${{STATS.mean_rmse_px.toFixed(2)}} px</div><div class="stat-lbl">平均拟合 RMSE</div></div>
  <div><div class="stat-val">${{STATS.max_error_px.toFixed(2)}} px</div><div class="stat-lbl">最大单段误差</div></div>
`;

function toPx(x, y) {{ return [x * SCALE + W / 2, H / 2 - y * SCALE]; }}
function toMath(u, v) {{ return [(u - W / 2) / SCALE, (H / 2 - v) / SCALE]; }}

function evalShifted(coeffs, t, tc) {{
  const u = t - tc;
  let acc = 0;
  for (let i = coeffs.length - 1; i >= 0; i--) acc = acc * u + coeffs[i];
  return acc;
}}

// Pre-evaluate every curve purely from its mathematical equation f(x) = g(y)
const SAMPLED = CURVES.map(cv => {{
  const pts = [];
  if (cv.ax === "conic") {{
    const [x0, y0, a, b] = cv.c;
    const n = 48;
    for (let k = 0; k <= n; k++) {{
      const th = (2 * Math.PI * k) / n;
      pts.push(toPx(x0 + a * Math.cos(th), y0 + b * Math.sin(th)));
    }}
  }} else {{
    const span = cv.t1 - cv.t0;
    const steps = Math.max(10, Math.ceil(span / 0.008));
    for (let k = 0; k <= steps; k++) {{
      const t = cv.t0 + span * (k / steps);
      const v = evalShifted(cv.c, t, cv.tc);
      pts.push(cv.ax === "x" ? toPx(t, v) : toPx(v, t));
    }}
  }}
  return pts;
}});

let hoveredIdx = -1;
let pinnedIdx = -1;
let visibleCount = CURVES.length;
let animTimer = null;

function colorOf(cv) {{
  if (!document.getElementById("colorByMethod").checked) return "#181824";
  if (cv.m === "lagrange") return cv.ax === "x" ? COLORS.lagrange_x : COLORS.lagrange_y;
  return COLORS[cv.m] || "#181824";
}}

function drawGrid() {{
  ctx.save();
  ctx.lineWidth = 1;
  for (let gx = -3; gx <= 3; gx++) {{
    const [u] = toPx(gx, 0);
    ctx.strokeStyle = gx === 0 ? "rgba(100,116,139,0.55)" : "rgba(148,163,184,0.22)";
    ctx.beginPath(); ctx.moveTo(u, 0); ctx.lineTo(u, H); ctx.stroke();
  }}
  for (let gy = -2; gy <= 2; gy++) {{
    const [, v] = toPx(0, gy);
    ctx.strokeStyle = gy === 0 ? "rgba(100,116,139,0.55)" : "rgba(148,163,184,0.22)";
    ctx.beginPath(); ctx.moveTo(0, v); ctx.lineTo(W, v); ctx.stroke();
  }}
  ctx.fillStyle = "rgba(71,85,105,0.75)";
  ctx.font = "12px Consolas, monospace";
  const [ox, oy] = toPx(0, 0);
  for (let gx = -3; gx <= 3; gx++) {{
    if (gx === 0) continue;
    const [u] = toPx(gx, 0);
    ctx.fillText(String(gx), u + 3, oy + 14);
  }}
  for (let gy = -2; gy <= 2; gy++) {{
    if (gy === 0) continue;
    const [, v] = toPx(0, gy);
    ctx.fillText(String(gy), ox + 5, v - 4);
  }}
  ctx.restore();
}}

function render() {{
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#fcfcfd";
  ctx.fillRect(0, 0, W, H);

  const bgOp = Number(document.getElementById("bgOpacity").value) / 100;
  if (imgReady && bgOp > 0) {{
    ctx.save();
    ctx.globalAlpha = bgOp;
    ctx.drawImage(origImg, 0, 0, W, H);
    ctx.restore();
  }}

  if (document.getElementById("showGrid").checked) drawGrid();

  const lw = Number(document.getElementById("lineWidth").value) / 10;
  const showNodes = document.getElementById("showNodes").checked;
  const activeIdx = pinnedIdx >= 0 ? pinnedIdx : hoveredIdx;

  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  for (let i = 0; i < visibleCount; i++) {{
    const cv = CURVES[i];
    const pts = SAMPLED[i];
    if (pts.length < 2) continue;
    const isActive = (i === activeIdx);
    ctx.strokeStyle = isActive ? "#ff007f" : colorOf(cv);
    ctx.lineWidth = isActive ? lw * 2.4 : lw;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let k = 1; k < pts.length; k++) ctx.lineTo(pts[k][0], pts[k][1]);
    ctx.stroke();

    if (showNodes && cv.nd && cv.nd.length > 0) {{
      ctx.fillStyle = "#f59e0b";
      for (const [nx, ny] of cv.nd) {{
        const [px, py] = toPx(nx, ny);
        ctx.beginPath(); ctx.arc(px, py, 2.2, 0, Math.PI * 2); ctx.fill();
      }}
    }}
  }}

  // Highlight interpolation nodes of the active curve
  if (activeIdx >= 0 && activeIdx < visibleCount) {{
    const cv = CURVES[activeIdx];
    ctx.fillStyle = "#facc15";
    ctx.strokeStyle = "#111827";
    ctx.lineWidth = 1.5;
    for (const [nx, ny] of cv.nd) {{
      const [px, py] = toPx(nx, ny);
      ctx.beginPath(); ctx.arc(px, py, 4.5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    }}
  }}
}}

function updateInspector(idx) {{
  const meta = document.getElementById("hover-meta");
  const eq = document.getElementById("hover-eq");
  const lw = document.getElementById("hover-lag-wrap");
  const lag = document.getElementById("hover-lag");
  if (idx < 0) return;
  const cv = CURVES[idx];
  const tag = cv.m === "lagrange"
    ? `Lagrange 插值 (deg=${{cv.d}}, ${{cv.ax === "x" ? "y=L(x)" : "x=L(y)"}})`
    : `${{cv.m}} (deg=${{cv.d}})`;
  meta.textContent = `曲线 #${{cv.id}} · ${{tag}} · 最大误差 ${{cv.err}} px · 节点数 ${{cv.nd.length}}`;
  eq.textContent = cv.eq;
  if (cv.lag) {{
    lw.style.display = "block";
    lag.textContent = cv.lag;
  }} else {{
    lw.style.display = "none";
  }}
}}

function findNearestCurve(mx, my) {{
  let best = -1, bestD2 = 14 * 14;
  for (let i = 0; i < visibleCount; i++) {{
    const pts = SAMPLED[i];
    for (let k = 0; k < pts.length; k++) {{
      const dx = pts[k][0] - mx, dy = pts[k][1] - my;
      const d2 = dx * dx + dy * dy;
      if (d2 < bestD2) {{ bestD2 = d2; best = i; }}
    }}
  }}
  return best;
}}

canvas.addEventListener("mousemove", e => {{
  const rect = canvas.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (W / rect.width);
  const my = (e.clientY - rect.top) * (H / rect.height);
  const idx = findNearestCurve(mx, my);
  if (idx !== hoveredIdx) {{
    hoveredIdx = idx;
    if (pinnedIdx < 0) updateInspector(idx);
    render();
  }}
}});

canvas.addEventListener("click", e => {{
  const rect = canvas.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (W / rect.width);
  const my = (e.clientY - rect.top) * (H / rect.height);
  const idx = findNearestCurve(mx, my);
  pinnedIdx = (idx === pinnedIdx) ? -1 : idx;
  if (pinnedIdx >= 0) updateInspector(pinnedIdx);
  render();
}});

["bgOpacity", "colorByMethod", "showNodes", "showGrid", "lineWidth"].forEach(id => {{
  document.getElementById(id).addEventListener("input", render);
}});

document.getElementById("btnAnimate").addEventListener("click", () => {{
  if (animTimer) clearInterval(animTimer);
  visibleCount = 0;
  const step = Math.max(1, Math.ceil(CURVES.length / 180));
  animTimer = setInterval(() => {{
    visibleCount = Math.min(CURVES.length, visibleCount + step);
    render();
    if (visibleCount >= CURVES.length) {{
      clearInterval(animTimer);
      animTimer = null;
    }}
  }}, 25);
}});

document.getElementById("btnShowAll").addEventListener("click", () => {{
  if (animTimer) clearInterval(animTimer);
  visibleCount = CURVES.length;
  render();
}});

render();
</script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
