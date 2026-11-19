# -*- coding: utf-8 -*-
"""
对 agent/MyGOTest/千早爱音.jpg 的前景剪影轮廓做函数描图。

方法：
1. 阈值分割（threshold >= 132）得到前景 mask。
2. 按列提取剪影上边界 top[x]（剪影轮廓的 y 坐标，x 为列号）。
3. 用拉格朗日插值在采样边界点上构造多项式函数 g(x)，使其图像与轮廓尽量一致
   （barycentric 形式评估，数值稳定）。
4. 输出：
   - 千早爱音_函数描图.png：原图 + 剪影轮廓 + 拟合函数图像
   - 千早爱音_函数描图数据.csv：x, 轮廓上界, 拟合g(x)
   - 千早爱音_函数描图.txt：拉格朗日节点表 + 拟合误差统计
"""

from PIL import Image
import numpy as np
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IMG = "agent/MyGOTest/千早爱音.jpg"
THRESH = 132
N_SAMPLES = 12
OUT_PNG = "agent/MyGOTest/TidepoolAlpha/千早爱音_函数描图.png"
OUT_CSV = "agent/MyGOTest/TidepoolAlpha/千早爱音_函数描图数据.csv"
OUT_TXT = "agent/MyGOTest/TidepoolAlpha/千早爱音_函数描图.txt"


def column_bounds(mask):
    H, W = mask.shape
    any_col = mask.any(axis=0)
    top = np.where(any_col, np.where(mask, np.arange(H)[:, None], H).min(axis=0), -1)
    bot = np.where(any_col, np.where(mask, np.arange(H)[:, None], -1).max(axis=0), -1)
    return top, bot


def lagrange_eval_stable(xs, ys, X):
    """稳定计算拉格朗日插值多项式在点 X 上的值（barycentric 形式）。"""
    X = np.atleast_1d(np.asarray(X, dtype=float))
    n = len(xs)
    # barycentric 权重 w[i] = 1 / prod_{j != i} (x_i - x_j)
    w = np.ones(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                w[i] *= (xs[i] - xs[j])
        w[i] = 1.0 / w[i]
    num = np.zeros_like(X)
    den = np.zeros_like(X)
    for i in range(n):
        d = X - xs[i]
        at_node = np.abs(d) < 1e-9
        d = np.where(at_node, 1.0, d)
        wi = np.where(at_node, 0.0, w[i] / d)
        num += ys[i] * wi
        den += wi
    with np.errstate(divide="ignore", invalid="ignore"):
        p = num / den
    for i in range(n):
        m = np.abs(X - xs[i]) < 1e-9
        if m.any():
            p = np.where(m, ys[i], p)
    return p


def main():
    img = Image.open(IMG).convert("L")
    arr = np.array(img)
    H, W = arr.shape
    print("image: W x H = %d x %d, threshold = %d" % (W, H, THRESH))

    mask = arr >= THRESH
    top, bot = column_bounds(mask)

    xs_all = np.where(top >= 0)[0]
    if len(xs_all) == 0:
        raise SystemExit("no foreground columns found")

    # 在有效列上均匀采样边界点作为拉格朗日节点
    n_all = len(xs_all)
    n_samp = min(N_SAMPLES, n_all)
    idx = np.unique(np.linspace(0, n_all - 1, n_samp).astype(int))
    sx = xs_all[idx].astype(float)
    sy = top[xs_all[idx]].astype(float)

    xgrid = np.arange(W, dtype=float)
    g = lagrange_eval_stable(sx, sy, xgrid)

    # 拟合误差：拟合值与真实轮廓上界在所有有效列上的差
    tvals = top[xs_all].astype(float)
    gvals = g[xs_all]
    dev = np.abs(gvals - tvals)
    print("valid columns: %d (x in [%d, %d])" % (n_all, int(xs_all[0]), int(xs_all[-1])))
    print("lagrange sample points: %d" % len(sx))
    print("fit error: max=%.2fpx mean=%.2fpx RMS=%.2fpx"
          % (dev.max(), dev.mean(), np.sqrt((dev ** 2).mean())))

    # ---- 输出数据 ----
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "轮廓上界top(x)", "拟合g(x)"])
        for x in range(W):
            topv = int(top[x]) if top[x] >= 0 else ""
            w.writerow([int(x), topv, round(float(g[x]), 3)])

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("千早爱音.jpg 剪影轮廓函数描图\n")
        f.write("前景阈值: arr >= %d\n" % THRESH)
        f.write("前景 mask 面积: %d / %d\n" % (int(mask.sum()), mask.size))
        f.write("有效列数: %d (x 范围 [%d, %d])\n" % (n_all, int(xs_all[0]), int(xs_all[-1])))
        f.write("拉格朗日采样节点数: %d\n" % len(sx))
        f.write("拟合函数形式: g(x) = sum_i top_i * prod_{j != i} (x - x_j) / (x_i - x_j)\n")
        f.write("拟合误差: max=%.2fpx mean=%.2fpx RMS=%.2fpx\n\n"
                % (dev.max(), dev.mean(), np.sqrt((dev ** 2).mean())))
        f.write("节点表 (x_i, top_i):\n")
        for xi, yi in zip(sx, sy):
            f.write("  (%d, %.1f)\n" % (int(round(xi)), float(yi)))

    # ---- 输出图像 ----
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.imshow(arr, cmap="gray", origin="upper", aspect="equal")
    ax.plot(xs_all, top[xs_all], "r-", lw=1.5, label="silhouette top(x)")
    ax.plot(xgrid, g, "b--", lw=2, label="fitted function g(x)")
    ax.legend(loc="upper right")
    ax.set_title("silhouette outline vs fitted function g(x)")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)
    print("saved:", OUT_PNG)
    print("saved:", OUT_CSV)
    print("saved:", OUT_TXT)


if __name__ == "__main__":
    main()
