"""
Zero-dependency anime lineart extraction, Zhang-Suen thinning, and polyline graph tracing.
Designed specifically for cel-shaded anime illustrations so ink strokes become crisp
single-pixel centerlines (avoiding Canny double-edge artifacts).
"""

from __future__ import annotations

import math
import os
import struct
import subprocess
import tempfile
import zlib
from collections import deque
from itertools import accumulate
from typing import Dict, List, Tuple


def load_image_rgb(image_path: str) -> Tuple[int, int, bytes]:
    """Decode JPG/PNG image to raw RGB bytes using Windows .NET System.Drawing."""
    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Image not found: {abs_path}")

    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
        raw_path = tf.name

    ps_script = f"""
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap '{abs_path.replace("'", "''")}'
$w = $bmp.Width
$h = $bmp.Height
$rect = New-Object System.Drawing.Rectangle(0, 0, $w, $h)
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$stride = [Math]::Abs($data.Stride)
$bytes = New-Object byte[] ($stride * $h)
[System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $bytes, 0, $bytes.Length)
$bmp.UnlockBits($data)
$bmp.Dispose()

$out = New-Object byte[] (8 + $w * $h * 3)
[Array]::Copy([BitConverter]::GetBytes([int]$w), 0, $out, 0, 4)
[Array]::Copy([BitConverter]::GetBytes([int]$h), 0, $out, 4, 4)
$dst = 8
for ($y = 0; $y -lt $h; $y++) {{
    $rowStart = $y * $stride
    for ($x = 0; $x -lt $w; $x++) {{
        $i = $rowStart + $x * 3
        $out[$dst]     = $bytes[$i + 2] # R
        $out[$dst + 1] = $bytes[$i + 1] # G
        $out[$dst + 2] = $bytes[$i]     # B
        $dst += 3
    }}
}}
[System.IO.File]::WriteAllBytes('{raw_path.replace("'", "''")}', $out)
"""
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            check=True,
            capture_output=True,
            text=True,
        )
        with open(raw_path, "rb") as f:
            blob = f.read()
        w, h = struct.unpack("<ii", blob[:8])
        return w, h, blob[8:]
    finally:
        if os.path.exists(raw_path):
            os.remove(raw_path)


def save_png_rgb(path: str, w: int, h: int, rgb: bytes | bytearray) -> None:
    """Write an uncompressed/zlib-compressed RGB PNG using only Python stdlib."""
    def png_chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    row_bytes = w * 3
    raw_rows = bytearray()
    for y in range(h):
        raw_rows.append(0)  # filter type None
        start = y * row_bytes
        raw_rows.extend(rgb[start:start + row_bytes])

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw_rows), level=6)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(png_chunk(b"IHDR", ihdr))
        f.write(png_chunk(b"IDAT", idat))
        f.write(png_chunk(b"IEND", b""))


def box_blur_2d(grid: List[float], w: int, h: int, radius: int) -> List[float]:
    """Fast O(w*h) separable box blur using prefix sums."""
    tmp = [0.0] * (w * h)
    # Horizontal pass
    for y in range(h):
        row_off = y * w
        row = grid[row_off:row_off + w]
        pref = [0.0] + list(accumulate(row))
        for x in range(w):
            x0 = x - radius if x > radius else 0
            x1 = x + radius + 1 if x + radius + 1 < w else w
            tmp[row_off + x] = (pref[x1] - pref[x0]) / (x1 - x0)

    # Vertical pass
    out = [0.0] * (w * h)
    for x in range(w):
        col = tmp[x::w]
        pref = [0.0] + list(accumulate(col))
        for y in range(h):
            y0 = y - radius if y > radius else 0
            y1 = y + radius + 1 if y + radius + 1 < h else h
            out[y * w + x] = (pref[y1] - pref[y0]) / (y1 - y0)
    return out


def extract_anime_lineart(w: int, h: int, rgb: bytes) -> Tuple[bytearray, List[float]]:
    """
    Extract crisp single-centerline anime ink mask.
    Combines:
      1. Multi-scale Local Dark-Valley response (G_sigma(L) - L): peaks at the EXACT
         center of dark ink lines (hair, face, hand, eyes, mouth, collar, clothes).
      2. Strong color-step boundary detection for non-inked high-contrast features
         (e.g. eye iris/pupil/highlights, bright teeth inside dark mouth, tie stripes).
      3. Hysteresis thresholding to keep thin/faint hair strokes connected without noise.
    """
    n = w * h
    lum = [0.0] * n
    min_ch = [0.0] * n
    r_ch = [0.0] * n
    g_ch = [0.0] * n
    b_ch = [0.0] * n

    for i in range(n):
        j = i * 3
        r = rgb[j]
        g = rgb[j + 1]
        b = rgb[j + 2]
        r_ch[i] = r
        g_ch[i] = g
        b_ch[i] = b
        lum[i] = 0.299 * r + 0.587 * g + 0.114 * b
        min_ch[i] = r if (r <= g and r <= b) else (g if g <= b else b)

    # Smooth luminance with small (radius=3) and medium (radius=6) Gaussian approx (2 box passes)
    blur_s = box_blur_2d(box_blur_2d(lum, w, h, 2), w, h, 2)
    blur_m = box_blur_2d(box_blur_2d(lum, w, h, 4), w, h, 4)

    # Valley response: positive where pixel is darker than surrounding neighborhood
    valley = [0.0] * n
    for i in range(n):
        v1 = blur_s[i] - lum[i]
        v2 = blur_m[i] - lum[i]
        v = v1 if v1 > v2 else v2
        # Suppress very dark flat interior fills (like tie/mouth interior) unless near an edge:
        # In dark fills blur_s - lum is ~0 anyway!
        valley[i] = v if v > 0.0 else 0.0

    # Also detect sharp chromatic/luminance edges on high-contrast interior features
    # (like white teeth vs dark mouth, white specular highlights inside eyes, dark tie edge)
    # Using non-maximum-like ridge criterion so edges stay thin.
    edge_resp = [0.0] * n
    for y in range(1, h - 1):
        row = y * w
        for x in range(1, w - 1):
            idx = row + x
            # Max RGB gradient magnitude
            gx_r = r_ch[idx + 1] - r_ch[idx - 1]
            gy_r = r_ch[idx + w] - r_ch[idx - w]
            gx_g = g_ch[idx + 1] - g_ch[idx - 1]
            gy_g = g_ch[idx + w] - g_ch[idx - w]
            gx_b = b_ch[idx + 1] - b_ch[idx - 1]
            gy_b = b_ch[idx + w] - b_ch[idx - w]
            grad = math.sqrt(
                (gx_r * gx_r + gy_r * gy_r +
                 gx_g * gx_g + gy_g * gy_g +
                 gx_b * gx_b + gy_b * gy_b) / 3.0
            )
            # Only trigger pure color-edge where luminance jump is very large
            # AND pixel is on the darker side of the boundary (avoids double edges!)
            if grad > 55.0 and lum[idx] < blur_s[idx] - 4.0:
                edge_resp[idx] = grad * 0.45

    # Combined score
    score = [0.0] * n
    for i in range(n):
        s = valley[i]
        e = edge_resp[i]
        score[i] = s if s >= e else e

    # Hysteresis thresholding:
    # Strong ink strokes: score >= high_th
    # Weak connected strokes (e.g., delicate hair strands/eyebrows):
    # Blush in Anon's image is very soft (valley ~ 4-7), real thin hair lines have valley >= 11.
    high_th = 21.0
    low_th = 10.5

    mask = bytearray(n)
    q = deque()
    for y in range(1, h - 1):
        row = y * w
        for x in range(1, w - 1):
            idx = row + x
            if score[idx] >= high_th:
                mask[idx] = 1
                q.append((x, y))

    neighbors8 = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
    while q:
        cx, cy = q.popleft()
        for dx, dy in neighbors8:
            nx, ny = cx + dx, cy + dy
            if 1 <= nx < w - 1 and 1 <= ny < h - 1:
                nidx = ny * w + nx
                if mask[nidx] == 0 and score[nidx] >= low_th:
                    mask[nidx] = 1
                    q.append((nx, ny))

    # Morphological closing (tiny 1px bridge) to close micro-gaps in hair lines
    # Only fill a 0 pixel if it has >= 5 foreground 8-neighbors
    to_fill = []
    for y in range(1, h - 1):
        row = y * w
        for x in range(1, w - 1):
            idx = row + x
            if mask[idx] == 0:
                cnt = (
                    mask[idx - w - 1] + mask[idx - w] + mask[idx - w + 1] +
                    mask[idx - 1] + mask[idx + 1] +
                    mask[idx + w - 1] + mask[idx + w] + mask[idx + w + 1]
                )
                if cnt >= 5:
                    to_fill.append(idx)
    for idx in to_fill:
        mask[idx] = 1

    return mask, score


def zhang_suen_thinning(mask: bytearray, w: int, h: int) -> bytearray:
    """
    Fast active-set Zhang-Suen morphological thinning to obtain a 1-pixel skeleton.
    """
    img = bytearray(mask)
    active = [
        (x, y)
        for y in range(1, h - 1)
        for x in range(1, w - 1)
        if img[y * w + x]
    ]

    while True:
        changed = False
        for step in (0, 1):
            to_remove = []
            for x, y in active:
                idx = y * w + x
                if not img[idx]:
                    continue
                p2 = img[idx - w]
                p3 = img[idx - w + 1]
                p4 = img[idx + 1]
                p5 = img[idx + w + 1]
                p6 = img[idx + w]
                p7 = img[idx + w - 1]
                p8 = img[idx - 1]
                p9 = img[idx - w - 1]

                B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
                if B < 2 or B > 6:
                    continue

                A = (
                    (p2 == 0 and p3 == 1) +
                    (p3 == 0 and p4 == 1) +
                    (p4 == 0 and p5 == 1) +
                    (p5 == 0 and p6 == 1) +
                    (p6 == 0 and p7 == 1) +
                    (p7 == 0 and p8 == 1) +
                    (p8 == 0 and p9 == 1) +
                    (p9 == 0 and p2 == 1)
                )
                if A != 1:
                    continue

                if step == 0:
                    if (p2 * p4 * p6 == 0) and (p4 * p6 * p8 == 0):
                        to_remove.append(idx)
                else:
                    if (p2 * p4 * p8 == 0) and (p2 * p6 * p8 == 0):
                        to_remove.append(idx)

            if to_remove:
                changed = True
                for idx in to_remove:
                    img[idx] = 0
                active = [(x, y) for (x, y) in active if img[y * w + x]]

        if not changed:
            break

    # Cleanup: remove redundant 8-connected L-corner pixels (eliminates fake degree-3
    # pixel triangles along diagonal lines without breaking 8-connectivity).
    active = [
        (x, y)
        for y in range(1, h - 1)
        for x in range(1, w - 1)
        if img[y * w + x]
    ]
    for x, y in active:
        idx = y * w + x
        if not img[idx]:
            continue
        p2 = img[idx - w]
        p3 = img[idx - w + 1]
        p4 = img[idx + 1]
        p5 = img[idx + w + 1]
        p6 = img[idx + w]
        p7 = img[idx + w - 1]
        p8 = img[idx - 1]
        p9 = img[idx - w - 1]
        # Only remove if it forms a strict 4-connected L-corner whose deletion leaves
        # the 8-neighborhood 1-connected (transition count A == 1 and corner pair present).
        has_L = (
            (p2 and p4 and not p7) or
            (p4 and p6 and not p9) or
            (p6 and p8 and not p3) or
            (p8 and p2 and not p5)
        )
        if not has_L:
            continue
        # Check if remaining neighbors in 3x3 are a single 8-connected component
        nbs = []
        for dx, dy in ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)):
            if img[(y + dy) * w + (x + dx)]:
                nbs.append((dx, dy))
        if len(nbs) < 2:
            continue
        # BFS among nbs using 8-adjacency
        seen = {nbs[0]}
        stack = [nbs[0]]
        while stack:
            cx, cy = stack.pop()
            for q in nbs:
                if q not in seen and max(abs(q[0] - cx), abs(q[1] - cy)) <= 1:
                    seen.add(q)
                    stack.append(q)
        if len(seen) == len(nbs):
            img[idx] = 0

    return img


def trace_skeleton_polylines(
    skel: bytearray,
    w: int,
    h: int,
    min_chain_len: int = 8,
    spur_prune_len: int = 6,
) -> List[List[Tuple[float, float]]]:
    """
    Convert a 1-pixel binary skeleton into long, continuous, unbroken polylines:
      1. Prune tiny dead-end spurs (< spur_prune_len) attached to junctions.
      2. Tangent-guided continuous tracing: start from endpoints (deg==1), walk pixel by
         pixel, and at junctions (deg>=3) CONTINUE STRAIGHT along the most collinear
         unvisited branch instead of shattering the stroke!
      3. Secondary branches attach cleanly right up to the junction pixel (zero T-gaps).
      4. Trace remaining pure closed loops (pupils, irises, nose ring, highlights).
      5. Fast collinear gap bridging (<= 9 px) to fuse faint broken hair strokes.
    """
    pixels = set()
    for y in range(1, h - 1):
        row = y * w
        for x in range(1, w - 1):
            if skel[row + x]:
                pixels.add((x, y))

    nb8 = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))

    def get_neighbors(p: Tuple[int, int], pset: set) -> List[Tuple[int, int]]:
        x, y = p
        return [(x + dx, y + dy) for dx, dy in nb8 if (x + dx, y + dy) in pset]

    # 1. Iterative short spur pruning
    for _ in range(3):
        adj = {p: get_neighbors(p, pixels) for p in pixels}
        endpoints = [p for p, nbs in adj.items() if len(nbs) == 1]
        to_del = set()
        for ep in endpoints:
            if ep in to_del:
                continue
            path = [ep]
            prev = None
            curr = ep
            hit_junction = False
            while len(path) <= spur_prune_len:
                nbs = [q for q in adj[curr] if q != prev and q not in to_del]
                if not nbs:
                    break
                if len(nbs) >= 2:
                    hit_junction = True
                    break
                nxt = nbs[0]
                if len(adj[nxt]) >= 3:
                    hit_junction = True
                    break
                path.append(nxt)
                prev, curr = curr, nxt
            if hit_junction and len(path) <= spur_prune_len:
                to_del.update(path)
        if not to_del:
            break
        pixels -= to_del

    adj = {p: get_neighbors(p, pixels) for p in pixels}
    pixels = {p for p in pixels if len(adj[p]) >= 1}
    adj = {p: get_neighbors(p, pixels) for p in pixels}

    visited_edges = set()

    def ekey(a: Tuple[int, int], b: Tuple[int, int]):
        return (a, b) if a < b else (b, a)

    def choose_next(chain: List[Tuple[int, int]], candidates: List[Tuple[int, int]]) -> Tuple[int, int]:
        if len(candidates) == 1:
            return candidates[0]
        # Compute incoming tangent over last min(6, len-1) points
        curr = chain[-1]
        k = min(6, len(chain) - 1)
        vx = curr[0] - chain[-1 - k][0]
        vy = curr[1] - chain[-1 - k][1]
        L = math.hypot(vx, vy)
        if L < 1e-6:
            return candidates[0]
        ux, uy = vx / L, vy / L
        # Prefer candidate with best forward cosine alignment (tie-break: 4-neighbor before diagonal)
        best_q = candidates[0]
        best_sc = -2.0
        for q in candidates:
            dx = q[0] - curr[0]
            dy = q[1] - curr[1]
            dL = math.hypot(dx, dy)
            cos_a = (dx * ux + dy * uy) / dL
            sc = cos_a + (0.01 if dL < 1.1 else 0.0)
            if sc > best_sc:
                best_sc = sc
                best_q = q
        return best_q

    def trace_from(start: Tuple[int, int], first_nb: Tuple[int, int]) -> List[Tuple[int, int]]:
        chain = [start, first_nb]
        visited_edges.add(ekey(start, first_nb))
        in_chain = {start, first_nb}
        curr = first_nb
        while True:
            # Unvisited incident edges
            cands = [q for q in adj[curr] if ekey(curr, q) not in visited_edges]
            if not cands:
                break
            # Prefer continuing without immediately closing a tiny 3-pixel triangle
            non_local = [q for q in cands if q not in in_chain or (q == chain[0] and len(chain) >= 8)]
            if not non_local:
                break
            nxt = choose_next(chain, non_local)
            visited_edges.add(ekey(curr, nxt))
            chain.append(nxt)
            if nxt == chain[0] and len(chain) >= 9:
                break  # cleanly closed loop!
            if nxt in in_chain:
                break  # self-intersection
            in_chain.add(nxt)
            curr = nxt
        return chain

    raw_chains: List[List[Tuple[int, int]]] = []

    # Pass 1: Trace starting from endpoints (deg == 1) — produces long sweeping strokes!
    endpoints = sorted([p for p, nbs in adj.items() if len(nbs) == 1])
    for ep in endpoints:
        for nb in adj[ep]:
            if ekey(ep, nb) not in visited_edges:
                raw_chains.append(trace_from(ep, nb))

    # Pass 2: Trace remaining unvisited branches starting at junctions (deg >= 3)
    junctions = sorted([p for p, nbs in adj.items() if len(nbs) >= 3])
    for jp in junctions:
        for nb in adj[jp]:
            if ekey(jp, nb) not in visited_edges:
                raw_chains.append(trace_from(jp, nb))

    # Pass 3: Trace remaining pure closed loops (every pixel deg == 2)
    for p in sorted(pixels):
        for nb in adj[p]:
            if ekey(p, nb) not in visited_edges:
                raw_chains.append(trace_from(p, nb))

    # Pass 4: Fast collinear gap bridging (<= 9 px) to reconnect faint broken hair lines
    # Sort candidate pairs ONCE and merge greedily via Union-Find-style chain concatenation -> O(N^2) once (<0.03s)!
    chains: List[Optional[List[Tuple[int, int]]]] = [c for c in raw_chains if len(c) >= 4]
    cos_bridge = math.cos(math.radians(30.0))

    # Compute outgoing tips for open chains
    tips = []
    for idx, c in enumerate(chains):
        if c is None or len(c) < 5:
            continue
        if math.hypot(c[0][0] - c[-1][0], c[0][1] - c[-1][1]) <= 2.5 and len(c) >= 10:
            continue  # already closed
        k = min(6, len(c) - 1)
        dx0, dy0 = c[0][0] - c[k][0], c[0][1] - c[k][1]
        L0 = math.hypot(dx0, dy0)
        if L0 > 1e-6:
            tips.append((idx, True, c[0], (dx0 / L0, dy0 / L0)))
        dx1, dy1 = c[-1][0] - c[-1 - k][0], c[-1][1] - c[-1 - k][1]
        L1 = math.hypot(dx1, dy1)
        if L1 > 1e-6:
            tips.append((idx, False, c[-1], (dx1 / L1, dy1 / L1)))

    # Spatial bucket hash (cell size 12px) so neighbor lookup is O(N)!
    cell = 12
    buckets: Dict[Tuple[int, int], List[int]] = {}
    for ti, (_, _, (px, py), _) in enumerate(tips):
        buckets.setdefault((px // cell, py // cell), []).append(ti)

    pair_cands = []
    for ti, (ci, si, pi, di) in enumerate(tips):
        bx, by = pi[0] // cell, pi[1] // cell
        for dcx in (-1, 0, 1):
            for dcy in (-1, 0, 1):
                for tj in buckets.get((bx + dcx, by + dcy), ()):
                    if tj <= ti:
                        continue
                    cj, sj, pj, dj = tips[tj]
                    if ci == cj:
                        continue
                    gx = pj[0] - pi[0]
                    gy = pj[1] - pi[1]
                    dist = math.hypot(gx, gy)
                    if dist < 1.0 or dist > 9.0:
                        continue
                    ux, uy = gx / dist, gy / dist
                    a1 = di[0] * ux + di[1] * uy
                    a2 = -(dj[0] * ux + dj[1] * uy)
                    if a1 > cos_bridge and a2 > cos_bridge:
                        sc = (a1 + a2) - 0.06 * dist
                        pair_cands.append((sc, ti, tj))

    pair_cands.sort(reverse=True)
    used_tips = set()
    # Map original (chain_idx, at_start) -> current live chain_idx and whether reversed
    alive: Dict[int, List[Tuple[int, int]]] = {i: list(c) for i, c in enumerate(chains) if c is not None}
    # Track which live chain owns each original tip
    tip_owner = {ti: (tips[ti][0], tips[ti][1]) for ti in range(len(tips))}

    for _, ti, tj in pair_cands:
        if ti in used_tips or tj in used_tips:
            continue
        ci, si = tip_owner[ti]
        cj, sj = tip_owner[tj]
        if ci == cj or ci not in alive or cj not in alive:
            continue
        c1 = alive[ci]
        c2 = alive[cj]
        # Verify tip coordinates still match the actual ends of c1 and c2
        p1 = tips[ti][2]
        p2 = tips[tj][2]
        if c1[0] == p1:
            c1.reverse()
        elif c1[-1] != p1:
            continue
        if c2[-1] == p2:
            c2.reverse()
        elif c2[0] != p2:
            continue
        alive[ci] = c1 + c2
        del alive[cj]
        used_tips.add(ti)
        used_tips.add(tj)
        # Reassign surviving tips of cj to ci
        for tk in range(len(tips)):
            if tip_owner[tk][0] == cj:
                tip_owner[tk] = (ci, tip_owner[tk][1])

    # Final filter: keep all meaningful strokes & closed loops
    final_chains: List[List[Tuple[float, float]]] = []
    for c in alive.values():
        is_closed = (len(c) >= 8 and math.hypot(c[0][0] - c[-1][0], c[0][1] - c[-1][1]) <= 3.0)
        if is_closed or len(c) >= min_chain_len:
            final_chains.append([(float(x), float(y)) for x, y in c])

    return final_chains


if __name__ == "__main__":
    import time
    t0 = time.time()
    w, h, rgb = load_image_rgb(os.path.join(os.path.dirname(__file__), "..", "千早爱音.jpg"))
    print(f"Loaded image {w}x{h} in {time.time() - t0:.2f}s")
    t1 = time.time()
    mask, _ = extract_anime_lineart(w, h, rgb)
    print(f"Extracted lineart ({sum(mask)} px) in {time.time() - t1:.2f}s")
    t2 = time.time()
    skel = zhang_suen_thinning(mask, w, h)
    print(f"Thinned skeleton ({sum(skel)} px) in {time.time() - t2:.2f}s")
    t3 = time.time()
    chains = trace_skeleton_polylines(skel, w, h)
    print(f"Traced {len(chains)} polylines (total {sum(len(c) for c in chains)} pts) in {time.time() - t3:.2f}s")

    # Save diagnostic preview of skeleton
    out_rgb = bytearray([255] * (w * h * 3))
    for i in range(w * h):
        if skel[i]:
            out_rgb[i * 3] = 20
            out_rgb[i * 3 + 1] = 20
            out_rgb[i * 3 + 2] = 35
    preview_path = os.path.join(os.path.dirname(__file__), "_debug_skeleton.png")
    save_png_rgb(preview_path, w, h, out_rgb)
    print(f"Saved diagnostic skeleton preview to {preview_path}")
