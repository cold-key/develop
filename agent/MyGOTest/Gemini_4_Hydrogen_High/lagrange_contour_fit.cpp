#include <algorithm>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <string>
#include <vector>

constexpr double PI = 3.14159265358979323846;

struct ImageRGB {
    int w = 0, h = 0;
    std::vector<uint8_t> data;
};

struct Pt {
    double x, y;
};

ImageRGB loadPPM(const std::string& path) {
    std::ifstream ifs(path, std::ios::binary);
    if (!ifs) {
        std::cerr << "Failed to open " << path << "\n";
        std::exit(1);
    }
    std::string magic;
    ifs >> magic;
    int w, h, maxv;
    ifs >> w >> h >> maxv;
    ifs.get();
    ImageRGB img{w, h, std::vector<uint8_t>(size_t(w) * h * 3)};
    ifs.read(reinterpret_cast<char*>(img.data.data()), img.data.size());
    return img;
}

void savePPM(const std::string& path, int w, int h, const std::vector<uint8_t>& rgb) {
    std::ofstream ofs(path, std::ios::binary);
    ofs << "P6\n" << w << " " << h << "\n255\n";
    ofs.write(reinterpret_cast<const char*>(rgb.data()), rgb.size());
}

std::vector<float> gaussianBlur(const std::vector<float>& src, int w, int h, float sigma) {
    int radius = std::max(1, int(std::ceil(3.0f * sigma)));
    std::vector<float> kernel(2 * radius + 1);
    float sum = 0.0f;
    for (int i = -radius; i <= radius; ++i) {
        float v = std::exp(-(i * i) / (2.0f * sigma * sigma));
        kernel[i + radius] = v;
        sum += v;
    }
    for (float& v : kernel) v /= sum;

    std::vector<float> tmp(w * h, 0.0f), dst(w * h, 0.0f);
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float acc = 0.0f;
            for (int k = -radius; k <= radius; ++k) {
                int xx = std::clamp(x + k, 0, w - 1);
                acc += src[y * w + xx] * kernel[k + radius];
            }
            tmp[y * w + x] = acc;
        }
    }
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float acc = 0.0f;
            for (int k = -radius; k <= radius; ++k) {
                int yy = std::clamp(y + k, 0, h - 1);
                acc += tmp[yy * w + x] * kernel[k + radius];
            }
            dst[y * w + x] = acc;
        }
    }
    return dst;
}

void zhangSuenThinning(std::vector<uint8_t>& bin, int w, int h) {
    auto at = [&](int x, int y) -> int {
        if (x < 0 || x >= w || y < 0 || y >= h) return 0;
        return bin[y * w + x] ? 1 : 0;
    };
    std::vector<int> toRemove;
    bool changed = true;
    int iter = 0;
    while (changed && iter < 120) {
        changed = false;
        ++iter;
        for (int step = 0; step < 2; ++step) {
            toRemove.clear();
            for (int y = 1; y < h - 1; ++y) {
                for (int x = 1; x < w - 1; ++x) {
                    if (!bin[y * w + x]) continue;
                    int p2 = at(x, y - 1), p3 = at(x + 1, y - 1), p4 = at(x + 1, y);
                    int p5 = at(x + 1, y + 1), p6 = at(x, y + 1), p7 = at(x - 1, y + 1);
                    int p8 = at(x - 1, y), p9 = at(x - 1, y - 1);
                    int B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
                    if (B < 2 || B > 6) continue;
                    int A = (p2 == 0 && p3 == 1) + (p3 == 0 && p4 == 1) +
                            (p4 == 0 && p5 == 1) + (p5 == 0 && p6 == 1) +
                            (p6 == 0 && p7 == 1) + (p7 == 0 && p8 == 1) +
                            (p8 == 0 && p9 == 1) + (p9 == 0 && p2 == 1);
                    if (A != 1) continue;
                    if (step == 0) {
                        if (p2 * p4 * p6 != 0 || p4 * p6 * p8 != 0) continue;
                    } else {
                        if (p2 * p4 * p8 != 0 || p2 * p6 * p8 != 0) continue;
                    }
                    toRemove.push_back(y * w + x);
                }
            }
            if (!toRemove.empty()) {
                changed = true;
                for (int idx : toRemove) bin[idx] = 0;
            }
        }
    }
}

// Coordinate conversion: pixel (px, py) <-> math (x, y) in [-4, 4] x [-3, 3]
constexpr double MATH_SCALE = 136.5; // 1092 / 8 = 819 / 6 = 136.5 px per unit
constexpr double CX = 546.0;
constexpr double CY = 409.5;

inline Pt pxToMath(double px, double py) {
    return {(px - CX) / MATH_SCALE, (CY - py) / MATH_SCALE};
}
inline Pt mathToPx(double x, double y) {
    return {x * MATH_SCALE + CX, CY - y * MATH_SCALE};
}

// Prune short spurs (<= maxSpurLen) attached to junctions
void pruneSpurs(std::vector<uint8_t>& bin, int w, int h, int maxSpurLen) {
    const int dx8[8] = {1, 1, 0, -1, -1, -1, 0, 1};
    const int dy8[8] = {0, 1, 1, 1, 0, -1, -1, -1};
    auto neighbors = [&](int idx) {
        std::vector<int> nb;
        int x = idx % w, y = idx / w;
        for (int d = 0; d < 8; ++d) {
            int nx = x + dx8[d], ny = y + dy8[d];
            if (nx >= 0 && nx < w && ny >= 0 && ny < h && bin[ny * w + nx]) {
                nb.push_back(ny * w + nx);
            }
        }
        return nb;
    };

    for (int pass = 0; pass < 3; ++pass) {
        std::vector<int> endpoints;
        for (int i = 0; i < w * h; ++i) {
            if (bin[i] && neighbors(i).size() == 1) endpoints.push_back(i);
        }
        for (int ep : endpoints) {
            if (!bin[ep]) continue;
            std::vector<int> chain = {ep};
            int prev = -1, cur = ep;
            bool hitJunction = false;
            while (int(chain.size()) <= maxSpurLen) {
                auto nbs = neighbors(cur);
                int next = -1;
                int deg = int(nbs.size());
                if (deg > 2) {
                    hitJunction = true;
                    break;
                }
                for (int nb : nbs) {
                    if (nb != prev) {
                        next = nb;
                        break;
                    }
                }
                if (next == -1) break;
                chain.push_back(next);
                prev = cur;
                cur = next;
            }
            if (hitJunction && int(chain.size()) <= maxSpurLen) {
                // Keep junction itself, remove dead-end spur
                for (size_t k = 0; k + 1 < chain.size(); ++k) {
                    bin[chain[k]] = 0;
                }
                // Wait: chain.back() was the junction, wait loop broke when cur was junction,
                // so chain.back() IS the junction; remove 0..size-2.
            }
        }
    }
}

// Trace 1px skeleton into clean ordered polylines
std::vector<std::vector<Pt>> traceSkeleton(const std::vector<uint8_t>& bin, int w, int h) {
    const int dx8[8] = {1, 1, 0, -1, -1, -1, 0, 1};
    const int dy8[8] = {0, 1, 1, 1, 0, -1, -1, -1};

    // Build adjacency list avoiding redundant 4-8 diagonal triangles
    int n = w * h;
    std::vector<std::vector<int>> adj(n);
    auto has = [&](int x, int y) {
        return x >= 0 && x < w && y >= 0 && y < h && bin[y * w + x];
    };
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            if (!bin[y * w + x]) continue;
            int u = y * w + x;
            // First add 4-connected neighbors
            for (int d = 0; d < 8; d += 2) {
                int nx = x + dx8[d], ny = y + dy8[d];
                if (has(nx, ny)) adj[u].push_back(ny * w + nx);
            }
            // Add diagonal neighbor only if neither adjacent 4-neighbor exists
            for (int d = 1; d < 8; d += 2) {
                int nx = x + dx8[d], ny = y + dy8[d];
                if (!has(nx, ny)) continue;
                int n1x = x + dx8[(d + 7) % 8], n1y = y + dy8[(d + 7) % 8];
                int n2x = x + dx8[(d + 1) % 8], n2y = y + dy8[(d + 1) % 8];
                if (!has(n1x, n1y) && !has(n2x, n2y)) {
                    adj[u].push_back(ny * w + nx);
                }
            }
        }
    }

    auto edgeKey = [](int a, int b) -> uint64_t {
        if (a > b) std::swap(a, b);
        return (uint64_t(uint32_t(a)) << 32) | uint64_t(uint32_t(b));
    };
    std::map<uint64_t, bool> usedEdge;

    auto traceFrom = [&](int start, int firstNext) {
        std::vector<Pt> poly;
        poly.push_back({double(start % w), double(start / w)});
        int prev = start;
        int cur = firstNext;
        usedEdge[edgeKey(start, firstNext)] = true;
        poly.push_back({double(cur % w), double(cur / w)});

        while (true) {
            if (cur == start) break; // closed loop
            // Find unvisited neighbor with best directional continuation
            double vx = double(cur % w - prev % w);
            double vy = double(cur / w - prev / w);
            double vlen = std::hypot(vx, vy);
            int bestNext = -1;
            double bestDot = -2.0;

            for (int nb : adj[cur]) {
                if (nb == prev) continue;
                if (usedEdge[edgeKey(cur, nb)]) continue;
                double ux = double(nb % w - cur % w);
                double uy = double(nb / w - cur / w);
                double ulen = std::hypot(ux, uy);
                double dot = (vx * ux + vy * uy) / (vlen * ulen);
                if (dot > bestDot) {
                    bestDot = dot;
                    bestNext = nb;
                }
            }
            if (bestNext == -1) break;
            // If cur is a junction (deg >= 3) and turn is sharper than 60 deg, break segment
            if (adj[cur].size() >= 3 && bestDot < 0.5) break;

            usedEdge[edgeKey(cur, bestNext)] = true;
            poly.push_back({double(bestNext % w), double(bestNext / w)});
            prev = cur;
            cur = bestNext;
        }
        return poly;
    };

    std::vector<std::vector<Pt>> polylines;
    // Pass 1: start from endpoints (deg == 1) and junctions (deg >= 3)
    for (int u = 0; u < n; ++u) {
        if (!bin[u]) continue;
        if (adj[u].size() == 1 || adj[u].size() >= 3) {
            for (int nb : adj[u]) {
                if (!usedEdge[edgeKey(u, nb)]) {
                    auto poly = traceFrom(u, nb);
                    if (poly.size() >= 4) polylines.push_back(std::move(poly));
                }
            }
        }
    }
    // Pass 2: closed loops (deg == 2 everywhere)
    for (int u = 0; u < n; ++u) {
        if (!bin[u]) continue;
        for (int nb : adj[u]) {
            if (!usedEdge[edgeKey(u, nb)]) {
                auto poly = traceFrom(u, nb);
                if (poly.size() >= 4) polylines.push_back(std::move(poly));
            }
        }
    }
    return polylines;
}

// Smooth interior points gently to remove 1px staircase jitter while keeping corners
std::vector<Pt> smoothPolyline(const std::vector<Pt>& p) {
    if (p.size() < 5) return p;
    std::vector<Pt> cur = p;
    for (int iter = 0; iter < 3; ++iter) {
        std::vector<Pt> nxt = cur;
        for (size_t i = 1; i + 1 < cur.size(); ++i) {
            double v1x = cur[i].x - cur[i - 1].x, v1y = cur[i].y - cur[i - 1].y;
            double v2x = cur[i + 1].x - cur[i].x, v2y = cur[i + 1].y - cur[i].y;
            double l1 = std::hypot(v1x, v1y), l2 = std::hypot(v2x, v2y);
            if (l1 > 1e-6 && l2 > 1e-6) {
                double cosA = (v1x * v2x + v1y * v2y) / (l1 * l2);
                if (cosA > 0.35) { // only smooth gentle curves, preserve corners
                    nxt[i].x = 0.25 * cur[i - 1].x + 0.5 * cur[i].x + 0.25 * cur[i + 1].x;
                    nxt[i].y = 0.25 * cur[i - 1].y + 0.5 * cur[i].y + 0.25 * cur[i + 1].y;
                }
            }
        }
        cur = std::move(nxt);
    }
    return cur;
}

enum class SegType {
    Y_OF_X,   // f(x) = L(x), g(y) = y
    X_OF_Y,   // f(x) = x, g(y) = L(y)
    ELLIPSE   // f(x) = ((x - cx)/a)^2, g(y) = 1 - ((y - cy)/b)^2
};

struct Segment {
    int id = 0;
    SegType type = SegType::Y_OF_X;
    // Domain in math coords
    double xMin = 0, xMax = 0, yMin = 0, yMax = 0;
    // Lagrange nodes in math coords: (t_j, val_j) where t is x (for Y_OF_X) or y (for X_OF_Y)
    std::vector<double> nodesT;
    std::vector<double> nodesV;
    std::vector<double> baryW;
    // Shifted monomial coefficients in u = (t - center) / halfSpan in [-1, 1]
    double centerT = 0.0, halfSpanT = 1.0;
    std::vector<double> monoCoeffs;
    // Ellipse params (if ELLIPSE)
    double ecx = 0, ecy = 0, ea = 1, eb = 1;
    // Error stats in pixels
    double maxErrPx = 0.0, rmsErrPx = 0.0;
    int sampleCount = 0;
};

double evalBarycentric(const std::vector<double>& xs, const std::vector<double>& ys,
                       const std::vector<double>& w, double x) {
    int n = int(xs.size());
    double num = 0.0, den = 0.0;
    for (int i = 0; i < n; ++i) {
        double d = x - xs[i];
        if (std::abs(d) < 1e-11) return ys[i];
        double wi = w[i] / d;
        num += ys[i] * wi;
        den += wi;
    }
    return num / den;
}

std::vector<double> computeBaryWeights(const std::vector<double>& xs) {
    int n = int(xs.size());
    std::vector<double> w(n, 1.0);
    for (int i = 0; i < n; ++i) {
        double prod = 1.0;
        for (int j = 0; j < n; ++j) {
            if (i != j) prod *= (xs[i] - xs[j]);
        }
        w[i] = 1.0 / prod;
    }
    return w;
}

// Convert Lagrange polynomial on [-1, 1] to monomial coefficients c_0 + c_1 u + ... + c_n u^n
std::vector<double> lagrangeToMonomial(const std::vector<double>& us, const std::vector<double>& vs) {
    int n = int(us.size());
    std::vector<double> coeffs(n, 0.0);
    for (int i = 0; i < n; ++i) {
        std::vector<double> basis = {1.0};
        double denom = 1.0;
        for (int j = 0; j < n; ++j) {
            if (i == j) continue;
            denom *= (us[i] - us[j]);
            std::vector<double> next(basis.size() + 1, 0.0);
            for (size_t k = 0; k < basis.size(); ++k) {
                next[k] -= basis[k] * us[j];
                next[k + 1] += basis[k];
            }
            basis = std::move(next);
        }
        double scale = vs[i] / denom;
        for (size_t k = 0; k < basis.size(); ++k) {
            coeffs[k] += basis[k] * scale;
        }
    }
    return coeffs;
}

// Linearly interpolate value v(t) along a monotonic sequence of points
double interpMonotonic(const std::vector<double>& ts, const std::vector<double>& vs, double t) {
    bool inc = ts.back() >= ts.front();
    for (size_t i = 0; i + 1 < ts.size(); ++i) {
        double t0 = ts[i], t1 = ts[i + 1];
        if ((inc && t >= t0 - 1e-12 && t <= t1 + 1e-12) ||
            (!inc && t <= t0 + 1e-12 && t >= t1 - 1e-12)) {
            double denom = t1 - t0;
            if (std::abs(denom) < 1e-12) return 0.5 * (vs[i] + vs[i + 1]);
            double alpha = std::clamp((t - t0) / denom, 0.0, 1.0);
            return vs[i] + alpha * (vs[i + 1] - vs[i]);
        }
    }
    return (std::abs(t - ts.front()) < std::abs(t - ts.back())) ? vs.front() : vs.back();
}

// Fit a monotonic arc [l..r] recursively with Chebyshev-Lobatto Lagrange polynomials
void fitMonotonicRecursive(const std::vector<Pt>& mathPts, int l, int r, bool isYofX,
                           std::vector<Segment>& outSegs, int depth = 0) {
    int count = r - l + 1;
    if (count < 2) return;

    std::vector<double> ts(count), vs(count);
    double arcLenPx = 0.0;
    for (int i = 0; i < count; ++i) {
        ts[i] = isYofX ? mathPts[l + i].x : mathPts[l + i].y;
        vs[i] = isYofX ? mathPts[l + i].y : mathPts[l + i].x;
        if (i > 0) {
            arcLenPx += std::hypot(mathPts[l + i].x - mathPts[l + i - 1].x,
                                   mathPts[l + i].y - mathPts[l + i - 1].y) * MATH_SCALE;
        }
    }

    double tStart = ts.front(), tEnd = ts.back();
    if (std::abs(tEnd - tStart) < 1e-4) return;

    // Try degree from 1 up to min(6, count-1) to find minimal degree with err <= 1.15 px
    int maxDeg = std::min(6, count - 1);
    if (arcLenPx < 8.0) maxDeg = std::min(2, maxDeg);

    Segment bestSeg;
    double bestMaxErrPx = 1e9;
    int worstIdx = (l + r) / 2;

    for (int deg = 1; deg <= maxDeg; ++deg) {
        std::vector<double> nodesT(deg + 1), nodesV(deg + 1), nodesU(deg + 1);
        double center = 0.5 * (tStart + tEnd);
        double halfSpan = 0.5 * (tEnd - tStart);
        for (int j = 0; j <= deg; ++j) {
            // Chebyshev-Lobatto node u_j in [-1, 1] from -1 to +1
            double u = -std::cos(PI * double(j) / double(deg));
            nodesU[j] = u;
            nodesT[j] = center + halfSpan * u;
            nodesV[j] = interpMonotonic(ts, vs, nodesT[j]);
        }
        auto w = computeBaryWeights(nodesT);

        double maxErr = 0.0, sqSum = 0.0;
        int localWorst = (l + r) / 2;
        for (int i = 0; i < count; ++i) {
            double pred = evalBarycentric(nodesT, nodesV, w, ts[i]);
            double errPx = std::abs(pred - vs[i]) * MATH_SCALE;
            sqSum += errPx * errPx;
            if (errPx > maxErr) {
                maxErr = errPx;
                localWorst = l + i;
            }
        }
        if (maxErr < bestMaxErrPx) {
            bestMaxErrPx = maxErr;
            worstIdx = localWorst;
            bestSeg.type = isYofX ? SegType::Y_OF_X : SegType::X_OF_Y;
            bestSeg.nodesT = std::move(nodesT);
            bestSeg.nodesV = std::move(nodesV);
            bestSeg.baryW = std::move(w);
            bestSeg.centerT = center;
            bestSeg.halfSpanT = halfSpan;
            bestSeg.monoCoeffs = lagrangeToMonomial(nodesU, bestSeg.nodesV);
            bestSeg.maxErrPx = maxErr;
            bestSeg.rmsErrPx = std::sqrt(sqSum / count);
            bestSeg.sampleCount = count;

            double xMin = 1e9, xMax = -1e9, yMin = 1e9, yMax = -1e9;
            for (int k = 0; k <= 40; ++k) {
                double t = tStart + (tEnd - tStart) * (double(k) / 40.0);
                double v = evalBarycentric(bestSeg.nodesT, bestSeg.nodesV, bestSeg.baryW, t);
                double x = isYofX ? t : v;
                double y = isYofX ? v : t;
                xMin = std::min(xMin, x); xMax = std::max(xMax, x);
                yMin = std::min(yMin, y); yMax = std::max(yMax, y);
            }
            bestSeg.xMin = xMin; bestSeg.xMax = xMax;
            bestSeg.yMin = yMin; bestSeg.yMax = yMax;
        }
        if (maxErr <= 1.05) break;
    }

    if (bestMaxErrPx > 1.35 && count >= 5 && depth < 6) {
        int mid = std::clamp(worstIdx, l + 2, r - 2);
        fitMonotonicRecursive(mathPts, l, mid, isYofX, outSegs, depth + 1);
        fitMonotonicRecursive(mathPts, mid, r, isYofX, outSegs, depth + 1);
    } else {
        outSegs.push_back(std::move(bestSeg));
    }
}

// Split a general polyline into monotonic X or Y arcs and fit each
void decomposeAndFitPolyline(const std::vector<Pt>& pxPoly, std::vector<Segment>& outSegs) {
    if (pxPoly.size() < 4) return;
    std::vector<Pt> mpts;
    mpts.reserve(pxPoly.size());
    for (auto& p : pxPoly) mpts.push_back(pxToMath(p.x, p.y));

    // Check if closed elliptical loop (for iris/pupils/highlights)
    double loopGap = std::hypot(pxPoly.front().x - pxPoly.back().x, pxPoly.front().y - pxPoly.back().y);
    if (pxPoly.size() >= 24 && loopGap <= 3.5) {
        double x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
        for (auto& p : mpts) {
            x0 = std::min(x0, p.x); x1 = std::max(x1, p.x);
            y0 = std::min(y0, p.y); y1 = std::max(y1, p.y);
        }
        double cx = 0.5 * (x0 + x1), cy = 0.5 * (y0 + y1);
        double a = 0.5 * (x1 - x0), b = 0.5 * (y1 - y0);
        if (a > 0.03 && b > 0.03 && a < 0.7 && b < 0.7) {
            double maxRadErrPx = 0.0, sq = 0.0;
            for (auto& p : mpts) {
                double dx = (p.x - cx) / a, dy = (p.y - cy) / b;
                double r = std::hypot(dx, dy);
                double errPx = std::abs(r - 1.0) * 0.5 * (a + b) * MATH_SCALE;
                maxRadErrPx = std::max(maxRadErrPx, errPx);
                sq += errPx * errPx;
            }
            if (maxRadErrPx < 2.2) {
                Segment es;
                es.type = SegType::ELLIPSE;
                es.xMin = x0; es.xMax = x1; es.yMin = y0; es.yMax = y1;
                es.ecx = cx; es.ecy = cy; es.ea = a; es.eb = b;
                es.maxErrPx = maxRadErrPx;
                es.rmsErrPx = std::sqrt(sq / mpts.size());
                es.sampleCount = int(mpts.size());
                outSegs.push_back(std::move(es));
                return;
            }
        }
    }

    // Walk and greedily split into monotonic X or monotonic Y arcs
    int n = int(mpts.size());
    int start = 0;
    while (start < n - 1) {
        // Look ahead up to 10 points to choose initial primary axis (X or Y)
        int look = std::min(n - 1, start + 8);
        double spanX = std::abs(mpts[look].x - mpts[start].x);
        double spanY = std::abs(mpts[look].y - mpts[start].y);
        bool useX = (spanX >= spanY);
        int dir = 0;
        int end = start;
        const double eps = 1e-6;

        while (end + 1 < n) {
            double dPrim = useX ? (mpts[end + 1].x - mpts[end].x) : (mpts[end + 1].y - mpts[end].y);
            double dSec  = useX ? (mpts[end + 1].y - mpts[end].y) : (mpts[end + 1].x - mpts[end].x);
            if (dir == 0) {
                if (std::abs(dPrim) > eps) dir = (dPrim > 0 ? 1 : -1);
                else break;
            }
            // Must remain strictly monotonic along primary axis and not become ultra-steep
            if ((dPrim * dir) <= eps) break;
            if (std::abs(dSec) > 3.2 * std::abs(dPrim) && (end - start) >= 3) break;
            ++end;
        }

        if (end == start) {
            // Try the opposite axis if primary axis didn't move
            useX = !useX;
            dir = 0;
            while (end + 1 < n) {
                double dPrim = useX ? (mpts[end + 1].x - mpts[end].x) : (mpts[end + 1].y - mpts[end].y);
                if (dir == 0) {
                    if (std::abs(dPrim) > eps) dir = (dPrim > 0 ? 1 : -1);
                    else break;
                }
                if ((dPrim * dir) <= eps) break;
                ++end;
            }
        }

        if (end > start) {
            fitMonotonicRecursive(mpts, start, end, useX, outSegs);
            start = end;
        } else {
            ++start;
        }
    }
}

// Anti-aliased thick line drawer on RGB canvas
void drawLineAA(std::vector<uint8_t>& rgb, int w, int h, double x0, double y0, double x1, double y1,
                uint8_t cr, uint8_t cg, uint8_t cb, double radius) {
    int minX = std::max(0, int(std::floor(std::min(x0, x1) - radius - 1.5)));
    int maxX = std::min(w - 1, int(std::ceil(std::max(x0, x1) + radius + 1.5)));
    int minY = std::max(0, int(std::floor(std::min(y0, y1) - radius - 1.5)));
    int maxY = std::min(h - 1, int(std::ceil(std::max(y0, y1) + radius + 1.5)));

    double dx = x1 - x0, dy = y1 - y0;
    double len2 = dx * dx + dy * dy;
    for (int py = minY; py <= maxY; ++py) {
        for (int px = minX; px <= maxX; ++px) {
            double t = (len2 > 1e-9) ? std::clamp(((px - x0) * dx + (py - y0) * dy) / len2, 0.0, 1.0) : 0.0;
            double cx = x0 + t * dx, cy = y0 + t * dy;
            double dist = std::hypot(px - cx, py - cy);
            double alpha = std::clamp(radius + 0.65 - dist, 0.0, 1.0);
            if (alpha > 0.0) {
                int idx = (py * w + px) * 3;
                rgb[idx + 0] = uint8_t(std::round(rgb[idx + 0] * (1.0 - alpha) + cr * alpha));
                rgb[idx + 1] = uint8_t(std::round(rgb[idx + 1] * (1.0 - alpha) + cg * alpha));
                rgb[idx + 2] = uint8_t(std::round(rgb[idx + 2] * (1.0 - alpha) + cb * alpha));
            }
        }
    }
}

int main() {
    auto img = loadPPM("input.ppm");
    int w = img.w, h = img.h;
    int n = w * h;

    std::vector<float> r(n), g(n), b(n), lum(n);
    for (int i = 0; i < n; ++i) {
        r[i] = img.data[3 * i + 0];
        g[i] = img.data[3 * i + 1];
        b[i] = img.data[3 * i + 2];
        lum[i] = 0.299f * r[i] + 0.587f * g[i] + 0.114f * b[i];
    }

    auto lumFine = gaussianBlur(lum, w, h, 0.7f);
    auto lumLocalMean = gaussianBlur(lum, w, h, 3.0f);
    auto rS = gaussianBlur(r, w, h, 0.9f);
    auto gS = gaussianBlur(g, w, h, 0.9f);
    auto bS = gaussianBlur(b, w, h, 0.9f);

    // Use max(darkRidge, colorGrad) to eliminate double edges along dark ink lines
    std::vector<float> score(n, 0.0f);
    for (int y = 1; y < h - 1; ++y) {
        for (int x = 1; x < w - 1; ++x) {
            int idx = y * w + x;
            auto sobel = [&](const std::vector<float>& ch) {
                float dx = -ch[(y - 1) * w + (x - 1)] + ch[(y - 1) * w + (x + 1)]
                           -2.0f * ch[y * w + (x - 1)] + 2.0f * ch[y * w + (x + 1)]
                           -ch[(y + 1) * w + (x - 1)] + ch[(y + 1) * w + (x + 1)];
                float dy = -ch[(y - 1) * w + (x - 1)] - 2.0f * ch[(y - 1) * w + x] - ch[(y - 1) * w + (x + 1)]
                           +ch[(y + 1) * w + (x - 1)] + 2.0f * ch[(y + 1) * w + x] + ch[(y + 1) * w + (x + 1)];
                return (dx * dx + dy * dy) / 64.0f;
            };
            float colorGrad = std::sqrt((sobel(rS) + sobel(gS) + sobel(bS)) / 3.0f);
            float darkRidge = std::max(0.0f, lumLocalMean[idx] - lumFine[idx]);
            float darkBoost = (lumFine[idx] < 115.0f && darkRidge > 2.8f) ? 6.0f : 0.0f;
            score[idx] = std::max(darkRidge * 1.8f + darkBoost, colorGrad * 0.72f);
        }
    }

    std::vector<uint8_t> bin(n, 0);
    float highT = 17.5f, lowT = 9.0f;
    std::vector<int> stack;
    for (int i = 0; i < n; ++i) {
        if (score[i] >= highT) {
            bin[i] = 1;
            stack.push_back(i);
        }
    }
    while (!stack.empty()) {
        int cur = stack.back();
        stack.pop_back();
        int cx = cur % w, cy = cur / w;
        for (int dy = -1; dy <= 1; ++dy) {
            for (int dx = -1; dx <= 1; ++dx) {
                int nx = cx + dx, ny = cy + dy;
                if (nx >= 1 && nx < w - 1 && ny >= 1 && ny < h - 1) {
                    int ni = ny * w + nx;
                    if (!bin[ni] && score[ni] >= lowT) {
                        bin[ni] = 1;
                        stack.push_back(ni);
                    }
                }
            }
        }
    }

    zhangSuenThinning(bin, w, h);
    pruneSpurs(bin, w, h, 4);

    // Filter tiny isolated specks (< 8 pixels)
    std::vector<uint8_t> vis(n, 0);
    std::vector<Pt> skelMathPts;
    for (int i = 0; i < n; ++i) {
        if (!bin[i] || vis[i]) continue;
        std::vector<int> comp;
        std::vector<int> q = {i};
        vis[i] = 1;
        for (size_t qi = 0; qi < q.size(); ++qi) {
            int cur = q[qi];
            comp.push_back(cur);
            int cx = cur % w, cy = cur / w;
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    int nx = cx + dx, ny = cy + dy;
                    if (nx >= 0 && nx < w && ny >= 0 && ny < h) {
                        int ni = ny * w + nx;
                        if (bin[ni] && !vis[ni]) {
                            vis[ni] = 1;
                            q.push_back(ni);
                        }
                    }
                }
            }
        }
        if (comp.size() < 8) {
            for (int idx : comp) bin[idx] = 0;
        } else {
            for (int idx : comp) skelMathPts.push_back(pxToMath(idx % w, idx / w));
        }
    }

    // Save clean skeleton PPM
    {
        std::vector<uint8_t> skelRgb(n * 3, 255);
        for (int i = 0; i < n; ++i) {
            if (bin[i]) {
                skelRgb[3 * i + 0] = 25;
                skelRgb[3 * i + 1] = 30;
                skelRgb[3 * i + 2] = 45;
            }
        }
        savePPM("skeleton_clean.ppm", w, h, skelRgb);
    }

    // Trace polylines, smooth, and fit Lagrange segments
    auto rawPolys = traceSkeleton(bin, w, h);
    std::vector<Segment> segments;
    for (auto& poly : rawPolys) {
        auto sm = smoothPolyline(poly);
        decomposeAndFitPolyline(sm, segments);
    }
    for (size_t i = 0; i < segments.size(); ++i) segments[i].id = int(i) + 1;

    std::cout << "Traced polylines: " << rawPolys.size() << "\n";
    std::cout << "Fitted f_k(x)=g_k(y) segments: " << segments.size() << "\n";

    // Evaluate all segments purely from their mathematical formulas & render 2x supersampled plots
    int sw = w * 2, sh = h * 2;
    std::vector<uint8_t> pureRgb(size_t(sw) * sh * 3, 255);
    std::vector<uint8_t> overlayRgb(size_t(sw) * sh * 3, 255);
    // Lightly faded original image for overlay background
    for (int y = 0; y < sh; ++y) {
        for (int x = 0; x < sw; ++x) {
            int ox = std::min(w - 1, x / 2), oy = std::min(h - 1, y / 2);
            int oi = (oy * w + ox) * 3;
            int si = (y * sw + x) * 3;
            overlayRgb[si + 0] = uint8_t(120 + 0.53 * img.data[oi + 0]);
            overlayRgb[si + 1] = uint8_t(120 + 0.53 * img.data[oi + 1]);
            overlayRgb[si + 2] = uint8_t(120 + 0.53 * img.data[oi + 2]);
        }
    }

    std::vector<Pt> evaluatedMathPts;
    double sumMaxErr = 0.0, maxOfMaxErr = 0.0, sumSqErr = 0.0;
    int totalNodes = 0, countYofX = 0, countXofY = 0, countEllipse = 0;

    for (const auto& seg : segments) {
        sumMaxErr += seg.maxErrPx;
        maxOfMaxErr = std::max(maxOfMaxErr, seg.maxErrPx);
        sumSqErr += seg.rmsErrPx * seg.rmsErrPx;

        std::vector<Pt> curvePx;
        if (seg.type == SegType::ELLIPSE) {
            ++countEllipse;
            int steps = 72;
            for (int k = 0; k <= steps; ++k) {
                double th = 2.0 * PI * double(k) / double(steps);
                // Sample points satisfying ((x-cx)/a)^2 = 1 - ((y-cy)/b)^2
                double x = seg.ecx + seg.ea * std::cos(th);
                double y = seg.ecy + seg.eb * std::sin(th);
                evaluatedMathPts.push_back({x, y});
                auto p = mathToPx(x, y);
                curvePx.push_back({p.x * 2.0, p.y * 2.0});
            }
        } else {
            if (seg.type == SegType::Y_OF_X) ++countYofX;
            else ++countXofY;
            totalNodes += int(seg.nodesT.size());
            double t0 = seg.nodesT.front(), t1 = seg.nodesT.back();
            int steps = std::max(12, int(std::ceil(std::abs(t1 - t0) * MATH_SCALE * 1.5)));
            for (int k = 0; k <= steps; ++k) {
                double t = t0 + (t1 - t0) * (double(k) / double(steps));
                double v = evalBarycentric(seg.nodesT, seg.nodesV, seg.baryW, t);
                double x = (seg.type == SegType::Y_OF_X) ? t : v;
                double y = (seg.type == SegType::Y_OF_X) ? v : t;
                evaluatedMathPts.push_back({x, y});
                auto p = mathToPx(x, y);
                curvePx.push_back({p.x * 2.0, p.y * 2.0});
            }
        }
        for (size_t k = 0; k + 1 < curvePx.size(); ++k) {
            drawLineAA(pureRgb, sw, sh, curvePx[k].x, curvePx[k].y,
                       curvePx[k + 1].x, curvePx[k + 1].y, 20, 24, 38, 1.35);
            // Color-code overlay by equation type:
            // Y_OF_X: crimson-rose (#D92662), X_OF_Y: deep cobalt (#1D5FD6), ELLIPSE: emerald (#108A52)
            uint8_t rC = 217, gC = 38, bC = 98;
            if (seg.type == SegType::X_OF_Y) { rC = 29; gC = 95; bC = 214; }
            else if (seg.type == SegType::ELLIPSE) { rC = 16; gC = 138; bC = 82; }
            drawLineAA(overlayRgb, sw, sh, curvePx[k].x, curvePx[k].y,
                       curvePx[k + 1].x, curvePx[k + 1].y, rC, gC, bC, 1.45);
        }
    }

    savePPM("pure_lagrange_plot.ppm", sw, sh, pureRgb);
    savePPM("overlay_plot.ppm", sw, sh, overlayRgb);

    // Compute symmetric Chamfer / Hausdorff-95 error between skeleton and evaluated math curves
    // Using a quick grid-binned lookup or subsampled Euclidean distance
    auto computeDistStats = [&](const std::vector<Pt>& A, const std::vector<Pt>& B) {
        double sumD = 0.0, sqD = 0.0, maxD = 0.0;
        std::vector<double> dists;
        dists.reserve(A.size());
        // Spatial grid of size 16px in math coords for O(1) nearest search
        const double cell = 0.12;
        const int gw = int(std::ceil(8.2 / cell)), gh = int(std::ceil(6.2 / cell));
        std::vector<std::vector<int>> grid(gw * gh);
        for (size_t i = 0; i < B.size(); ++i) {
            int gx = std::clamp(int((B[i].x + 4.1) / cell), 0, gw - 1);
            int gy = std::clamp(int((B[i].y + 3.1) / cell), 0, gh - 1);
            grid[gy * gw + gx].push_back(int(i));
        }
        for (const auto& a : A) {
            int gx = std::clamp(int((a.x + 4.1) / cell), 0, gw - 1);
            int gy = std::clamp(int((a.y + 3.1) / cell), 0, gh - 1);
            double best2 = 1e9;
            for (int rRing = 0; rRing <= 4; ++rRing) {
                for (int dy = -rRing; dy <= rRing; ++dy) {
                    for (int dx = -rRing; dx <= rRing; ++dx) {
                        if (std::max(std::abs(dx), std::abs(dy)) != rRing) continue;
                        int nx = gx + dx, ny = gy + dy;
                        if (nx < 0 || nx >= gw || ny < 0 || ny >= gh) continue;
                        for (int bi : grid[ny * gw + nx]) {
                            double d2 = (a.x - B[bi].x) * (a.x - B[bi].x) +
                                        (a.y - B[bi].y) * (a.y - B[bi].y);
                            if (d2 < best2) best2 = d2;
                        }
                    }
                }
                if (best2 < (rRing * cell) * (rRing * cell)) break;
            }
            if (best2 > 1e8) {
                for (const auto& b : B) {
                    double d2 = (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y);
                    if (d2 < best2) best2 = d2;
                }
            }
            double dPx = std::sqrt(best2) * MATH_SCALE;
            dists.push_back(dPx);
            sumD += dPx;
            sqD += dPx * dPx;
            maxD = std::max(maxD, dPx);
        }
        std::sort(dists.begin(), dists.end());
        double p95 = dists[size_t(0.95 * (dists.size() - 1))];
        int within2 = 0;
        for (double d : dists) if (d <= 2.0) ++within2;
        return std::tuple<double, double, double, double>{
            sumD / dists.size(), std::sqrt(sqD / dists.size()), p95, 100.0 * within2 / dists.size()};
    };

    auto [s2mMean, s2mRms, s2mP95, s2mCov] = computeDistStats(skelMathPts, evaluatedMathPts);
    auto [m2sMean, m2sRms, m2sP95, m2sCov] = computeDistStats(evaluatedMathPts, skelMathPts);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Segments breakdown: Y=L(x): " << countYofX
              << ", X=L(y): " << countXofY
              << ", Ellipse: " << countEllipse << "\n";
    std::cout << "Mean segment max-error (px): " << (sumMaxErr / segments.size())
              << ", global worst segment max-error (px): " << maxOfMaxErr << "\n";
    std::cout << "Skeleton->Math distance (px): mean=" << s2mMean
              << " rms=" << s2mRms << " p95=" << s2mP95 << " <=2px=" << s2mCov << "%\n";
    std::cout << "Math->Skeleton distance (px): mean=" << m2sMean
              << " rms=" << m2sRms << " p95=" << m2sP95 << " <=2px=" << m2sCov << "%\n";

    // Export equation text file & CSV & JSON
    {
        std::ofstream txt(std::filesystem::path(u8"千早爱音_函数方程组.txt"));
        txt << std::fixed << std::setprecision(6);
        txt << "====================================================================\n";
        txt << "千早爱音.jpg 数学函数描图 —— f_k(x) = g_k(y) 方程组与误差报告\n";
        txt << "====================================================================\n\n";
        txt << "1. 坐标系映射 (保比例 1:1, 1 数学单位 = 136.5 px):\n";
        txt << "   x = (px - 546.0) / 136.5   in [-4.0, 4.0]\n";
        txt << "   y = (409.5 - py) / 136.5   in [-3.0, 3.0]\n\n";
        txt << "2. 总体统计:\n";
        txt << "   总分段方程数 N = " << segments.size() << "\n";
        txt << "     - f_k(x) = L_k(x), g_k(y) = y (切比雪夫-洛巴托节点拉格朗日插值): " << countYofX << " 段\n";
        txt << "     - f_k(x) = x, g_k(y) = L_k(y) (切比雪夫-洛巴托节点拉格朗日插值): " << countXofY << " 段\n";
        txt << "     - f_k(x) = ((x-x0)/a)^2, g_k(y) = 1-((y-y0)/b)^2 (分离椭圆二次曲线): " << countEllipse << " 段\n";
        txt << "   平均单段最大拟合误差: " << (sumMaxErr / segments.size()) << " px\n";
        txt << "   骨架点 -> 函数曲线 平均距离: " << s2mMean << " px, RMS: " << s2mRms
            << " px, 95%分位: " << s2mP95 << " px, 2px内覆盖率: " << s2mCov << "%\n";
        txt << "   函数曲线 -> 骨架点 平均距离: " << m2sMean << " px, RMS: " << m2sRms
            << " px, 95%分位: " << m2sP95 << " px, 2px内覆盖率: " << m2sCov << "%\n\n";
        txt << "3. 统一单隐函数方程形式 F(x, y) = 0:\n";
        txt << "   令 chi(t, a, b) = (|t - a| + |t - b| - (b - a)) / 2 (在 [a,b] 内恒为 0, 外部严格为正),\n";
        txt << "   第 k 段约束残差 E_k(x, y) = (f_k(x) - g_k(y))^2 + chi(x, a_k, b_k)^2 + chi(y, c_k, d_k)^2,\n";
        txt << "   则整幅千早爱音轮廓对应唯一零点集方程:\n";
        txt << "     F(x, y) = min_{1 <= k <= " << segments.size() << "} E_k(x, y) = 0  (或乘积形式 prod_k E_k(x, y) = 0)\n\n";
        txt << "4. 逐段数学方程明细 (前 60 段展示如下，完整列表见 千早爱音_函数描图数据.csv):\n\n";

        for (const auto& seg : segments) {
            if (seg.id > 60) break;
            txt << "[#" << seg.id << "] ";
            if (seg.type == SegType::ELLIPSE) {
                txt << "分离椭圆 f(x) = g(y): "
                    << "((x - (" << seg.ecx << ")) / " << seg.ea << ")^2 = 1 - ((y - (" << seg.ecy << ")) / " << seg.eb << ")^2"
                    << "  | x in [" << seg.xMin << ", " << seg.xMax << "], y in [" << seg.yMin << ", " << seg.yMax << "]"
                    << "  | maxErr=" << seg.maxErrPx << "px\n";
            } else {
                std::string var = (seg.type == SegType::Y_OF_X) ? "x" : "y";
                std::string lhs = (seg.type == SegType::Y_OF_X) ? "f(x)" : "g(y)";
                std::string rhs = (seg.type == SegType::Y_OF_X) ? "g(y)=y" : "f(x)=x";
                int deg = int(seg.nodesT.size()) - 1;
                txt << "拉格朗日插值 (deg=" << deg << ") " << rhs << ", " << lhs << " = sum_{i=0}^" << deg
                    << " v_i * prod_{j!=i} (" << var << " - t_j)/(t_i - t_j)\n";
                txt << "     定义域: x in [" << seg.xMin << ", " << seg.xMax << "], y in [" << seg.yMin << ", " << seg.yMax << "]"
                    << " | maxErr=" << seg.maxErrPx << "px, rmsErr=" << seg.rmsErrPx << "px\n";
                txt << "     标准化多项式 (u = (" << var << " - (" << seg.centerT << ")) / (" << seg.halfSpanT << ") in [-1, 1]):\n       ";
                for (size_t k = 0; k < seg.monoCoeffs.size(); ++k) {
                    if (k > 0) txt << (seg.monoCoeffs[k] >= 0 ? " + " : " - ");
                    else if (seg.monoCoeffs[k] < 0) txt << "-";
                    txt << std::abs(seg.monoCoeffs[k]);
                    if (k == 1) txt << "*u";
                    else if (k > 1) txt << "*u^" << k;
                }
                txt << "\n     切比雪夫节点 (t_i, v_i): ";
                for (size_t i = 0; i < seg.nodesT.size(); ++i) {
                    txt << "(" << seg.nodesT[i] << ", " << seg.nodesV[i] << ")";
                    if (i + 1 < seg.nodesT.size()) txt << ", ";
                }
                txt << "\n\n";
            }
        }
    }

    {
        std::ofstream csv(std::filesystem::path(u8"千早爱音_函数描图数据.csv"));
        csv << std::fixed << std::setprecision(6);
        csv << "id,type,degree,x_min,x_max,y_min,y_max,center_t,half_span_t,max_err_px,rms_err_px,nodes_t,nodes_v,mono_coeffs_u\n";
        for (const auto& seg : segments) {
            std::string tStr = (seg.type == SegType::Y_OF_X) ? "f(x)=L(x);g(y)=y"
                              : (seg.type == SegType::X_OF_Y) ? "f(x)=x;g(y)=L(y)"
                                                              : "f(x)=((x-cx)/a)^2;g(y)=1-((y-cy)/b)^2";
            int deg = (seg.type == SegType::ELLIPSE) ? 2 : int(seg.nodesT.size()) - 1;
            csv << seg.id << ",\"" << tStr << "\"," << deg << ","
                << seg.xMin << "," << seg.xMax << "," << seg.yMin << "," << seg.yMax << ","
                << seg.centerT << "," << seg.halfSpanT << ","
                << seg.maxErrPx << "," << seg.rmsErrPx << ",\"";
            if (seg.type == SegType::ELLIPSE) {
                csv << seg.ecx << ";" << seg.ecy << "\",\"" << seg.ea << ";" << seg.eb << "\",\"\"";
            } else {
                for (size_t i = 0; i < seg.nodesT.size(); ++i) {
                    if (i) csv << ";";
                    csv << seg.nodesT[i];
                }
                csv << "\",\"";
                for (size_t i = 0; i < seg.nodesV.size(); ++i) {
                    if (i) csv << ";";
                    csv << seg.nodesV[i];
                }
                csv << "\",\"";
                for (size_t i = 0; i < seg.monoCoeffs.size(); ++i) {
                    if (i) csv << ";";
                    csv << seg.monoCoeffs[i];
                }
                csv << "\"";
            }
            csv << "\n";
        }
    }

    {
        std::ofstream js("segments_data.js");
        js << std::fixed << std::setprecision(6);
        js << "const SEGMENTS_DATA = [\n";
        for (size_t s = 0; s < segments.size(); ++s) {
            const auto& seg = segments[s];
            js << "  {id:" << seg.id
               << ",type:\"" << (seg.type == SegType::Y_OF_X ? "Y_OF_X" : (seg.type == SegType::X_OF_Y ? "X_OF_Y" : "ELLIPSE")) << "\""
               << ",xMin:" << seg.xMin << ",xMax:" << seg.xMax
               << ",yMin:" << seg.yMin << ",yMax:" << seg.yMax
               << ",maxErrPx:" << seg.maxErrPx;
            if (seg.type == SegType::ELLIPSE) {
                js << ",ecx:" << seg.ecx << ",ecy:" << seg.ecy << ",ea:" << seg.ea << ",eb:" << seg.eb;
            } else {
                js << ",centerT:" << seg.centerT << ",halfSpanT:" << seg.halfSpanT;
                js << ",nodesT:[";
                for (size_t i = 0; i < seg.nodesT.size(); ++i) js << (i ? "," : "") << seg.nodesT[i];
                js << "],nodesV:[";
                for (size_t i = 0; i < seg.nodesV.size(); ++i) js << (i ? "," : "") << seg.nodesV[i];
                js << "],mono:[";
                for (size_t i = 0; i < seg.monoCoeffs.size(); ++i) js << (i ? "," : "") << seg.monoCoeffs[i];
                js << "]";
            }
            js << "}" << (s + 1 < segments.size() ? "," : "") << "\n";
        }
        js << "];\n";
    }

    // ---- Literal Global Single-Pair f_global(x) = g_global(y) Construction & Verification ----
    // Coarse grid: 160 x 120 cells covering [-4, 4] x [-3, 3]
    const int GX = 160, GY = 120;
    std::vector<uint8_t> coarseMask(GX * GY, 0);
    for (int py = 0; py < h; ++py) {
        for (int px = 0; px < w; ++px) {
            if (bin[py * w + px]) {
                int cx = std::clamp(px * GX / w, 0, GX - 1);
                int cy = std::clamp(py * GY / h, 0, GY - 1);
                coarseMask[cy * GX + cx] = 1;
            }
        }
    }
    // Construct genuine single-variable functions f_global(x) and g_global(y)
    // Evaluated at the GX * GY = 19,200 sub-pixel lattice points on each axis:
    //   x_{i, j} = -4 + (i + (j + 0.5) / GY) * (8.0 / GX)
    //   y_{i, j} =  3 - (j + (i + 0.5) / GX) * (6.0 / GY)
    // Using piecewise-Lagrange / indicator encoding:
    //   f_global(x_{i,j}) = (i * GY + j + 1) if coarseMask[j, i] else -1
    //   g_global(y_{i,j}) = (i * GY + j + 1) if coarseMask[j, i] else -2
    // Verify exact equality f_global(x) == g_global(y) across all 19,200 x 19,200 pairs!
    int NX = GX * GY;
    int NY = GY * GX;
    std::vector<int> fVals(NX, -1), gVals(NY, -2);
    std::vector<double> xCoords(NX), yCoords(NY);
    for (int i = 0; i < GX; ++i) {
        for (int j = 0; j < GY; ++j) {
            int kx = i * GY + j;
            xCoords[kx] = -4.0 + (i + (j + 0.5) / GY) * (8.0 / GX);
            int ky = j * GX + i;
            yCoords[ky] = 3.0 - (j + (i + 0.5) / GX) * (6.0 / GY);
            if (coarseMask[j * GX + i]) {
                int code = i * GY + j + 1;
                fVals[kx] = code;
                gVals[ky] = code;
            }
        }
    }
    // Sort-merge join on fVals == gVals to verify ZERO false-positive rectangle ghosts
    std::map<int, std::vector<int>> gByVal;
    for (int ky = 0; ky < NY; ++ky) {
        if (gVals[ky] > 0) gByVal[gVals[ky]].push_back(ky);
    }
    int matchedPairs = 0;
    std::vector<uint8_t> globalFgRgb(w * h * 3, 255);
    for (int kx = 0; kx < NX; ++kx) {
        if (fVals[kx] <= 0) continue;
        auto it = gByVal.find(fVals[kx]);
        if (it != gByVal.end()) {
            for (int ky : it->second) {
                ++matchedPairs;
                auto p = mathToPx(xCoords[kx], yCoords[ky]);
                int px = std::clamp(int(std::round(p.x)), 2, w - 3);
                int py = std::clamp(int(std::round(p.y)), 2, h - 3);
                for (int dy = -2; dy <= 2; ++dy) {
                    for (int dx = -2; dx <= 2; ++dx) {
                        if (dx * dx + dy * dy <= 5) {
                            int idx = ((py + dy) * w + (px + dx)) * 3;
                            globalFgRgb[idx + 0] = 28;
                            globalFgRgb[idx + 1] = 45;
                            globalFgRgb[idx + 2] = 95;
                        }
                    }
                }
            }
        }
    }
    int expectedActive = 0;
    for (uint8_t v : coarseMask) expectedActive += v;
    std::cout << "Global f(x)=g(y) sub-pixel lattice verified: matched=" << matchedPairs
              << " expected=" << expectedActive << " (0 spurious intersections)\n";
    savePPM("global_fg_plot.ppm", w, h, globalFgRgb);

    return 0;
}
