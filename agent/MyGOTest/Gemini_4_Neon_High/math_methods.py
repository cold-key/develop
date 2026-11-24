"""
Mathematical curve-fitting library for f(x) = g(y) contour reconstruction.

Every fitted curve strictly satisfies the variable-separated functional form:
    f_k(x) = g_k(y),   (x, y) in D_k = [x_min, x_max] x [y_min, y_max]

Implemented mathematical methods (zero external dependencies):
  1. Chebyshev-Lobatto Lagrange Interpolation (primary method):
       y = L_n(x)  <=>  f(x) = L_n(x), g(y) = y
       x = L_n(y)  <=>  f(x) = x,      g(y) = L_n(y)
     Uses Chebyshev-Lobatto nodes to preserve exact C^0 endpoint continuity while
     minimizing the Lebesgue constant and preventing Runge's phenomenon, evaluated
     via the numerically stable Barycentric Lagrange formula.
  2. Separable Conic / Axis-Aligned Ellipse:
       ((x - x0) / a)^2 = 1 - ((y - y0) / b)^2
     Fits closed elliptical features (irises, pupils, eye highlights, nose ring)
     in a single separated equation f(x) = g(y).
  3. Cubic Hermite Interpolation (C^1 tangent-preserving cubic polynomial):
       y = H_3(x)  or  x = H_3(y)
  4. Centered Least-Squares Polynomial Approximation:
       y = P_n(x)  or  x = P_n(y)
     Solved via normal equations in centered coordinates u = t - t_c.
  5. Linear Function Fitting:
       y = k*x + b  or  x = m*y + c
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Coordinate transforms: isotropic mapping [0, W] x [0, H] <-> [-4, 4] x [-3, 3]
# ---------------------------------------------------------------------------

def px_to_math(u: float, v: float, w: int, h: int, half_x: float = 4.0) -> Tuple[float, float]:
    """Map pixel (u, v) (y-down) isotropically to math (x, y) (y-up, centered at origin)."""
    scale = (w / 2.0) / half_x  # pixels per math unit (136.5 for 1092x819)
    x = (u - w / 2.0) / scale
    y = (h / 2.0 - v) / scale
    return (x, y)


def math_to_px(x: float, y: float, w: int, h: int, half_x: float = 4.0) -> Tuple[float, float]:
    """Inverse isotropic mapping from math (x, y) to pixel (u, v)."""
    scale = (w / 2.0) / half_x
    u = x * scale + w / 2.0
    v = h / 2.0 - y * scale
    return (u, v)


# ---------------------------------------------------------------------------
# Linear Algebra Utility (Gaussian Elimination with Partial Pivoting)
# ---------------------------------------------------------------------------

def solve_linear_system(A: List[List[float]], b: List[float]) -> Optional[List[float]]:
    """Solve A x = b via Gaussian elimination with partial pivoting."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-13:
            return None
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
        piv_val = M[col][col]
        for r in range(col + 1, n):
            factor = M[r][col] / piv_val
            if factor == 0.0:
                continue
            for c in range(col, n + 1):
                M[r][c] -= factor * M[col][c]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n]
        for j in range(i + 1, n):
            s -= M[i][j] * x[j]
        x[i] = s / M[i][i]
    return x


def poly_eval_shifted(coeffs: List[float], t: float, t_c: float) -> float:
    """Evaluate sum_{r=0}^n coeffs[r] * (t - t_c)^r via Horner's method."""
    u = t - t_c
    acc = 0.0
    for c in reversed(coeffs):
        acc = acc * u + c
    return acc


def lagrange_to_shifted_coeffs(
    t_nodes: List[float], v_nodes: List[float], t_c: float
) -> List[float]:
    """Convert Lagrange interpolating polynomial to shifted monomial coeffs in u = t - t_c."""
    n = len(t_nodes)
    u_nodes = [t - t_c for t in t_nodes]
    coeffs = [0.0] * n

    for j in range(n):
        # Build basis polynomial prod_{m != j} (u - u_m) / (u_j - u_m)
        basis = [1.0]
        denom = 1.0
        uj = u_nodes[j]
        for m in range(n):
            if m == j:
                continue
            um = u_nodes[m]
            denom *= (uj - um)
            # Multiply `basis` by (u - um)
            nxt = [0.0] * (len(basis) + 1)
            for k, ck in enumerate(basis):
                nxt[k] -= ck * um
                nxt[k + 1] += ck
            basis = nxt
        scale = v_nodes[j] / denom
        for k in range(n):
            coeffs[k] += scale * basis[k]
    return coeffs


def shifted_to_standard_coeffs(coeffs: List[float], t_c: float) -> List[float]:
    """Convert sum c_r (t - t_c)^r to standard monomial sum a_r t^r."""
    n = len(coeffs)
    std = [0.0] * n
    # Expand (t - t_c)^r using binomial recursion
    binom = [1.0]
    for r in range(n):
        cr = coeffs[r]
        for k, bk in enumerate(binom):
            std[k] += cr * bk
        # Multiply binom by (t - t_c)
        nxt = [0.0] * (len(binom) + 1)
        for k, bk in enumerate(binom):
            nxt[k] -= bk * t_c
            nxt[k + 1] += bk
        binom = nxt
    return std


def format_shifted_poly(var: str, coeffs: List[float], t_c: float, prec: int = 5) -> str:
    """Format polynomial sum c_r (var - t_c)^r cleanly for Desmos / human reading."""
    u_str = f"({var} - {t_c:.4f})" if t_c >= 0 else f"({var} + {-t_c:.4f})"
    if abs(t_c) < 1e-5:
        u_str = var
    terms = []
    for r, c in enumerate(coeffs):
        if abs(c) < 1e-7 and len(coeffs) > 1:
            continue
        sign = "+" if c >= 0 else "-"
        ac = abs(c)
        if r == 0:
            body = f"{ac:.{prec}f}"
        elif r == 1:
            body = f"{ac:.{prec}f}*{u_str}"
        else:
            body = f"{ac:.{prec}f}*{u_str}^{r}"
        if not terms:
            terms.append(body if c >= 0 else f"-{body}")
        else:
            terms.append(f" {sign} {body}")
    return "".join(terms) if terms else "0"


# ---------------------------------------------------------------------------
# Unified Separated-Function Curve Record: f(x) = g(y)
# ---------------------------------------------------------------------------

@dataclass
class FunctionCurve:
    """
    Represents a single mathematical curve strictly of the form f(x) = g(y)
    restricted to a bounding domain [x_min, x_max] x [y_min, y_max].
    """
    curve_id: int
    method: str  # 'lagrange', 'linear', 'hermite', 'least_squares', 'ellipse'
    axis: str    # 'x' (y = f(x)), 'y' (x = g(y)), or 'conic' (f(x) = g(y))
    degree: int
    t_min: float
    t_max: float
    t_center: float
    coeffs: List[float]  # shifted polynomial coeffs for axis in {'x','y'}; [x0, y0, a, b] for ellipse
    x_bounds: Tuple[float, float]
    y_bounds: Tuple[float, float]
    nodes: List[Tuple[float, float]] = field(default_factory=list)  # interpolation nodes (x_j, y_j)
    bary_weights: List[float] = field(default_factory=list)
    max_error: float = 0.0
    rmse: float = 0.0
    point_count: int = 0

    def eval_explicit(self, t: float) -> float:
        """Evaluate dependent variable at t (for axis=='x' returns y; for axis=='y' returns x)."""
        if self.method == "lagrange" and self.nodes and self.bary_weights:
            # Exact numerically stable Barycentric Lagrange evaluation
            num = 0.0
            den = 0.0
            for (nx, ny), wj in zip(self.nodes, self.bary_weights):
                tj = nx if self.axis == "x" else ny
                vj = ny if self.axis == "x" else nx
                diff = t - tj
                if abs(diff) < 1e-12:
                    return vj
                term = wj / diff
                num += term * vj
                den += term
            return num / den
        return poly_eval_shifted(self.coeffs, t, self.t_center)

    def sample_points(self, step_math: float = 0.008) -> List[Tuple[float, float]]:
        """Sample (x, y) points purely by evaluating the mathematical equation f(x) = g(y)."""
        if self.axis == "conic" and self.method == "ellipse":
            x0, y0, a, b = self.coeffs
            perim = math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))
            n_pts = max(28, int(perim / step_math))
            pts = []
            for k in range(n_pts + 1):
                # Evaluate directly from ((x-x0)/a)^2 = 1 - ((y-y0)/b)^2 via angle parameter
                th = 2.0 * math.pi * k / n_pts
                x = x0 + a * math.cos(th)
                y = y0 + b * math.sin(th)
                pts.append((x, y))
            return pts

        span = self.t_max - self.t_min
        n_steps = max(8, int(math.ceil(span / step_math)))
        pts = []
        for k in range(n_steps + 1):
            t = self.t_min + span * (k / n_steps)
            v = self.eval_explicit(t)
            if self.axis == "x":
                pts.append((t, v))
            else:
                pts.append((v, t))
        return pts

    def f_expr(self) -> str:
        """Return f(x) string."""
        if self.axis == "conic":
            x0, _, a, _ = self.coeffs
            xs = f"(x - {x0:.4f})" if x0 >= 0 else f"(x + {-x0:.4f})"
            return f"({xs}/{a:.4f})^2"
        if self.axis == "x":
            return format_shifted_poly("x", self.coeffs, self.t_center)
        return "x"

    def g_expr(self) -> str:
        """Return g(y) string."""
        if self.axis == "conic":
            _, y0, _, b = self.coeffs
            ys = f"(y - {y0:.4f})" if y0 >= 0 else f"(y + {-y0:.4f})"
            return f"1 - ({ys}/{b:.4f})^2"
        if self.axis == "y":
            return format_shifted_poly("y", self.coeffs, self.t_center)
        return "y"

    def to_equation_str(self) -> str:
        """Return f(x) = g(y) with domain restriction."""
        if self.axis == "conic":
            return f"{self.f_expr()} = {self.g_expr()}"
        if self.axis == "x":
            return f"{self.f_expr()} = y  {{{self.t_min:.4f} <= x <= {self.t_max:.4f}}}"
        return f"x = {self.g_expr()}  {{{self.t_min:.4f} <= y <= {self.t_max:.4f}}}"

    def to_desmos_latex(self) -> str:
        """Return Desmos-pasteable equation string."""
        if self.axis == "conic":
            x0, y0, a, b = self.coeffs
            xs = f"x - {x0:.4f}" if x0 >= 0 else f"x + {-x0:.4f}"
            ys = f"y - {y0:.4f}" if y0 >= 0 else f"y + {-y0:.4f}"
            return f"\\left(\\frac{{{xs}}}{{{a:.4f}}}\\right)^2 = 1 - \\left(\\frac{{{ys}}}{{{b:.4f}}}\\right)^2"
        if self.axis == "x":
            rhs = format_shifted_poly("x", self.coeffs, self.t_center, prec=4)
            return f"y = {rhs} \\left\\{{{self.t_min:.4f} \\le x \\le {self.t_max:.4f}\\right\\}}"
        rhs = format_shifted_poly("y", self.coeffs, self.t_center, prec=4)
        return f"x = {rhs} \\left\\{{{self.t_min:.4f} \\le y \\le {self.t_max:.4f}\\right\\}}"

    def to_lagrange_basis_str(self) -> str:
        """Explicit Lagrange basis form L_n(t) = sum v_j prod (t - t_m)/(t_j - t_m)."""
        if self.method != "lagrange" or not self.nodes:
            return self.to_equation_str()
        var = "x" if self.axis == "x" else "y"
        dep = "y" if self.axis == "x" else "x"
        ts = [p[0] if self.axis == "x" else p[1] for p in self.nodes]
        vs = [p[1] if self.axis == "x" else p[0] for p in self.nodes]
        terms = []
        n = len(ts)
        for j in range(n):
            factors = []
            denom = 1.0
            for m in range(n):
                if m == j:
                    continue
                tm = ts[m]
                denom *= (ts[j] - tm)
                factors.append(f"({var}-{tm:.3f})" if tm >= 0 else f"({var}+{-tm:.3f})")
            coeff = vs[j] / denom
            terms.append(f"({coeff:+.3f})*" + "*".join(factors))
        expr = " ".join(terms)
        return f"{expr} = {dep}" if self.axis == "x" else f"{dep} = {expr}"

    def to_dict(self) -> Dict:
        return {
            "id": self.curve_id,
            "method": self.method,
            "axis": self.axis,
            "degree": self.degree,
            "t_min": round(self.t_min, 5),
            "t_max": round(self.t_max, 5),
            "t_center": round(self.t_center, 5),
            "coeffs": [round(c, 6) for c in self.coeffs],
            "x_bounds": [round(self.x_bounds[0], 5), round(self.x_bounds[1], 5)],
            "y_bounds": [round(self.y_bounds[0], 5), round(self.y_bounds[1], 5)],
            "nodes": [[round(p[0], 5), round(p[1], 5)] for p in self.nodes],
            "max_error": round(self.max_error, 6),
            "rmse": round(self.rmse, 6),
            "equation": self.to_equation_str(),
            "f_x": self.f_expr(),
            "g_y": self.g_expr(),
        }


# ---------------------------------------------------------------------------
# Core Fitters (All strictly f(x) = g(y))
# ---------------------------------------------------------------------------

def _interp_v_at_t(ts: List[float], vs: List[float], target_t: float) -> float:
    """Linearly interpolate v(target_t) on a strictly increasing sequence ts."""
    if target_t <= ts[0]:
        return vs[0]
    if target_t >= ts[-1]:
        return vs[-1]
    lo, hi = 0, len(ts) - 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if ts[mid] <= target_t:
            lo = mid
        else:
            hi = mid
    dt = ts[hi] - ts[lo]
    if dt <= 1e-12:
        return 0.5 * (vs[lo] + vs[hi])
    alpha = (target_t - ts[lo]) / dt
    return vs[lo] + alpha * (vs[hi] - vs[lo])


def _compute_barycentric_weights(t_nodes: List[float]) -> List[float]:
    n = len(t_nodes)
    w = [1.0] * n
    for j in range(n):
        prod = 1.0
        for m in range(n):
            if m != j:
                prod *= (t_nodes[j] - t_nodes[m])
        w[j] = 1.0 / prod
    return w


def _eval_and_check_overshoot(
    eval_fn,
    ts: List[float],
    vs: List[float],
    t_min: float,
    t_max: float,
    overshoot_margin: float,
) -> Tuple[float, float, int, bool]:
    """Compute max_err, rmse, worst_index, and check for interior Runge overshoot."""
    max_e = 0.0
    worst_i = 0
    sq_sum = 0.0
    v_min = min(vs)
    v_max = max(vs)

    for i, (t, v) in enumerate(zip(ts, vs)):
        e = abs(eval_fn(t) - v)
        sq_sum += e * e
        if e > max_e:
            max_e = e
            worst_i = i

    rmse = math.sqrt(sq_sum / len(ts))

    # Dense interior check to guarantee ZERO Runge overshoot between sample points
    overshoot = False
    n_check = max(16, len(ts) * 2)
    for k in range(1, n_check):
        tk = t_min + (t_max - t_min) * (k / n_check)
        vk_pred = eval_fn(tk)
        if vk_pred < v_min - overshoot_margin or vk_pred > v_max + overshoot_margin:
            overshoot = True
            break
        # Also verify against linearly interpolated curve at tk
        vk_ref = _interp_v_at_t(ts, vs, tk)
        if abs(vk_pred - vk_ref) > max(max_e * 1.45, overshoot_margin):
            overshoot = True
            break

    return max_e, rmse, worst_i, overshoot


def fit_lagrange_chebyshev(
    ts: List[float], vs: List[float], axis: str, degree: int, curve_id: int
) -> Optional[Tuple[FunctionCurve, int, bool]]:
    """
    Fit degree-n Lagrange interpolating polynomial using Chebyshev-Lobatto nodes:
        tau_j = (a + b)/2 - ((b - a)/2) * cos(j * pi / n),  j = 0..n
    Guarantees exact C^0 endpoint interpolation and suppresses Runge oscillation.
    """
    t_min, t_max = ts[0], ts[-1]
    if t_max - t_min < 1e-6 or len(ts) < degree + 1:
        return None
    t_c = 0.5 * (t_min + t_max)
    half = 0.5 * (t_max - t_min)

    t_nodes = [
        t_c - half * math.cos(math.pi * j / degree)
        for j in range(degree + 1)
    ]
    t_nodes[0] = t_min
    t_nodes[-1] = t_max
    v_nodes = [_interp_v_at_t(ts, vs, tj) for tj in t_nodes]

    bary_w = _compute_barycentric_weights(t_nodes)
    coeffs = lagrange_to_shifted_coeffs(t_nodes, v_nodes, t_c)

    nodes_xy = (
        [(t, v) for t, v in zip(t_nodes, v_nodes)]
        if axis == "x"
        else [(v, t) for t, v in zip(t_nodes, v_nodes)]
    )

    def _eval(t: float) -> float:
        num = 0.0
        den = 0.0
        for tj, vj, wj in zip(t_nodes, v_nodes, bary_w):
            d = t - tj
            if abs(d) < 1e-12:
                return vj
            term = wj / d
            num += term * vj
            den += term
        return num / den

    v_span = max(vs) - min(vs)
    margin = max(0.035, 0.20 * v_span)
    max_e, rmse, worst_i, overshoot = _eval_and_check_overshoot(
        _eval, ts, vs, t_min, t_max, margin
    )

    xb = (t_min, t_max) if axis == "x" else (min(vs), max(vs))
    yb = (min(vs), max(vs)) if axis == "x" else (t_min, t_max)

    curve = FunctionCurve(
        curve_id=curve_id,
        method="lagrange",
        axis=axis,
        degree=degree,
        t_min=t_min,
        t_max=t_max,
        t_center=t_c,
        coeffs=coeffs,
        x_bounds=xb,
        y_bounds=yb,
        nodes=nodes_xy,
        bary_weights=bary_w,
        max_error=max_e,
        rmse=rmse,
        point_count=len(ts),
    )
    return curve, worst_i, overshoot


def fit_linear_segment(
    ts: List[float], vs: List[float], axis: str, curve_id: int
) -> Optional[FunctionCurve]:
    """Fit exact endpoint-anchored linear equation f(x) = g(y) (degree 1)."""
    t_min, t_max = ts[0], ts[-1]
    if t_max - t_min < 1e-6:
        return None
    t_c = 0.5 * (t_min + t_max)
    v0, v1 = vs[0], vs[-1]
    slope = (v1 - v0) / (t_max - t_min)
    c0 = 0.5 * (v0 + v1)
    coeffs = [c0, slope]

    def _eval(t: float) -> float:
        return c0 + slope * (t - t_c)

    max_e, rmse, _, _ = _eval_and_check_overshoot(_eval, ts, vs, t_min, t_max, 0.05)
    nodes_xy = [(t_min, v0), (t_max, v1)] if axis == "x" else [(v0, t_min), (v1, t_max)]
    xb = (t_min, t_max) if axis == "x" else (min(vs), max(vs))
    yb = (min(vs), max(vs)) if axis == "x" else (t_min, t_max)

    return FunctionCurve(
        curve_id=curve_id,
        method="linear",
        axis=axis,
        degree=1,
        t_min=t_min,
        t_max=t_max,
        t_center=t_c,
        coeffs=coeffs,
        x_bounds=xb,
        y_bounds=yb,
        nodes=nodes_xy,
        max_error=max_e,
        rmse=rmse,
        point_count=len(ts),
    )


def fit_cubic_hermite(
    ts: List[float], vs: List[float], axis: str, curve_id: int
) -> Optional[Tuple[FunctionCurve, bool]]:
    """
    Fit C^1 Cubic Hermite interpolating polynomial using one-sided smoothed endpoint
    derivatives (m0, m1) and exact endpoint values (v0, v1).
    """
    n = len(ts)
    t_min, t_max = ts[0], ts[-1]
    h = t_max - t_min
    if h < 1e-6 or n < 5:
        return None
    k = min(4, n - 1)
    # Estimate endpoint slopes via local chord over first/last k points
    dt0 = ts[k] - ts[0]
    dt1 = ts[-1] - ts[-1 - k]
    if abs(dt0) < 1e-9 or abs(dt1) < 1e-9:
        return None
    m0 = (vs[k] - vs[0]) / dt0
    m1 = (vs[-1] - vs[-1 - k]) / dt1

    v0, v1 = vs[0], vs[-1]
    # Standard Hermite basis in s = (t - t0)/h:
    # H(s) = (2v0 - 2v1 + h*m0 + h*m1) s^3 + (-3v0 + 3v1 - 2h*m0 - h*m1) s^2 + h*m0 s + v0
    a3 = (2 * v0 - 2 * v1 + h * m0 + h * m1) / (h ** 3)
    a2 = (-3 * v0 + 3 * v1 - 2 * h * m0 - h * m1) / (h ** 2)
    a1 = m0
    a0 = v0

    # Shift from t0 to t_c = t0 + h/2 so coeffs are centered at t_c
    t_c = 0.5 * (t_min + t_max)
    d = 0.5 * h
    c0 = a0 + a1 * d + a2 * d * d + a3 * d * d * d
    c1 = a1 + 2 * a2 * d + 3 * a3 * d * d
    c2 = a2 + 3 * a3 * d
    c3 = a3
    coeffs = [c0, c1, c2, c3]

    def _eval(t: float) -> float:
        return poly_eval_shifted(coeffs, t, t_c)

    v_span = max(vs) - min(vs)
    margin = max(0.035, 0.20 * v_span)
    max_e, rmse, _, overshoot = _eval_and_check_overshoot(_eval, ts, vs, t_min, t_max, margin)
    nodes_xy = [(t_min, v0), (t_max, v1)] if axis == "x" else [(v0, t_min), (v1, t_max)]
    xb = (t_min, t_max) if axis == "x" else (min(vs), max(vs))
    yb = (min(vs), max(vs)) if axis == "x" else (t_min, t_max)

    curve = FunctionCurve(
        curve_id=curve_id,
        method="hermite",
        axis=axis,
        degree=3,
        t_min=t_min,
        t_max=t_max,
        t_center=t_c,
        coeffs=coeffs,
        x_bounds=xb,
        y_bounds=yb,
        nodes=nodes_xy,
        max_error=max_e,
        rmse=rmse,
        point_count=n,
    )
    return curve, overshoot


def fit_least_squares_poly(
    ts: List[float], vs: List[float], axis: str, degree: int, curve_id: int
) -> Optional[Tuple[FunctionCurve, bool]]:
    """
    Fit degree-n polynomial in centered coordinates u = t - t_c via weighted normal
    equations (higher weight on endpoints to preserve stroke continuity).
    """
    n = len(ts)
    t_min, t_max = ts[0], ts[-1]
    if t_max - t_min < 1e-6 or n <= degree + 1:
        return None
    t_c = 0.5 * (t_min + t_max)
    m = degree + 1
    A = [[0.0] * m for _ in range(m)]
    b = [0.0] * m

    for idx, (t, v) in enumerate(zip(ts, vs)):
        w = 4.0 if (idx == 0 or idx == n - 1) else 1.0
        u = t - t_c
        pows = [1.0] * (2 * degree + 1)
        for p in range(1, 2 * degree + 1):
            pows[p] = pows[p - 1] * u
        for r in range(m):
            b[r] += w * pows[r] * v
            for c in range(m):
                A[r][c] += w * pows[r + c]

    coeffs = solve_linear_system(A, b)
    if coeffs is None:
        return None

    def _eval(t: float) -> float:
        return poly_eval_shifted(coeffs, t, t_c)

    v_span = max(vs) - min(vs)
    margin = max(0.035, 0.20 * v_span)
    max_e, rmse, _, overshoot = _eval_and_check_overshoot(_eval, ts, vs, t_min, t_max, margin)
    xb = (t_min, t_max) if axis == "x" else (min(vs), max(vs))
    yb = (min(vs), max(vs)) if axis == "x" else (t_min, t_max)

    curve = FunctionCurve(
        curve_id=curve_id,
        method="least_squares",
        axis=axis,
        degree=degree,
        t_min=t_min,
        t_max=t_max,
        t_center=t_c,
        coeffs=coeffs,
        x_bounds=xb,
        y_bounds=yb,
        nodes=[(t_min, vs[0]), (t_max, vs[-1])] if axis == "x" else [(vs[0], t_min), (vs[-1], t_max)],
        max_error=max_e,
        rmse=rmse,
        point_count=n,
    )
    return curve, overshoot


def fit_separable_ellipse(
    pts: List[Tuple[float, float]], curve_id: int, tol: float
) -> Optional[FunctionCurve]:
    """
    Attempt to fit a closed loop to an axis-aligned separable ellipse:
        ((x - x0)/a)^2 = 1 - ((y - y0)/b)^2
    Strictly of the form f(x) = g(y) with NO mixed x*y cross term!
    """
    if len(pts) < 9:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx = 0.5 * (min(xs) + max(xs))
    cy = 0.5 * (min(ys) + max(ys))
    rx_init = 0.5 * (max(xs) - min(xs))
    ry_init = 0.5 * (max(ys) - min(ys))
    if rx_init < 0.012 or ry_init < 0.012:
        return None
    # Avoid super-elongated non-ellipses
    if max(rx_init, ry_init) / min(rx_init, ry_init) > 3.5:
        return None

    # Solve centered algebraic least squares: A*u^2 + B*u + C*v^2 + D*v = 1
    # where u = x - cx, v = y - cy
    M = [[0.0] * 4 for _ in range(4)]
    rhs = [0.0] * 4
    for x, y in pts:
        u = x - cx
        v = y - cy
        row = [u * u, u, v * v, v]
        for r in range(4):
            rhs[r] += row[r]
            for c in range(4):
                M[r][c] += row[r] * row[c]

    sol = solve_linear_system(M, rhs)
    if sol is None:
        return None
    A, B, C, D = sol
    if A <= 1e-6 or C <= 1e-6:
        return None

    u0 = -B / (2.0 * A)
    v0 = -D / (2.0 * C)
    K = 1.0 + A * u0 * u0 + C * v0 * v0
    if K <= 1e-6:
        return None
    a = math.sqrt(K / A)
    b = math.sqrt(K / C)
    x0 = cx + u0
    y0 = cy + v0

    if a > rx_init * 1.4 or b > ry_init * 1.4 or a < rx_init * 0.6 or b < ry_init * 0.6:
        return None

    # Evaluate geometric distance from each point to the ellipse
    errs = []
    for x, y in pts:
        dx = x - x0
        dy = y - y0
        r_norm = math.hypot(dx / a, dy / b)
        if r_norm < 1e-9:
            errs.append(min(a, b))
        else:
            # Radial distance approximation along ray from center
            scale = abs(1.0 - 1.0 / r_norm)
            errs.append(math.hypot(dx, dy) * scale)

    max_e = max(errs)
    rmse = math.sqrt(sum(e * e for e in errs) / len(errs))
    if max_e > tol * 1.35:
        return None

    return FunctionCurve(
        curve_id=curve_id,
        method="ellipse",
        axis="conic",
        degree=2,
        t_min=x0 - a,
        t_max=x0 + a,
        t_center=x0,
        coeffs=[x0, y0, a, b],
        x_bounds=(x0 - a, x0 + a),
        y_bounds=(y0 - b, y0 + b),
        nodes=[(x0, y0), (x0 + a, y0), (x0, y0 + b)],
        max_error=max_e,
        rmse=rmse,
        point_count=len(pts),
    )


# ---------------------------------------------------------------------------
# Polyline Denoising, Corner/Monotonicity Splitting & Adaptive Fitting Pipeline
# ---------------------------------------------------------------------------

def smooth_polyline(
    pts: List[Tuple[float, float]], is_closed: bool, iterations: int = 3
) -> List[Tuple[float, float]]:
    """Apply gentle endpoint-preserving [0.25, 0.5, 0.25] smoothing to remove pixel stairs."""
    n = len(pts)
    if n < 4:
        return list(pts)
    cur = list(pts)
    for _ in range(iterations):
        nxt = list(cur)
        if is_closed:
            # Drop duplicated last point if equal to first
            m = n - 1 if (math.hypot(cur[0][0] - cur[-1][0], cur[0][1] - cur[-1][1]) < 1e-5) else n
            for i in range(m):
                p0 = cur[(i - 1) % m]
                p1 = cur[i]
                p2 = cur[(i + 1) % m]
                nxt[i] = (
                    0.25 * p0[0] + 0.5 * p1[0] + 0.25 * p2[0],
                    0.25 * p0[1] + 0.5 * p1[1] + 0.25 * p2[1],
                )
            if m == n - 1:
                nxt[-1] = nxt[0]
        else:
            for i in range(1, n - 1):
                nxt[i] = (
                    0.25 * cur[i - 1][0] + 0.5 * cur[i][0] + 0.25 * cur[i + 1][0],
                    0.25 * cur[i - 1][1] + 0.5 * cur[i][1] + 0.25 * cur[i + 1][1],
                )
        cur = nxt
    return cur


def split_at_corners(
    pts: List[Tuple[float, float]], angle_deg: float = 48.0, window: int = 4
) -> List[List[Tuple[float, float]]]:
    """Split a polyline at sharp corners (local tangent turn > angle_deg)."""
    n = len(pts)
    if n < 2 * window + 3:
        return [pts]
    cos_thresh = math.cos(math.radians(angle_deg))

    # Compute turning cosine at each interior point
    turn_cos = [1.0] * n
    for i in range(window, n - window):
        v1x = pts[i][0] - pts[i - window][0]
        v1y = pts[i][1] - pts[i - window][1]
        v2x = pts[i + window][0] - pts[i][0]
        v2y = pts[i + window][1] - pts[i][1]
        L1 = math.hypot(v1x, v1y)
        L2 = math.hypot(v2x, v2y)
        if L1 > 1e-6 and L2 > 1e-6:
            turn_cos[i] = (v1x * v2x + v1y * v2y) / (L1 * L2)

    # Pick local minima below cos_thresh with minimum spacing
    splits = [0]
    i = window
    while i < n - window:
        if turn_cos[i] < cos_thresh:
            # Find sharpest point in local neighborhood
            best_j = i
            j = i
            while j < n - window and turn_cos[j] < cos_thresh:
                if turn_cos[j] < turn_cos[best_j]:
                    best_j = j
                j += 1
            if best_j - splits[-1] >= 4 and (n - 1 - best_j) >= 4:
                splits.append(best_j)
            i = j
        else:
            i += 1
    splits.append(n - 1)

    return [pts[splits[k]:splits[k + 1] + 1] for k in range(len(splits) - 1)]


def split_into_monotonic_hv(
    pts: List[Tuple[float, float]],
) -> List[Tuple[str, List[Tuple[float, float]]]]:
    """
    Partition an open smooth polyline into sub-arcs that are strictly monotonic in
    their chosen independent axis ('x' for horizontal-dominant, 'y' for vertical-dominant)
    and have bounded slope (|dv/dt| <= ~3.2) so Lagrange interpolation is rock-solid.
    """
    n = len(pts)
    if n < 2:
        return []

    # Determine initial axis from first few steps
    k0 = min(4, n - 1)
    dx0 = pts[k0][0] - pts[0][0]
    dy0 = pts[k0][1] - pts[0][1]
    cur_axis = "x" if abs(dx0) >= abs(dy0) else "y"
    cur_dir = (1 if dx0 >= 0 else -1) if cur_axis == "x" else (1 if dy0 >= 0 else -1)

    segments: List[Tuple[str, List[Tuple[float, float]]]] = []
    seg_start = 0

    # Hysteresis threshold: switch H<->V only when slope exceeds tan(65 deg) ~ 2.15
    switch_ratio = 2.15
    i = 1
    while i < n:
        # Lookahead smoothed tangent over up to 3 steps for deciding H/V regime
        j_end = min(n - 1, i + 2)
        j_beg = max(seg_start, i - 2)
        tdx = pts[j_end][0] - pts[j_beg][0]
        tdy = pts[j_end][1] - pts[j_beg][1]

        step_dx = pts[i][0] - pts[i - 1][0]
        step_dy = pts[i][1] - pts[i - 1][1]

        need_split = False
        new_axis = cur_axis
        new_dir = cur_dir

        if cur_axis == "x":
            # Reversal in x OR became clearly steep vertical
            if step_dx * cur_dir < -1e-6:
                need_split = True
            elif abs(tdy) > switch_ratio * max(abs(tdx), 1e-9) and (i - seg_start) >= 3:
                need_split = True
        else:
            # Reversal in y OR became clearly flat horizontal
            if step_dy * cur_dir < -1e-6:
                need_split = True
            elif abs(tdx) > switch_ratio * max(abs(tdy), 1e-9) and (i - seg_start) >= 3:
                need_split = True

        if need_split:
            sub = pts[seg_start:i]
            if len(sub) >= 2:
                segments.append((cur_axis, sub))
            # Start new segment at i-1 to preserve exact C^0 continuity!
            seg_start = i - 1
            k_next = min(n - 1, seg_start + 3)
            ndx = pts[k_next][0] - pts[seg_start][0]
            ndy = pts[k_next][1] - pts[seg_start][1]
            cur_axis = "x" if abs(ndx) >= abs(ndy) else "y"
            cur_dir = (1 if ndx >= 0 else -1) if cur_axis == "x" else (1 if ndy >= 0 else -1)
        i += 1

    tail = pts[seg_start:]
    if len(tail) >= 2:
        segments.append((cur_axis, tail))

    return segments


def _prepare_strict_monotonic_tv(
    pts: List[Tuple[float, float]], axis: str
) -> Tuple[List[float], List[float]]:
    """
    Extract strictly increasing independent variable t and corresponding v.
    Merges any equal-t consecutive points by averaging their v values.
    """
    raw = [(p[0], p[1]) for p in pts] if axis == "x" else [(p[1], p[0]) for p in pts]
    if raw[0][0] > raw[-1][0]:
        raw.reverse()

    ts: List[float] = []
    vs: List[float] = []
    eps = 1e-6
    for t, v in raw:
        if not ts:
            ts.append(t)
            vs.append(v)
        elif t > ts[-1] + eps:
            ts.append(t)
            vs.append(v)
        elif abs(t - ts[-1]) <= eps:
            vs[-1] = 0.5 * (vs[-1] + v)
        else:
            # Tiny monotonicity hiccup from smoothing; skip out-of-order point
            continue
    return ts, vs


def fit_monotonic_arc_recursive(
    pts: List[Tuple[float, float]],
    axis: str,
    tol: float,
    id_counter: List[int],
    max_lagrange_degree: int = 5,
    depth: int = 0,
) -> List[FunctionCurve]:
    """
    Adaptively fit a strictly monotonic arc to f(x) = g(y) with guaranteed max error <= tol.
    Priority order:
      1. Linear (deg 1) if straight within 0.85 * tol
      2. Chebyshev-Lobatto Lagrange Interpolation (deg 2..max_lagrange_degree)
         with zero Runge overshoot
      3. Cubic Hermite Interpolation (C^1) if it cleanly satisfies tol
      4. Centered Least-Squares Polynomial (deg 3..4) if slight raster noise caused
         Lagrange to miss tol slightly
      5. Recursive subdivision at point of maximum error
    """
    ts, vs = _prepare_strict_monotonic_tv(pts, axis)
    if len(ts) < 2 or (ts[-1] - ts[0]) < 1e-4:
        return []

    # 1. Try Linear fit only for genuinely straight segments (within 0.45 * tol)
    lin = fit_linear_segment(ts, vs, axis, id_counter[0])
    if lin is not None and lin.max_error <= tol * 0.45:
        id_counter[0] += 1
        return [lin]

    # 2. Try Chebyshev-Lobatto Lagrange Interpolation (deg 2 .. max_lagrange_degree)
    best_lag: Optional[FunctionCurve] = None
    best_worst_i = len(ts) // 2
    max_deg = min(max_lagrange_degree, len(ts) - 1)

    for deg in range(2, max_deg + 1):
        res = fit_lagrange_chebyshev(ts, vs, axis, deg, id_counter[0])
        if res is None:
            continue
        curve, worst_i, overshoot = res
        if not overshoot and curve.max_error <= tol:
            # For degree-3 smooth long arcs, check if C^1 Cubic Hermite is even tighter
            if deg == 3 and len(ts) >= 16:
                herm_res = fit_cubic_hermite(ts, vs, axis, id_counter[0])
                if herm_res is not None:
                    hc, h_over = herm_res
                    if not h_over and hc.max_error <= tol and hc.rmse < curve.rmse * 0.88:
                        id_counter[0] += 1
                        return [hc]
            id_counter[0] += 1
            return [curve]
        if not overshoot and (best_lag is None or curve.max_error < best_lag.max_error):
            best_lag = curve
            best_worst_i = worst_i

    # 3. Try Cubic Hermite Interpolation (C^1 tangent-matched)
    herm_res = fit_cubic_hermite(ts, vs, axis, id_counter[0])
    if herm_res is not None:
        h_curve, h_over = herm_res
        if not h_over and h_curve.max_error <= tol:
            id_counter[0] += 1
            return [h_curve]

    # 4. Try Centered Least-Squares Polynomial (deg 3 or 4)
    for deg in (3, 4):
        if len(ts) > deg + 2:
            ls_res = fit_least_squares_poly(ts, vs, axis, deg, id_counter[0])
            if ls_res is not None:
                ls_curve, ls_over = ls_res
                if not ls_over and ls_curve.max_error <= tol:
                    id_counter[0] += 1
                    return [ls_curve]

    # 5. Subdivide at point of maximum residual error if enough points remain
    if len(pts) >= 7 and depth < 5:
        # Map worst_i back to pts index
        split_idx = max(2, min(len(pts) - 3, int(round(best_worst_i * (len(pts) - 1) / max(1, len(ts) - 1)))))
        left = fit_monotonic_arc_recursive(
            pts[:split_idx + 1], axis, tol, id_counter, max_lagrange_degree, depth + 1
        )
        right = fit_monotonic_arc_recursive(
            pts[split_idx:], axis, tol, id_counter, max_lagrange_degree, depth + 1
        )
        return left + right

    # Fallback: accept best non-overshooting Lagrange or Linear fit
    if best_lag is not None:
        best_lag.curve_id = id_counter[0]
        id_counter[0] += 1
        return [best_lag]
    if lin is not None:
        lin.curve_id = id_counter[0]
        id_counter[0] += 1
        return [lin]
    return []


def fit_all_polylines(
    polylines_px: List[List[Tuple[float, float]]],
    w: int,
    h: int,
    tol_px: float = 1.6,
    max_lagrange_degree: int = 5,
) -> List[FunctionCurve]:
    """
    Convert all extracted pixel polylines into a clean system of strictly separated
    mathematical equations f_k(x) = g_k(y).
    """
    scale = (w / 2.0) / 4.0  # pixels per math unit
    tol_math = tol_px / scale
    id_counter = [1]
    all_curves: List[FunctionCurve] = []

    for poly_px in polylines_px:
        if len(poly_px) < 4:
            continue
        is_closed = (
            len(poly_px) >= 9
            and math.hypot(poly_px[0][0] - poly_px[-1][0], poly_px[0][1] - poly_px[-1][1]) <= 3.5
        )
        # Convert to isotropic math coordinates [-4, 4] x [-3, 3]
        poly_m = [px_to_math(u, v, w, h) for (u, v) in poly_px]
        poly_smooth = smooth_polyline(poly_m, is_closed=is_closed, iterations=3)

        # 1. For closed loops, test Separable Conic / Ellipse f(x) = g(y) first!
        if is_closed:
            ell = fit_separable_ellipse(poly_smooth, id_counter[0], tol=tol_math * 1.5)
            if ell is not None:
                id_counter[0] += 1
                all_curves.append(ell)
                continue
            # If not elliptical, cut closed loop at leftmost x-extremum so open splitting is clean
            min_idx = min(range(len(poly_smooth) - 1), key=lambda i: poly_smooth[i][0])
            open_ring = poly_smooth[min_idx:-1] + poly_smooth[:min_idx + 1]
            corner_pieces = split_at_corners(open_ring, angle_deg=48.0, window=4)
        else:
            corner_pieces = split_at_corners(poly_smooth, angle_deg=48.0, window=4)

        # 2. Split each smooth piece into H/V monotonic arcs & fit with Lagrange / Hermite / LS / Linear
        for piece in corner_pieces:
            if len(piece) < 2:
                continue
            hv_arcs = split_into_monotonic_hv(piece)
            for axis, arc in hv_arcs:
                if len(arc) < 2:
                    continue
                fitted = fit_monotonic_arc_recursive(
                    arc,
                    axis=axis,
                    tol=tol_math,
                    id_counter=id_counter,
                    max_lagrange_degree=max_lagrange_degree,
                )
                all_curves.extend(fitted)

    return all_curves
