"""
Main entry point: End-to-end f(x) = g(y) mathematical function tracing for 千早爱音.jpg.

Usage:
    python Gemini_4_Neon_High/run_trace.py
"""

from __future__ import annotations

import math
import os
import sys
import time
from collections import Counter
from typing import Dict, List

# Ensure local modules resolve regardless of working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from image_extract import (
    extract_anime_lineart,
    load_image_rgb,
    trace_skeleton_polylines,
    zhang_suen_thinning,
)
from math_methods import FunctionCurve, fit_all_polylines, math_to_px
from renderer import (
    export_equations_files,
    export_interactive_html,
    render_overlay_plot,
    render_pure_function_plot,
    render_side_by_side,
)


def verify_separated_equation_consistency(curves: List[FunctionCurve]) -> float:
    """
    Mathematical self-check: verify that every sampled point (x, y) on every curve
    strictly satisfies |f_k(x) - g_k(y)| == 0 (within floating-point precision).
    """
    max_resid = 0.0
    for c in curves:
        pts = c.sample_points(step_math=0.05)
        for x, y in pts:
            if c.axis == "conic":
                x0, y0, a, b = c.coeffs
                fx = ((x - x0) / a) ** 2
                gy = 1.0 - ((y - y0) / b) ** 2
                resid = abs(fx - gy)
            elif c.axis == "x":
                fx = c.eval_explicit(x)
                gy = y
                resid = abs(fx - gy)
            else:
                fx = x
                gy = c.eval_explicit(y)
                resid = abs(fx - gy)
            if resid > max_resid:
                max_resid = resid
    return max_resid


def compute_contour_alignment(
    curves: List[FunctionCurve], skel: bytearray, w: int, h: int, radius_px: int = 3
) -> Dict[str, float]:
    """
    Measure how faithfully the purely mathematical f(x) = g(y) plot reproduces the
    original anime skeleton contour:
      - Recall:    % of original skeleton pixels within `radius_px` of a plotted f(x)=g(y) point
      - Precision: % of plotted f(x)=g(y) points within `radius_px` of an original skeleton pixel
    """
    # Rasterize mathematical curve points onto a binary grid
    plot_mask = bytearray(w * h)
    plotted_coords = []
    for c in curves:
        for x, y in c.sample_points(step_math=0.005):
            u, v = math_to_px(x, y, w, h)
            ui, vi = int(round(u)), int(round(v))
            if 0 <= ui < w and 0 <= vi < h:
                idx = vi * w + ui
                if not plot_mask[idx]:
                    plot_mask[idx] = 1
                    plotted_coords.append((ui, vi))

    def has_neighbor(grid: bytearray, cx: int, cy: int, r: int) -> bool:
        y0 = max(0, cy - r)
        y1 = min(h - 1, cy + r)
        x0 = max(0, cx - r)
        x1 = min(w - 1, cx + r)
        r2 = r * r
        for ny in range(y0, y1 + 1):
            dy2 = (ny - cy) ** 2
            row = ny * w
            for nx in range(x0, x1 + 1):
                if (nx - cx) ** 2 + dy2 <= r2 and grid[row + nx]:
                    return True
        return False

    skel_total = 0
    skel_hit = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if skel[row + x]:
                skel_total += 1
                if has_neighbor(plot_mask, x, y, radius_px):
                    skel_hit += 1

    plot_hit = sum(1 for (x, y) in plotted_coords if has_neighbor(skel, x, y, radius_px))
    recall = (skel_hit / skel_total) if skel_total else 0.0
    precision = (plot_hit / len(plotted_coords)) if plotted_coords else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return {
        "precision_at_3px": round(precision * 100.0, 2),
        "recall_at_3px": round(recall * 100.0, 2),
        "f1_at_3px": round(f1 * 100.0, 2),
    }


def main() -> None:
    t_start = time.time()
    image_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "千早爱音.jpg"))
    print("=" * 72)
    print("千早爱音 (Anon Chihaya) — f(x) = g(y) Mathematical Function Contour Tracer")
    print("=" * 72)

    # 1. Load image & extract anime lineart skeleton
    t0 = time.time()
    w, h, orig_rgb = load_image_rgb(image_path)
    print(f"[1/5] Loaded image ({w} x {h}) in {time.time() - t0:.2f}s")

    t1 = time.time()
    mask, _ = extract_anime_lineart(w, h, orig_rgb)
    skel = zhang_suen_thinning(mask, w, h)
    polylines = trace_skeleton_polylines(skel, w, h, min_chain_len=9, spur_prune_len=8)
    print(
        f"[2/5] Extracted anime lineart ({sum(mask)} px) -> skeleton ({sum(skel)} px) "
        f"-> {len(polylines)} merged strokes in {time.time() - t1:.2f}s"
    )

    # 2. Fit strictly separated f_k(x) = g_k(y) equations
    t2 = time.time()
    scale = (w / 2.0) / 4.0  # 136.5 px per math unit
    curves = fit_all_polylines(polylines, w, h, tol_px=1.6, max_lagrange_degree=5)
    max_eq_resid = verify_separated_equation_consistency(curves)
    print(
        f"[3/5] Fitted {len(curves)} f(x)=g(y) equations in {time.time() - t2:.2f}s "
        f"(equation self-check max |f(x)-g(y)| = {max_eq_resid:.2e})"
    )

    # 3. Compute statistics & contour accuracy
    t3 = time.time()
    method_counts = Counter(c.method for c in curves)
    axis_counts = Counter(c.axis for c in curves)
    deg_counts = Counter(c.degree for c in curves if c.method == "lagrange")
    rmses_px = [c.rmse * scale for c in curves]
    max_errs_px = [c.max_error * scale for c in curves]
    alignment = compute_contour_alignment(curves, skel, w, h, radius_px=3)

    stats = {
        "image_size": [w, h],
        "scale_px_per_unit": scale,
        "raw_polylines": len(polylines),
        "total_curves": len(curves),
        "method_counts": dict(method_counts),
        "axis_counts": dict(axis_counts),
        "lagrange_degree_distribution": {str(k): v for k, v in sorted(deg_counts.items())},
        "mean_rmse_px": round(sum(rmses_px) / max(1, len(rmses_px)), 3),
        "median_max_error_px": round(sorted(max_errs_px)[len(max_errs_px) // 2], 3),
        "max_error_px": round(max(max_errs_px) if max_errs_px else 0.0, 3),
        "max_equation_residual": float(f"{max_eq_resid:.2e}"),
        "contour_alignment": alignment,
    }
    print(f"[4/5] Evaluated accuracy in {time.time() - t3:.2f}s:")
    print(f"      Methods : {dict(method_counts)}")
    print(f"      Axes    : {dict(axis_counts)}")
    print(f"      Lagrange degrees: {dict(sorted(deg_counts.items()))}")
    print(
        f"      Fit err : mean RMSE = {stats['mean_rmse_px']:.2f} px, "
        f"median max-err = {stats['median_max_error_px']:.2f} px, "
        f"worst = {stats['max_error_px']:.2f} px"
    )
    print(
        f"      Contour : Precision@3px = {alignment['precision_at_3px']}%, "
        f"Recall@3px = {alignment['recall_at_3px']}%, "
        f"F1@3px = {alignment['f1_at_3px']}%"
    )

    # 4. Render outputs strictly from f(x) = g(y) evaluations
    t4 = time.time()
    pure_path = os.path.join(SCRIPT_DIR, "anon_function_plot.png")
    colored_path = os.path.join(SCRIPT_DIR, "anon_function_colored.png")
    overlay_path = os.path.join(SCRIPT_DIR, "anon_overlay.png")
    compare_path = os.path.join(SCRIPT_DIR, "anon_comparison.png")
    html_path = os.path.join(SCRIPT_DIR, "interactive_viewer.html")

    pure_rgb = render_pure_function_plot(curves, w, h, pure_path, color_by_method=False, show_grid=True)
    render_pure_function_plot(curves, w, h, colored_path, color_by_method=True, show_grid=True)
    render_overlay_plot(curves, orig_rgb, w, h, overlay_path)
    render_side_by_side(orig_rgb, pure_rgb, w, h, compare_path)
    export_equations_files(curves, SCRIPT_DIR, stats)
    export_interactive_html(curves, image_path, stats, html_path)

    # Clean up temporary debug image if present
    dbg = os.path.join(SCRIPT_DIR, "_debug_skeleton.png")
    if os.path.exists(dbg):
        os.remove(dbg)

    print(f"[5/5] Rendered all plots & exported equations/HTML in {time.time() - t4:.2f}s")
    print(f"Total pipeline time: {time.time() - t_start:.2f}s")
    print("=" * 72)


if __name__ == "__main__":
    main()
