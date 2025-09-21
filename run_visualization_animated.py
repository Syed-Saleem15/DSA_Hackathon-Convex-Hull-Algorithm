#!/usr/bin/env python3
"""
run_visualization_animated.py

Enhanced version with step-by-step algorithm animation/simulation.
Shows how Jarvis March and Graham Scan work in real-time.
"""

import sys
import os
import random
import webbrowser
import tempfile
import json
from typing import List, Tuple

# Import your existing functions
try:
    from convex_hull_comparison import jarvis_march, graham_scan, parse_stdin_points
    print("[SUCCESS] Successfully imported your convex hull functions!")
except ImportError as e:
    print(f"[ERROR] Could not import from convex_hull_comparison.py: {e}")
    print("Make sure convex_hull_comparison.py is in the same directory!")
    sys.exit(1)

Point = Tuple[float, float]
import random
import time

def generate_points(n: int) -> List[Point]:
    """Generate n random points within [0, 100] range."""
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]

def save_visualization(points: List[Point], jarvis_hull: List[Point], graham_hull: List[Point]):
    """Call the function that creates an animated visualizer."""
    create_animated_visualizer(points, jarvis_hull, graham_hull)
def create_animated_visualizer(points: List[Point], jarvis_hull: List[Point], graham_hull: List[Point]):
    """Create animated HTML visualizer showing algorithm steps."""
    
    # Scale points to fit canvas
    if points:
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        padding = 50
        canvas_width = 1200 - 2 * padding
        canvas_height = 700 - 2 * padding
        
        if max_x > min_x and max_y > min_y:
            scale_x = canvas_width / (max_x - min_x)
            scale_y = canvas_height / (max_y - min_y)
            scale = min(scale_x, scale_y)
            
            def scale_point(p):
                x = (p[0] - min_x) * scale + padding
                y = (p[1] - min_y) * scale + padding
                return {"x": x, "y": y}
            
            points_js = json.dumps([scale_point(p) for p in points])
            jarvis_js = json.dumps([scale_point(p) for p in jarvis_hull])
            graham_js = json.dumps([scale_point(p) for p in graham_hull])
        else:
            points_js = json.dumps([{"x": p[0], "y": p[1]} for p in points])
            jarvis_js = json.dumps([{"x": p[0], "y": p[1]} for p in jarvis_hull])
            graham_js = json.dumps([{"x": p[0], "y": p[1]} for p in graham_hull])
    else:
        points_js = "[]"
        jarvis_js = "[]"
        graham_js = "[]"
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Animated Convex Hull Visualization</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}

        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .algorithm-selector {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .algo-tab {{
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .algo-tab.active {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}

        .algo-tab.inactive {{
            background: #e1e8ed;
            color: #7f8c8d;
        }}

        .controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 30px;
            justify-content: center;
            align-items: center;
        }}

        button {{
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .btn-primary {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}

        .btn-success {{
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
            box-shadow: 0 4px 15px rgba(39, 174, 96, 0.4);
        }}

        .btn-warning {{
            background: linear-gradient(45deg, #f39c12, #e67e22);
            color: white;
            box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4);
        }}

        .btn-danger {{
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
        }}

        .btn-primary:hover, .btn-success:hover, .btn-warning:hover, .btn-danger:hover {{
            transform: translateY(-2px);
        }}

        .speed-control {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        input[type="range"] {{
            width: 150px;
        }}

        .canvas-container {{
            position: relative;
            border: 3px solid #e1e8ed;
            border-radius: 15px;
            background: white;
            box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}

        canvas {{
            display: block;
        }}

        .status-panel {{
            background: linear-gradient(45deg, #34495e, #2c3e50);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 16px;
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 15px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .color-dot {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 2px solid rgba(0, 0, 0, 0.2);
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }}

        .stat-label {{
            font-size: 14px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.2); }}
            100% {{ transform: scale(1); }}
        }}

        .current-point {{
            animation: pulse 1s infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Animated Convex Hull Algorithms</h1>
        
        <div class="algorithm-selector">
            <button class="algo-tab active" onclick="selectAlgorithm('jarvis')" id="jarvis-tab">
                Jarvis March (Gift Wrapping)
            </button>
            <button class="algo-tab inactive" onclick="selectAlgorithm('graham')" id="graham-tab">
                Graham Scan
            </button>
        </div>
        
        <div class="controls">
            <button class="btn-success" onclick="startAnimation()">Start Animation</button>
            <button class="btn-warning" onclick="pauseAnimation()">Pause</button>
            <button class="btn-danger" onclick="resetAnimation()">Reset</button>
            <button class="btn-primary" onclick="showFinalResult()">Show Final Result</button>
            
            <div class="speed-control">
                <span>Speed:</span>
                <input type="range" id="speedSlider" min="1" max="10" value="5">
                <span id="speedValue">5x</span>
            </div>
        </div>

        <div class="canvas-container">
            <canvas id="canvas" width="1200" height="700"></canvas>
        </div>

        <div class="status-panel" id="statusPanel">
            Click "Start Animation" to see how the algorithms work step by step!
        </div>

        <div class="legend">
            <div class="legend-item">
                <div class="color-dot" style="background: #3498db;"></div>
                <span><strong>Input Points</strong></span>
            </div>
            <div class="legend-item">
                <div class="color-dot" style="background: #e74c3c;"></div>
                <span><strong>Current Point</strong></span>
            </div>
            <div class="legend-item">
                <div class="color-dot" style="background: #27ae60;"></div>
                <span><strong>Hull Edge</strong></span>
            </div>
            <div class="legend-item">
                <div class="color-dot" style="background: #f39c12;"></div>
                <span><strong>Candidate Line</strong></span>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Current Algorithm</div>
                <div class="stat-value" id="currentAlgo">Jarvis March</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Animation Step</div>
                <div class="stat-value" id="currentStep">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Hull Vertices Found</div>
                <div class="stat-value" id="hullVertices">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Points</div>
                <div class="stat-value" id="totalPoints">{len(points) if points else 0}</div>
            </div>
        </div>
    </div>

    <script>
        // Data from Python
        const pythonPoints = {points_js};
        const pythonJarvisHull = {jarvis_js};
        const pythonGrahamHull = {graham_js};

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // Animation state
        let currentAlgorithm = 'jarvis';
        let animationState = {{}};
        let animationId = null;
        let isAnimating = false;
        let animationSpeed = 500; // milliseconds

        // Colors
        const colors = {{
            points: '#3498db',
            current: '#e74c3c',
            hull: '#27ae60',
            candidate: '#f39c12',
            completed: '#9b59b6'
        }};

        // Geometry helpers
        function orientation(a, b, c) {{
            const val = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
            if (val > 0) return 1;
            if (val < 0) return -1;
            return 0;
        }}

        function distanceSquared(a, b) {{
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            return dx * dx + dy * dy;
        }}

        // Drawing functions
        function clearCanvas() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }}

        function drawPoint(point, color = colors.points, size = 4, pulse = false) {{
            ctx.fillStyle = color;
            ctx.beginPath();
            
            if (pulse) {{
                const pulseSize = size + Math.sin(Date.now() * 0.01) * 2;
                ctx.arc(point.x, point.y, pulseSize, 0, 2 * Math.PI);
            }} else {{
                ctx.arc(point.x, point.y, size, 0, 2 * Math.PI);
            }}
            
            ctx.fill();
            
            // Add glow effect for special points
            if (color === colors.current) {{
                ctx.shadowColor = color;
                ctx.shadowBlur = 15;
                ctx.fill();
                ctx.shadowBlur = 0;
            }}
        }}

        function drawLine(from, to, color = colors.candidate, width = 2, dash = []) {{
            ctx.strokeStyle = color;
            ctx.lineWidth = width;
            ctx.setLineDash(dash);
            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        function drawHull(hull, color = colors.hull) {{
            if (hull.length < 2) return;
            
            ctx.strokeStyle = color;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(hull[0].x, hull[0].y);
            
            for (let i = 1; i < hull.length; i++) {{
                ctx.lineTo(hull[i].x, hull[i].y);
            }}
            
            ctx.stroke();
        }}

        // Algorithm selection
        function selectAlgorithm(algo) {{
            currentAlgorithm = algo;
            document.getElementById('jarvis-tab').className = algo === 'jarvis' ? 'algo-tab active' : 'algo-tab inactive';
            document.getElementById('graham-tab').className = algo === 'graham' ? 'algo-tab active' : 'algo-tab inactive';
            document.getElementById('currentAlgo').textContent = algo === 'jarvis' ? 'Jarvis March' : 'Graham Scan';
            resetAnimation();
        }}

        // Jarvis March Animation
        function* jarvisAnimation(points) {{
            if (points.length < 3) return;
            
            // Find leftmost point
            let start = points.reduce((leftmost, p) => 
                (p.x < leftmost.x || (p.x === leftmost.x && p.y < leftmost.y)) ? p : leftmost
            );
            
            yield {{
                type: 'status',
                message: 'Finding leftmost point as starting point...',
                highlight: [start]
            }};
            
            const hull = [];
            let current = start;
            let step = 0;
            
            do {{
                hull.push(current);
                step++;
                
                yield {{
                    type: 'status',
                    message: `Step ${{step}}: Starting from point (${{current.x.toFixed(1)}}, ${{current.y.toFixed(1)}})`,
                    hull: [...hull],
                    current: current
                }};
                
                let next = points[0] === current ? points[1] : points[0];
                
                yield {{
                    type: 'status',
                    message: `Checking all points to find the most counter-clockwise...`,
                    hull: [...hull],
                    current: current,
                    candidate: next
                }};
                
                for (let i = 0; i < points.length; i++) {{
                    if (points[i] === current) continue;
                    
                    const o = orientation(current, next, points[i]);
                    
                    yield {{
                        type: 'status',
                        message: `Testing point (${{points[i].x.toFixed(1)}}, ${{points[i].y.toFixed(1)}}) - Orientation: ${{o > 0 ? 'Counter-clockwise' : o < 0 ? 'Clockwise' : 'Collinear'}}`,
                        hull: [...hull],
                        current: current,
                        candidate: next,
                        testing: points[i]
                    }};
                    
                    if (o === 1 || (o === 0 && distanceSquared(current, points[i]) > distanceSquared(current, next))) {{
                        next = points[i];
                        yield {{
                            type: 'status',
                            message: `New best candidate: (${{next.x.toFixed(1)}}, ${{next.y.toFixed(1)}})`,
                            hull: [...hull],
                            current: current,
                            candidate: next
                        }};
                    }}
                }}
                
                yield {{
                    type: 'status',
                    message: `Adding edge to (${{next.x.toFixed(1)}}, ${{next.y.toFixed(1)}})`,
                    hull: [...hull, next],
                    current: current,
                    candidate: next
                }};
                
                current = next;
            }} while (current !== start);
            
            yield {{
                type: 'complete',
                message: `Jarvis March completed! Found ${{hull.length}} hull vertices.`,
                hull: hull
            }};
        }}

        // Graham Scan Animation
        function* grahamAnimation(points) {{
            if (points.length < 3) return;
            
            // Find pivot
            let pivot = points.reduce((lowest, p) => 
                (p.y < lowest.y || (p.y === lowest.y && p.x < lowest.x)) ? p : lowest
            );
            
            yield {{
                type: 'status',
                message: 'Finding pivot point (lowest Y, then lowest X)...',
                highlight: [pivot]
            }};
            
            const others = points.filter(p => p !== pivot);
            
            // Sort by polar angle
            others.sort((a, b) => {{
                const angleA = Math.atan2(a.y - pivot.y, a.x - pivot.x);
                const angleB = Math.atan2(b.y - pivot.y, b.x - pivot.x);
                if (Math.abs(angleA - angleB) < 0.001) {{
                    return distanceSquared(pivot, a) - distanceSquared(pivot, b);
                }}
                return angleA - angleB;
            }});
            
            yield {{
                type: 'status',
                message: 'Sorting points by polar angle from pivot...',
                highlight: [pivot],
                sorted: others
            }};
            
            const stack = [pivot];
            let step = 0;
            
            for (const point of others) {{
                step++;
                
                yield {{
                    type: 'status',
                    message: `Step ${{step}}: Processing point (${{point.x.toFixed(1)}}, ${{point.y.toFixed(1)}})`,
                    hull: [...stack],
                    current: point
                }};
                
                while (stack.length >= 2) {{
                    const o = orientation(stack[stack.length - 2], stack[stack.length - 1], point);
                    
                    if (o <= 0) {{
                        const removed = stack.pop();
                        yield {{
                            type: 'status',
                            message: `Removing point (${{removed.x.toFixed(1)}}, ${{removed.y.toFixed(1)}}) - creates right turn`,
                            hull: [...stack],
                            current: point,
                            removed: removed
                        }};
                    }} else {{
                        break;
                    }}
                }}
                
                stack.push(point);
                yield {{
                    type: 'status',
                    message: `Adding point (${{point.x.toFixed(1)}}, ${{point.y.toFixed(1)}}) to hull`,
                    hull: [...stack],
                    current: point
                }};
            }}
            
            yield {{
                type: 'complete',
                message: `Graham Scan completed! Found ${{stack.length}} hull vertices.`,
                hull: stack
            }};
        }}

        // Animation control
        function startAnimation() {{
            if (isAnimating) return;
            
            isAnimating = true;
            animationState = currentAlgorithm === 'jarvis' ? 
                jarvisAnimation(pythonPoints) : 
                grahamAnimation(pythonPoints);
            
            runAnimation();
        }}

        function runAnimation() {{
            const result = animationState.next();
            
            if (result.done) {{
                isAnimating = false;
                return;
            }}
            
            const step = result.value;
            drawAnimationStep(step);
            
            if (isAnimating) {{
                setTimeout(runAnimation, animationSpeed);
            }}
        }}

        function drawAnimationStep(step) {{
            clearCanvas();
            
            // Draw all points
            pythonPoints.forEach(point => {{
                let color = colors.points;
                let size = 4;
                let pulse = false;
                
                if (step.highlight && step.highlight.includes(point)) {{
                    color = colors.current;
                    size = 8;
                    pulse = true;
                }} else if (step.current === point) {{
                    color = colors.current;
                    size = 6;
                    pulse = true;
                }} else if (step.testing === point) {{
                    color = colors.candidate;
                    size = 6;
                }}
                
                drawPoint(point, color, size, pulse);
            }});
            
            // Draw hull so far
            if (step.hull && step.hull.length > 1) {{
                drawHull(step.hull);
            }}
            
            // Draw candidate line
            if (step.current && step.candidate) {{
                drawLine(step.current, step.candidate, colors.candidate, 2, [5, 5]);
            }}
            
            // Update status
            document.getElementById('statusPanel').textContent = step.message;
            document.getElementById('hullVertices').textContent = step.hull ? step.hull.length : 0;
        }}

        function pauseAnimation() {{
            isAnimating = false;
        }}

        function resetAnimation() {{
            isAnimating = false;
            clearCanvas();
            pythonPoints.forEach(point => drawPoint(point));
            document.getElementById('statusPanel').textContent = 'Click "Start Animation" to see how the algorithms work step by step!';
            document.getElementById('currentStep').textContent = '0';
            document.getElementById('hullVertices').textContent = '0';
        }}

        function showFinalResult() {{
            isAnimating = false;
            clearCanvas();
            
            const finalHull = currentAlgorithm === 'jarvis' ? pythonJarvisHull : pythonGrahamHull;
            
            pythonPoints.forEach(point => drawPoint(point));
            
            if (finalHull.length > 0) {{
                drawHull([...finalHull, finalHull[0]]); // Close the hull
                finalHull.forEach(point => drawPoint(point, colors.completed, 6));
            }}
            
            document.getElementById('statusPanel').textContent = 
                `Final Result: ${{currentAlgorithm === 'jarvis' ? 'Jarvis March' : 'Graham Scan'}} found ${{finalHull.length}} hull vertices.`;
        }}

        // Speed control
        document.getElementById('speedSlider').addEventListener('input', function(e) {{
            const speed = parseInt(e.target.value);
            animationSpeed = 1100 - (speed * 100); // Invert for intuitive control
            document.getElementById('speedValue').textContent = speed + 'x';
        }});

        // Initialize
        resetAnimation();
        document.getElementById('totalPoints').textContent = pythonPoints.length;
    </script>
</body>
</html>'''
    
    # Create temporary HTML file with UTF-8 encoding
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_path = f.name
    except Exception as e:
        temp_path = os.path.join(tempfile.gettempdir(), 'convex_hull_animated.html')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    webbrowser.open('file://' + os.path.abspath(temp_path))
    print(f"[SUCCESS] Animated visualizer opened: {temp_path}")
    
    return temp_path

def main():
    """Main function with animated visualization."""
    
    print("=" * 70)
    print("  ANIMATED CONVEX HULL VISUALIZER - Step-by-Step Algorithms")
    print("=" * 70)
    
    # Generate test points
    print("\n[STEP 1] Generating test points...")
    random.seed(42)
    n_points = 50  # Fewer points for better animation visibility
    test_points = [
        (random.uniform(0, 100), random.uniform(0, 100)) 
        for _ in range(n_points)
    ]
    print(f"         Generated {len(test_points)} random points")
    
    # Compute convex hulls
    print("\n[STEP 2] Computing convex hulls...")
    jarvis_result = jarvis_march(test_points)
    graham_result = graham_scan(test_points)
    print(f"         Jarvis March: {len(jarvis_result)} vertices")
    print(f"         Graham Scan: {len(graham_result)} vertices")
    
    # Create animated visualization
    print("\n[STEP 3] Creating animated visualization...")
    html_file = create_animated_visualizer(test_points, jarvis_result, graham_result)
    
    print("\n" + "=" * 70)
    print("SUCCESS! Animated visualization opened in browser.")
    print("\nFEATURES:")
    print("  * Step-by-step algorithm animation")
    print("  * Switch between Jarvis March and Graham Scan")
    print("  * Variable animation speed control")
    print("  * Real-time status updates")
    print("  * Pause/Resume/Reset controls")
    print("\nCONTROLS:")
    print("  * Click algorithm tabs to switch between methods")
    print("  * Use Start/Pause/Reset buttons to control animation")
    print("  * Adjust speed slider for faster/slower animation")
    print("  * Click 'Show Final Result' to see completed hull")
    print("=" * 70)
    
    return html_file

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnimation cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")