"""
convex_hull_comparison.py

Implements Jarvis March (Gift Wrapping) and Graham Scan convex-hull algorithms.
Features:
 - Robust handling of corner cases: duplicates, N<3, all-collinear, all-identical points.
 - Option to include all boundary (collinear) points on hull edges.
 - Prints results in the requested format:
     Jarvis: <hull_size> x1 y1 x2 y2 ...
     Graham: <hull_size> x1 y1 x2 y2 ...
 - Plots the points and both hulls (different colours), hull vertices are clearly marked.
 - Optional benchmarking routine to compare runtimes for increasing N.

Usage examples:
 1) Provide N only on stdin; script will generate N random points (deterministic seed):
    echo 100 | python3 convex_hull_comparison.py

 2) Provide N followed by 2*N numbers (x y pairs):
    printf "6 0 0 2 0 1 1 0 1 0.5 0.5 0 0.5\n" | python3 convex_hull_comparison.py

 3) Run benchmark (empirical performance plots):
    python3 convex_hull_comparison.py --bench

Notes:
 - The script is self-contained and uses only standard Python + matplotlib.
 - To turn off plotting use --no-plot. To toggle inclusion of collinear boundary points use --exclude-collinear.

"""

import sys
import math
import random
import argparse
import time
from typing import List, Tuple, Set
import plotly.graph_objects as go

import matplotlib.pyplot as plt

Point = Tuple[float, float]


# ---------- Geometry helpers ----------

def orientation(a: Point, b: Point, c: Point) -> int:
    """Return positive if a->b->c is counter-clockwise, negative if clockwise, 0 if collinear."""
    val = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if val > 0:
        return 1
    if val < 0:
        return -1
    return 0


def dist_sq(a: Point, b: Point) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


def on_segment(a: Point, b: Point, c: Point) -> bool:
    """Return True if point c lies on segment ab (inclusive). Assumes collinearity check was done."""
    return (min(a[0], b[0]) - 1e-9 <= c[0] <= max(a[0], b[0]) + 1e-9 and
            min(a[1], b[1]) - 1e-9 <= c[1] <= max(a[1], b[1]) + 1e-9)


# ---------- Jarvis March (Gift Wrapping) ----------

def jarvis_march(points: List[Point]) -> List[Point]:
    pts = list(dict.fromkeys(points))  # remove duplicates, preserving order
    n = len(pts)
    if n == 0:
        return []
    if n <= 2:
        return pts[:]

    # find leftmost point (smallest x, then smallest y)
    start = min(pts, key=lambda p: (p[0], p[1]))
    hull = []
    p = start
    while True:
        hull.append(p)
        # Choose an arbitrary candidate q different from p
        q = pts[0] if pts[0] != p else pts[1]
        for r in pts:
            if r == p:
                continue
            o = orientation(p, q, r)
            if o == 1:
                # r is more counter-clockwise than q relative to p
                q = r
            elif o == 0:
                # If collinear, pick the farthest so we wrap to outermost boundary point
                if dist_sq(p, r) > dist_sq(p, q):
                    q = r
        p = q
        if p == start:
            break
    return hull


# ---------- Graham Scan ----------

def graham_scan(points: List[Point]) -> List[Point]:
    pts = list(dict.fromkeys(points))  # remove duplicates
    n = len(pts)
    if n == 0:
        return []
    if n <= 2:
        return pts[:]

    # pivot: point with lowest y, then lowest x
    pivot = min(pts, key=lambda p: (p[1], p[0]))
    others = [p for p in pts if p != pivot]

    def angle_and_dist(p: Point):
        ang = math.atan2(p[1] - pivot[1], p[0] - pivot[0])
        return (ang, dist_sq(pivot, p))

    # Sort by angle, then by distance (ascending). This ensures collinear points
    # along the same ray keep the farthest at the end (so inner ones get popped).
    others.sort(key=lambda p: (angle_and_dist(p)[0], angle_and_dist(p)[1]))

    # Build hull using stack
    stack: List[Point] = [pivot]
    for p in others:
        while len(stack) >= 2 and orientation(stack[-2], stack[-1], p) <= 0:
            stack.pop()
        stack.append(p)

    return stack


# ---------- Include collinear boundary points (optional) ----------

def include_collinear_on_edges(hull_vertices: List[Point], all_points: List[Point]) -> List[Point]:
    """Given the list of outer hull vertices in order, extend each edge by inserting
    points from all_points that lie strictly on the segment between the two vertices.
    The returned sequence preserves order along each edge (from vertex A to B).
    """
    if not hull_vertices:
        return []
    extended: List[Point] = []
    m = len(hull_vertices)
    for i in range(m):
        a = hull_vertices[i]
        b = hull_vertices[(i + 1) % m]
        extended.append(a)
        # collect collinear points between a and b excluding endpoints
        col = [r for r in all_points if r != a and r != b and orientation(a, b, r) == 0 and on_segment(a, b, r)]
        # sort by distance from a so they appear along the edge in the right order
        col_sorted = sorted(col, key=lambda r: dist_sq(a, r))
        extended.extend(col_sorted)
    # note: do NOT append the starting vertex again at the end
    return extended


# ---------- I/O, plotting and benchmarking ----------

def print_hull(label: str, hull: List[Point]):
    coords = ' '.join(f"{x} {y}" for (x, y) in hull)
    print(f"{label}: {len(hull)} {coords}")


def plot_hulls(points: List[Point], jarvis_hull: List[Point], graham_hull: List[Point], filename: str = 'hulls.png', show_plot: bool = True):
    plt.figure(figsize=(8, 8))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    plt.scatter(xs, ys, s=15, alpha=0.6, label='Points', zorder=1)

    def draw_hull(hull_pts: List[Point], color: str, label: str, marker: str):
        if not hull_pts:
            return
        hx = [p[0] for p in hull_pts] + [hull_pts[0][0]]
        hy = [p[1] for p in hull_pts] + [hull_pts[0][1]]
        plt.plot(hx, hy, linestyle='-', linewidth=2, label=label, zorder=3)
        plt.scatter([p[0] for p in hull_pts], [p[1] for p in hull_pts], s=80, edgecolors='k', marker=marker, zorder=4)

    draw_hull(jarvis_hull, 'tab:blue', 'Jarvis Hull', 'o')
    draw_hull(graham_hull, 'tab:orange', 'Graham Hull', 's')

    plt.legend()
    plt.title('Convex Hulls: Jarvis (circle) vs Graham (square)')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    if show_plot:
        plt.show()
    plt.close()


def benchmark_and_plot(max_n=3000, trials=3):
    Ns = [50, 100, 200, 400, 800, 1600]
    Ns = [n for n in Ns if n <= max_n]
    jarvis_times = []
    graham_times = []
    random.seed(42)
    for n in Ns:
        jt = 0.0
        gt = 0.0
        for _ in range(trials):
            pts = [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]
            t0 = time.perf_counter(); _ = jarvis_march(pts); jt += time.perf_counter() - t0
            t0 = time.perf_counter(); _ = graham_scan(pts); gt += time.perf_counter() - t0
        jarvis_times.append(jt / trials)
        graham_times.append(gt / trials)
        print(f"N={n}: Jarvis avg {jarvis_times[-1]:.6f}s, Graham avg {graham_times[-1]:.6f}s")

    plt.figure()
    plt.plot(Ns, jarvis_times, marker='o', label='Jarvis (empirical)')
    plt.plot(Ns, graham_times, marker='s', label='Graham (empirical)')
    plt.xlabel('N (number of points)')
    plt.ylabel('Average time (s)')
    plt.legend()
    plt.title('Empirical runtime comparison')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('benchmark.png')
    plt.show()


def parse_stdin_points() -> List[Point]:
    data = sys.stdin.read().strip().split()
    if not data:
        # no input; default to a deterministic set so script can still run
        N = 100
        print(f"No stdin provided. Generating {N} random points (seed=42).", file=sys.stderr)
        random.seed(42)
        return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(N)]
    toks = [float(x) for x in data]
    N = int(toks[0])
    coords = toks[1:]
    pts: List[Point] = []
    if len(coords) >= 2 * N:
        for i in range(N):
            pts.append((coords[2 * i], coords[2 * i + 1]))
        return pts
    else:
        # Not enough coordinates provided: take what is available then generate the rest
        provided = len(coords) // 2
        for i in range(provided):
            pts.append((coords[2 * i], coords[2 * i + 1]))
        if provided < N:
            print(f"Only {provided} points provided; generating remaining {N - provided} points (seed=42)", file=sys.stderr)
            random.seed(42)
            for _ in range(N - provided):
                pts.append((random.uniform(0, 100), random.uniform(0, 100)))
        return pts
    
    def visualize_3d(points, hull_jarvis, hull_graham):
    # Convert to lists for plotting
        x, y = zip(*points)

        # Scatter all points
        fig = go.Figure(data=[
            go.Scatter3d(
                x=x, y=y, z=[0]*len(points),
                mode='markers',
                marker=dict(size=5, color='blue'),
                name="All Points"
            )
        ])

        # Jarvis hull edges
        hx, hy = zip(*hull_jarvis)
        fig.add_trace(go.Scatter3d(
            x=hx + (hx[0],), 
            y=hy + (hy[0],), 
            z=[0.05]* (len(hx)+1),  # lifted slightly
            mode='lines+markers',
            line=dict(color='red', width=5),
            marker=dict(size=6, color='red', symbol="circle"),
            name="Jarvis Hull"
        ))

        # Graham hull edges
        gx, gy = zip(*hull_graham)
        fig.add_trace(go.Scatter3d(
            x=gx + (gx[0],), 
            y=gy + (gy[0],), 
            z=[0.1]* (len(gx)+1),
            mode='lines+markers',
            line=dict(color='green', width=5),
            marker=dict(size=6, color='green', symbol="diamond"),
            name="Graham Hull"
        ))

        # Layout for presentation
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='X'),
                yaxis=dict(title='Y'),
                zaxis=dict(title='Z (lifted for visibility)')
            ),
            title="3D Interactive Convex Hulls",
            legend=dict(x=0.8, y=0.9)
        )

        fig.show()

    # Example call after computing hulls:
    # visualize_3d(points, hull_jarvis, hull_graham)


def main():
    parser = argparse.ArgumentParser(description='Convex hull comparison: Jarvis vs Graham')
    parser.add_argument('--bench', action='store_true', help='Run benchmark and show runtime plots')
    parser.add_argument('--no-plot', action='store_true', help='Do not show plots (still saves images)')
    parser.add_argument('--exclude-collinear', action='store_true', help='Exclude collinear boundary points from output')
    args = parser.parse_args()

    if args.bench:
        benchmark_and_plot()
        return

    points = parse_stdin_points()

    # Preprocess: remove exact duplicates but keep consistent ordering for reproducibility
    uniq_points = list(dict.fromkeys(points))

    # Compute extreme vertices
    jarvis_vertices = jarvis_march(uniq_points)
    graham_vertices = graham_scan(uniq_points)

    # Optionally include collinear boundary points along edges
    if args.exclude_collinear:
        jarvis_hull = jarvis_vertices
        graham_hull = graham_vertices
    else:
        jarvis_hull = include_collinear_on_edges(jarvis_vertices, uniq_points)
        graham_hull = include_collinear_on_edges(graham_vertices, uniq_points)

    # Print requested output format
    print_hull('Jarvis', jarvis_hull)
    print_hull('Graham', graham_hull)

    # Visualization
    plot_hulls(uniq_points, jarvis_hull, graham_hull, filename='hulls.png', show_plot=not args.no_plot)
    


if __name__ == '__main__':
    main()
