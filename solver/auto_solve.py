# -*- coding: utf-8 -*-
"""
解阵 / Flow 连线 —— 截图直读求解器
用法:
    python auto_solve.py 截图.png [-o 输出.png]
自动定位棋盘、重建 7x7 网格、识别彩色端点、求解、把路径叠回原图。
"""
import argparse
import colorsys
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# 色相参考（剑网三解阵实际色彩：红/橙/黄/绿/蓝/紫/粉，无青色）
HUES = [
    ('红', 0), ('橙', 22), ('黄', 41), ('绿', 152),
    ('蓝', 205), ('紫', 275), ('粉', 328),
]
PALETTE = {
    '红': (255, 72, 72), '橙': (255, 140, 26), '黄': (255, 208, 64),
    '绿': (72, 224, 128), '蓝': (72, 168, 255),
    '紫': (176, 108, 255), '粉': (255, 107, 203),
}


def longest_run(v, ratio=0.45, gap=20):
    thr = v.max() * ratio
    if thr == 0:
        return None
    idx = np.where(v > thr)[0]
    if not len(idx):
        return None
    best, cur = [idx[0], idx[0]], [idx[0], idx[0]]
    for i in idx[1:]:
        if i - cur[-1] <= gap:
            cur[-1] = i
        else:
            if cur[-1] - cur[0] > best[-1] - best[0]:
                best = cur[:]
            cur = [i, i]
    if cur[-1] - cur[0] > best[-1] - best[0]:
        best = cur[:]
    return best[0], best[-1]


def find_board(arr):
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)
    mask = (r >= 15) & (r <= 32) & (g >= 24) & (g <= 42) & (b >= 32) & (b <= 52) & ((b - r) >= 11)
    xr = longest_run(mask.sum(axis=0))
    yr = longest_run(mask.sum(axis=1))
    if xr is None or yr is None:
        h, w = arr.shape[:2]
        return int(w * 0.05), int(h * 0.05), int(w * 0.95), int(h * 0.95)
    return xr[0], yr[0], xr[1] + 1, yr[1] + 1


def peaks(v, thr):
    out = []
    i = 0
    n = len(v)
    while i < n:
        if v[i] >= thr:
            j = i
            while j < n and v[j] >= thr:
                j += 1
            out.append((i + j - 1) / 2.0)
            i = j
        else:
            i += 1
    return out


def clean_peaks(arr):
    if not arr or len(arr) <= 1:
        return arr
    sorted_arr = sorted(arr)
    res = [sorted_arr[0]]
    for v in sorted_arr[1:]:
        if v - res[-1] >= 40:
            res.append(v)
    return res


def enforce_seven(arr, start, end):
    if len(arr) == 7:
        return arr
    if len(arr) > 7:
        return arr[:7]
    step = (end - start) / 7.0
    return [start + step * (i + 0.5) for i in range(7)]


def detect_grid(img):
    arr = np.asarray(img).astype(np.float32)
    box = find_board(arr)
    x0, y0, x1, y1 = box
    pad = 6
    sub = arr[max(0, y0 + pad):min(arr.shape[0], y1 - pad), max(0, x0 + pad):min(arr.shape[1], x1 - pad)]
    lum = sub.mean(axis=2)
    mx = sub.max(axis=2)
    mn = sub.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    bright = (lum >= 78) & (lum <= 122) & (sat < 0.35)

    colproj = bright.sum(axis=0)
    rowproj = bright.sum(axis=1)

    max_c = colproj.max() if len(colproj) else 1
    max_r = rowproj.max() if len(rowproj) else 1

    gx_raw = [x0 + pad + p for p in peaks(colproj, max(4, max_c * 0.18))]
    gy_raw = [y0 + pad + p for p in peaks(rowproj, max(4, max_r * 0.18))]

    gx = enforce_seven(clean_peaks(gx_raw), x0, x1)
    gy = enforce_seven(clean_peaks(gy_raw), y0, y1)
    return gx, gy, box


def detect_endpoints(img, gx, gy, box):
    arr = np.asarray(img).astype(np.float32)
    x0, y0, x1, y1 = box
    h, w = arr.shape[:2]

    # 锁定在棋盘区域内部
    ex0 = max(0, x0 + 4)
    ex1 = min(w - 1, x1 - 4)
    ey0 = max(0, y0 + 4)
    ey1 = min(h - 1, y1 - 4)

    sub = arr[ey0:ey1 + 1, ex0:ex1 + 1]
    mx = sub.max(axis=2)
    mn = sub.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)

    # 精确区分彩色发光端点与暗灰点
    is_colored = ((sat >= 0.38) & (mx >= 110)) | ((sat >= 0.28) & (mx >= 170))

    sub_ys, sub_xs = np.where(is_colored)
    if not len(sub_xs):
        return []

    pts = set(zip((sub_xs + ex0).tolist(), (sub_ys + ey0).tolist()))
    seen = set()
    groups = []
    for p in list(pts):
        if p in seen:
            continue
        q = deque([p])
        seen.add(p)
        grp = []
        while q:
            cx, cy = q.popleft()
            grp.append((cx, cy))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    n = (cx + dx, cy + dy)
                    if n in pts and n not in seen:
                        seen.add(n)
                        q.append(n)
        if 45 <= len(grp) <= 800:
            groups.append(grp)

    out = []
    seen_cells = set()
    for grp in groups:
        grp_sorted = sorted(grp, key=lambda p: -float(arr[p[1], p[0]].sum()))
        top = grp_sorted[:max(1, len(grp) // 4)]
        rr = float(np.mean([arr[y, x, 0] for x, y in top]))
        gg = float(np.mean([arr[y, x, 1] for x, y in top]))
        bb = float(np.mean([arr[y, x, 2] for x, y in top]))
        hh, ss, vv = colorsys.rgb_to_hsv(rr / 255.0, gg / 255.0, bb / 255.0)
        hue = hh * 360.0
        cx = float(np.mean([p[0] for p in grp]))
        cy = float(np.mean([p[1] for p in grp]))

        name = min(HUES, key=lambda t: min(abs(t[1] - hue), 360 - abs(t[1] - hue)))[0]
        ci = int(min(range(len(gx)), key=lambda i: abs(gx[i] - cx)))
        ri = int(min(range(len(gy)), key=lambda i: abs(gy[i] - cy)))

        cell_key = (name, ri, ci)
        if cell_key not in seen_cells:
            seen_cells.add(cell_key)
            out.append((name, ri, ci, hue, cx, cy))
    return out


def solve(nr, nc, ends):
    board = [[None] * nc for _ in range(nr)]
    for name, pts in ends.items():
        for (r, c) in pts:
            board[r][c] = name
    colors = list(ends.keys())

    def nb(r, c):
        for dr, dc in DIRS:
            a, b2 = r + dr, c + dc
            if 0 <= a < nr and 0 <= b2 < nc:
                yield a, b2

    def prune(remaining):
        if not remaining:
            return True
        reach = [[False] * nc for _ in range(nr)]
        q = deque()
        for nm in remaining:
            for (r, c) in ends[nm]:
                if not reach[r][c]:
                    reach[r][c] = True
                    q.append((r, c))
        while q:
            r, c = q.popleft()
            for a, b2 in nb(r, c):
                if not reach[a][b2] and board[a][b2] is None:
                    reach[a][b2] = True
                    q.append((a, b2))
        for r in range(nr):
            for c in range(nc):
                if board[r][c] is None and not reach[r][c]:
                    return False
        return True

    def dist(nm):
        (r1, c1), (r2, c2) = ends[nm]
        return abs(r1 - r2) + abs(c1 - c2)

    # 远端点优先搜索（解法均匀美观）
    colors.sort(key=lambda nm: -dist(nm))
    paths = {}
    nodes = [0]
    LIMIT = 200000

    def dfs(idx):
        nodes[0] += 1
        if nodes[0] > LIMIT:
            return False
        if idx == len(colors):
            return all(board[r][c] is not None for r in range(nr) for c in range(nc))
        nm = colors[idx]
        start, end = ends[nm]
        path = [start]

        def walk(r, c):
            if (r, c) == end and len(path) > 1:
                if not prune(colors[idx + 1:]):
                    return False
                paths[nm] = list(path)
                if dfs(idx + 1):
                    return True
                del paths[nm]
                return False
            for a, b2 in nb(r, c):
                if (a, b2) == end:
                    path.append((a, b2))
                    ok = walk(a, b2)
                    path.pop()
                    if ok:
                        return True
                    continue
                if board[a][b2] is not None or (a, b2) in path:
                    continue
                board[a][b2] = nm
                path.append((a, b2))
                if prune(colors[idx:]):
                    if walk(a, b2):
                        return True
                path.pop()
                board[a][b2] = None
            return False

        return walk(start[0], start[1])

    ok = dfs(0)
    return ok, board, paths, nodes[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('-o', '--out', default=None)
    args = ap.parse_args()

    img = Image.open(args.src).convert('RGB')
    gx, gy, box = detect_grid(img)
    print(f'棋盘区域 {box}  ->  网格 {len(gy)} 行 x {len(gx)} 列')

    eps = detect_endpoints(img, gx, gy, box)
    ends = {}
    for name, r, c, hue, cx, cy in eps:
        ends.setdefault(name, []).append((r, c))
        print(f'  {name} hue={hue:5.1f} -> 行{r+1} 列{c+1}  (像素 {cx:.0f},{cy:.0f})')

    bad = {k: v for k, v in ends.items() if len(v) != 2}
    if bad:
        print('端点数量异常，无法求解:', {k: len(v) for k, v in bad.items()}, file=sys.stderr)
        return 1

    ok, board, paths, nodes = solve(len(gy), len(gx), ends)
    print('求解:', '成功' if ok else '无解', f'(搜索 {nodes} 个节点)')
    if not ok:
        return 1

    for nm, p in paths.items():
        print(f'{nm}({len(p)}格): ' + ' -> '.join(f'({r+1},{c+1})' for r, c in p))

    draw = ImageDraw.Draw(img, 'RGBA')
    for nm, p in paths.items():
        col = PALETTE.get(nm, (255, 255, 255))
        pts = [(gx[c], gy[r]) for r, c in p]
        draw.line(pts, fill=col + (75,), width=30, joint='curve')
        draw.line(pts, fill=col + (238,), width=16, joint='curve')
        for pt in [pts[0], pts[-1]]:
            draw.ellipse([pt[0]-14, pt[1]-14, pt[0]+14, pt[1]+14], fill=col + (255,), outline=(255,255,255,255), width=3)

    out = args.out or (args.src.rsplit('.', 1)[0] + '_answer.png')
    img.save(out)
    print('已保存:', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
