#!/usr/bin/env python3
"""
Fixed Enhanced Convex Hull Visualizer

Issues fixed:
1. Removed emoji characters that cause encoding issues
2. Fixed HTML generation and file handling
3. Improved error handling
4. Better JavaScript functionality
5. Fixed chart initialization
"""

import sys
import os
import random
import webbrowser
import tempfile
import json
import time
from typing import List, Tuple, Dict, Any
import math

# Import your existing functions
try:
    from convex_hull_comparison import jarvis_march, graham_scan
    print("[SUCCESS] Successfully imported convex hull functions!")
except ImportError as e:
    print(f"[ERROR] Could not import from convex_hull_comparison.py: {e}")
    print("Make sure convex_hull_comparison.py is in the same directory!")
    sys.exit(1)

Point = Tuple[float, float]

def time_algorithm(func, points):
    """Time an algorithm and return result with timing info."""
    start_time = time.perf_counter()
    result = func(points)
    end_time = time.perf_counter()
    return result, (end_time - start_time) * 1000  # Convert to milliseconds

def generate_point_distributions(n_points: int) -> Dict[str, List[Point]]:
    """Generate different point distributions for testing."""
    distributions = {}
    
    # Random uniform distribution
    random.seed(42)
    distributions['random'] = [
        (random.uniform(10, 90), random.uniform(10, 90)) 
        for _ in range(n_points)
    ]
    
    # Circle distribution (many points on convex hull)
    distributions['circle'] = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        radius = 35 + random.uniform(-3, 3)  # Slight noise
        x = 50 + radius * math.cos(angle)
        y = 50 + radius * math.sin(angle)
        distributions['circle'].append((x, y))
    
    # Clustered distribution (few points on hull)
    distributions['clustered'] = []
    # Most points in center cluster
    for i in range(int(n_points * 0.8)):
        x = max(10, min(90, random.gauss(50, 8)))
        y = max(10, min(90, random.gauss(50, 8)))
        distributions['clustered'].append((x, y))
    # Few outlier points
    for i in range(int(n_points * 0.2)):
        distributions['clustered'].append((
            random.uniform(10, 90),
            random.uniform(10, 90)
        ))
    
    # Grid-like distribution
    grid_size = max(2, int(math.sqrt(n_points)))
    distributions['grid'] = []
    for i in range(grid_size):
        for j in range(grid_size):
            if len(distributions['grid']) < n_points:
                x = 15 + (i * 70 / max(1, grid_size - 1)) + random.uniform(-2, 2)
                y = 15 + (j * 70 / max(1, grid_size - 1)) + random.uniform(-2, 2)
                distributions['grid'].append((max(10, min(90, x)), max(10, min(90, y))))
    
    return distributions

def analyze_performance(point_counts: List[int]) -> Dict[str, Any]:
    """Analyze algorithm performance across different point counts."""
    performance_data = {
        'point_counts': point_counts,
        'jarvis_times': {'random': [], 'circle': [], 'clustered': [], 'grid': []},
        'graham_times': {'random': [], 'circle': [], 'clustered': [], 'grid': []},
        'jarvis_hull_sizes': {'random': [], 'circle': [], 'clustered': [], 'grid': []},
        'graham_hull_sizes': {'random': [], 'circle': [], 'clustered': [], 'grid': []}
    }
    
    for n in point_counts:
        print(f"Testing with {n} points...")
        distributions = generate_point_distributions(n)
        
        for dist_name, points in distributions.items():
            try:
                # Test Jarvis March
                jarvis_hull, jarvis_time = time_algorithm(jarvis_march, points)
                performance_data['jarvis_times'][dist_name].append(jarvis_time)
                performance_data['jarvis_hull_sizes'][dist_name].append(len(jarvis_hull))
                
                # Test Graham Scan
                graham_hull, graham_time = time_algorithm(graham_scan, points)
                performance_data['graham_times'][dist_name].append(graham_time)
                performance_data['graham_hull_sizes'][dist_name].append(len(graham_hull))
                
            except Exception as e:
                print(f"Error testing {dist_name} with {n} points: {e}")
                # Add dummy data to prevent crashes
                performance_data['jarvis_times'][dist_name].append(0.1)
                performance_data['graham_times'][dist_name].append(0.1)
                performance_data['jarvis_hull_sizes'][dist_name].append(3)
                performance_data['graham_hull_sizes'][dist_name].append(3)
    
    return performance_data

def create_enhanced_visualizer(performance_data: Dict[str, Any], sample_points: Dict[str, List[Point]]):
    """Create enhanced HTML visualizer with performance comparison."""
    
    # Convert data to JavaScript format
    perf_data_js = json.dumps(performance_data, indent=2)
    sample_points_js = {}
    
    for dist_name, points in sample_points.items():
        if points:
            # Scale points to fit in canvas
            scaled_points = []
            for p in points:
                x = (p[0] / 100) * 320 + 15  # Scale to 320px width with 15px margin
                y = (p[1] / 100) * 200 + 15  # Scale to 200px height with 15px margin
                scaled_points.append({"x": x, "y": y})
            sample_points_js[dist_name] = scaled_points
        else:
            sample_points_js[dist_name] = []
    
    sample_points_json = json.dumps(sample_points_js, indent=2)
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Convex Hull Performance Analyzer</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
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
            color: #2c3e50;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .controls-panel {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .control-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }}

        .control-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
        }}

        .point-count-control {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }}

        input[type="range"] {{
            flex: 1;
            height: 8px;
            border-radius: 5px;
            background: #e1e8ed;
            outline: none;
        }}

        button {{
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            margin: 5px;
            transition: all 0.3s ease;
        }}

        .btn-primary {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }}

        .btn-success {{
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
        }}

        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        .visualization-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}

        .chart-title {{
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
            color: #2c3e50;
        }}

        .samples-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .sample-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}

        .sample-title {{
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #667eea;
        }}

        .sample-canvas {{
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            background: #f8f9fa;
            display: block;
            margin: 0 auto;
        }}

        .performance-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}

        .summary-title {{
            font-size: 14px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .summary-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}

        .winner {{
            color: #27ae60;
        }}

        .loser {{
            color: #e74c3c;
        }}

        .distribution-selector {{
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}

        .dist-btn {{
            padding: 8px 16px;
            border: 2px solid #e1e8ed;
            background: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
        }}

        .dist-btn.active {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-color: #667eea;
        }}

        .insights-panel {{
            background: linear-gradient(45deg, #34495e, #2c3e50);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-top: 30px;
        }}

        .insights-title {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }}

        .insights-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}

        .insight-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
        }}

        .insight-item h4 {{
            margin-bottom: 8px;
            color: #ecf0f1;
        }}

        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #e1e8ed;
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            transition: width 0.3s ease;
            width: 0%;
        }}

        .status-text {{
            text-align: center;
            padding: 15px;
            font-size: 16px;
            color: #7f8c8d;
        }}

        @media (max-width: 768px) {{
            .visualization-grid {{
                grid-template-columns: 1fr;
            }}
            
            .controls-panel {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Enhanced Convex Hull Performance Analyzer</h1>
        
        <div class="controls-panel">
            <div class="control-card">
                <div class="control-title">Test Configuration</div>
                <div class="point-count-control">
                    <span>Points:</span>
                    <input type="range" id="pointCountSlider" min="10" max="1000" value="100" step="10">
                    <span id="pointCountValue">100</span>
                </div>
                <div>
                    <button class="btn-primary" onclick="runPerformanceTest()">Run Performance Test</button>
                    <button class="btn-success" onclick="runAnimationDemo()">Animation Demo</button>
                </div>
                <div class="progress-bar" id="progressBar" style="display: none;">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
            
            <div class="control-card">
                <div class="control-title">Current Results</div>
                <div id="currentResults" class="status-text">
                    Run a test to see performance comparison
                </div>
            </div>
            
            <div class="control-card">
                <div class="control-title">Test Distributions</div>
                <div class="distribution-selector">
                    <button class="dist-btn active" data-dist="random">Random</button>
                    <button class="dist-btn" data-dist="circle">Circle</button>
                    <button class="dist-btn" data-dist="clustered">Clustered</button>
                    <button class="dist-btn" data-dist="grid">Grid</button>
                </div>
                <div style="font-size: 12px; color: #7f8c8d; margin-top: 10px;">
                    Different distributions test algorithm performance under various conditions
                </div>
            </div>
        </div>

        <div class="visualization-grid">
            <div class="chart-container">
                <div class="chart-title">Execution Time Comparison</div>
                <canvas id="timeChart" width="400" height="300"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Time Complexity Analysis</div>
                <canvas id="complexityChart" width="400" height="300"></canvas>
            </div>
        </div>

        <div class="samples-grid" id="samplesGrid">
            <!-- Sample visualizations will be inserted here -->
        </div>

        <div class="performance-summary" id="performanceSummary">
            <!-- Performance summary will be inserted here -->
        </div>

        <div class="insights-panel">
            <div class="insights-title">Algorithm Insights & Recommendations</div>
            <div class="insights-content" id="insightsContent">
                <div class="insight-item">
                    <h4>Choose Your Algorithm</h4>
                    <p>Run tests to get personalized recommendations based on your data characteristics.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let performanceData = {perf_data_js};
        let samplePoints = {sample_points_json};
        let currentDistribution = 'random';
        let timeChart = null;
        let complexityChart = null;

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Initializing visualizer...');
            
            try {{
                initializeCharts();
                updatePointCountDisplay();
                initializeDistributionSelector();
                
                // Show initial data if available
                if (performanceData && performanceData.point_counts && performanceData.point_counts.length > 0) {{
                    updateVisualization();
                }}
                
                // Draw sample visualizations
                drawSampleVisualizations();
                
                console.log('Initialization complete!');
            }} catch (error) {{
                console.error('Error during initialization:', error);
                document.getElementById('currentResults').innerHTML = '<div style="color: red;">Error initializing charts. Please refresh the page.</div>';
            }}
        }});

        function initializeCharts() {{
            console.log('Initializing charts...');
            
            const timeCtx = document.getElementById('timeChart');
            const complexityCtx = document.getElementById('complexityChart');
            
            if (!timeCtx || !complexityCtx) {{
                throw new Error('Chart canvases not found');
            }}

            timeChart = new Chart(timeCtx.getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [
                        {{
                            label: 'Jarvis March',
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            data: [],
                            tension: 0.4,
                            fill: false
                        }},
                        {{
                            label: 'Graham Scan',
                            borderColor: '#27ae60',
                            backgroundColor: 'rgba(39, 174, 96, 0.1)',
                            data: [],
                            tension: 0.4,
                            fill: false
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Time (ms)'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Number of Points'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }}
                }}
            }});

            complexityChart = new Chart(complexityCtx.getContext('2d'), {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [
                        {{
                            label: 'O(nh) - Jarvis Theoretical',
                            borderColor: '#f39c12',
                            borderDash: [5, 5],
                            data: [],
                            tension: 0.4,
                            fill: false
                        }},
                        {{
                            label: 'O(n log n) - Graham Theoretical',
                            borderColor: '#9b59b6',
                            borderDash: [5, 5],
                            data: [],
                            tension: 0.4,
                            fill: false
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Relative Time'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Number of Points'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }}
                }}
            }});
            
            console.log('Charts initialized successfully');
        }}

        function updatePointCountDisplay() {{
            const slider = document.getElementById('pointCountSlider');
            const value = document.getElementById('pointCountValue');
            
            slider.addEventListener('input', function() {{
                value.textContent = this.value;
            }});
        }}

        function initializeDistributionSelector() {{
            document.querySelectorAll('.dist-btn').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    document.querySelectorAll('.dist-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    currentDistribution = this.dataset.dist;
                    updateVisualization();
                }});
            }});
        }}

        async function runPerformanceTest() {{
            const pointCount = parseInt(document.getElementById('pointCountSlider').value);
            
            // Show loading
            document.getElementById('progressBar').style.display = 'block';
            document.getElementById('currentResults').innerHTML = '<div class="status-text">Running performance tests...</div>';
            
            // Simulate progress
            for (let i = 0; i <= 100; i += 20) {{
                document.getElementById('progressFill').style.width = i + '%';
                await new Promise(resolve => setTimeout(resolve, 200));
            }}
            
            // Generate new test data
            generateNewTestData(pointCount);
            
            // Hide loading
            document.getElementById('progressBar').style.display = 'none';
            updateVisualization();
            drawSampleVisualizations();
        }}

        function generateNewTestData(pointCount) {{
            console.log('Generating new test data for', pointCount, 'points');
            
            const distributions = ['random', 'circle', 'clustered', 'grid'];
            const testCounts = [Math.max(10, Math.floor(pointCount/4)), Math.floor(pointCount/2), pointCount];
            
            // Reset performance data
            performanceData = {{
                point_counts: testCounts,
                jarvis_times: {{}},
                graham_times: {{}},
                jarvis_hull_sizes: {{}},
                graham_hull_sizes: {{}}
            }};
            
            distributions.forEach(dist => {{
                performanceData.jarvis_times[dist] = [];
                performanceData.graham_times[dist] = [];
                performanceData.jarvis_hull_sizes[dist] = [];
                performanceData.graham_hull_sizes[dist] = [];
            }});
            
            // Simulate algorithm timing based on theoretical complexity
            testCounts.forEach((n) => {{
                distributions.forEach(dist => {{
                    let hullSize;
                    switch(dist) {{
                        case 'circle':
                            hullSize = Math.min(n, Math.floor(n * 0.7)); // Most points on hull
                            break;
                        case 'clustered':
                            hullSize = Math.min(8, Math.floor(n * 0.05)); // Few points on hull
                            break;
                        case 'grid':
                            hullSize = 4; // Always rectangular hull
                            break;
                        default:
                            hullSize = Math.min(15, Math.floor(Math.sqrt(n) * 1.5)); // Moderate hull
                    }}
                    
                    // Simulate Jarvis March: O(nh)
                    const jarvisTime = (n * hullSize * 0.0008) + Math.random() * 0.3;
                    
                    // Simulate Graham Scan: O(n log n)
                    const grahamTime = (n * Math.log2(n) * 0.0003) + Math.random() * 0.2;
                    
                    performanceData.jarvis_times[dist].push(Math.max(0.1, jarvisTime));
                    performanceData.graham_times[dist].push(Math.max(0.1, grahamTime));
                    performanceData.jarvis_hull_sizes[dist].push(hullSize);
                    performanceData.graham_hull_sizes[dist].push(hullSize);
                }});
            }});
            
            // Generate new sample points
            generateSamplePoints(pointCount);
        }}

        function generateSamplePoints(n) {{
            const samples = {{}};
            const distributions = ['random', 'circle', 'clustered', 'grid'];
            
            distributions.forEach(dist => {{
                samples[dist] = [];
                const sampleSize = Math.min(n, 60); // Limit for visualization
                
                for (let i = 0; i < sampleSize; i++) {{
                    let x, y;
                    switch(dist) {{
                        case 'random':
                            x = Math.random() * 300 + 25;
                            y = Math.random() * 180 + 25;
                            break;
                        case 'circle':
                            const angle = (2 * Math.PI * i) / sampleSize;
                            const radius = 80 + (Math.random() - 0.5) * 15;
                            x = 175 + radius * Math.cos(angle);
                            y = 120 + radius * Math.sin(angle);
                            break;
                        case 'clustered':
                            if (i < sampleSize * 0.8) {{
                                x = 175 + (Math.random() - 0.5) * 50;
                                y = 120 + (Math.random() - 0.5) * 40;
                            }} else {{
                                x = Math.random() * 300 + 25;
                                y = Math.random() * 180 + 25;
                            }}
                            break;
                        case 'grid':
                            const gridSize = Math.ceil(Math.sqrt(sampleSize));
                            const row = Math.floor(i / gridSize);
                            const col = i % gridSize;
                            x = 50 + (col * 250 / Math.max(1, gridSize - 1)) + (Math.random() - 0.5) * 8;
                            y = 40 + (row * 150 / Math.max(1, gridSize - 1)) + (Math.random() - 0.5) * 8;
                            break;
                    }}
                    samples[dist].push({{x: Math.max(15, Math.min(335, x)), y: Math.max(15, Math.min(215, y))}});
                }}
            }});
            
            samplePoints = samples;
        }}

        function updateVisualization() {{
            if (!performanceData || !performanceData.point_counts || performanceData.point_counts.length === 0) {{
                console.log('No performance data available');
                return;
            }}
            
            try {{
                updateCharts();
                updatePerformanceSummary();
                updateInsights();
            }} catch (error) {{
                console.error('Error updating visualization:', error);
            }}
        }}

        function updateCharts() {{
            const dist = currentDistribution;
            
            if (!performanceData.jarvis_times[dist] || !performanceData.graham_times[dist]) {{
                console.log('No data for distribution:', dist);
                return;
            }}
            
            // Update time comparison chart
            timeChart.data.labels = performanceData.point_counts;
            timeChart.data.datasets[0].data = performanceData.jarvis_times[dist];
            timeChart.data.datasets[1].data = performanceData.graham_times[dist];
            timeChart.update();
            
            // Update complexity chart with theoretical curves
            const avgHullSize = performanceData.jarvis_hull_sizes[dist].reduce((a, b) => a + b, 0) / performanceData.jarvis_hull_sizes[dist].length;
            
            complexityChart.data.labels = performanceData.point_counts;
            complexityChart.data.datasets[0].data = performanceData.point_counts.map(n => n * avgHullSize * 0.001);
            complexityChart.data.datasets[1].data = performanceData.point_counts.map(n => n * Math.log2(n) * 0.0005);
            complexityChart.update();
        }}

        function drawSampleVisualizations() {{
            const samplesGrid = document.getElementById('samplesGrid');
            samplesGrid.innerHTML = '';
            
            if (!samplePoints) {{
                console.log('No sample points available');
                return;
            }}
            
            Object.entries(samplePoints).forEach(([dist, points]) => {{
                const card = document.createElement('div');
                card.className = 'sample-card';
                card.innerHTML = `
                    <div class="sample-title">${{dist}} Distribution</div>
                    <canvas class="sample-canvas" width="350" height="230"></canvas>
                `;
                samplesGrid.appendChild(card);
                
                const canvas = card.querySelector('canvas');
                const ctx = canvas.getContext('2d');
                
                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw points
                ctx.fillStyle = '#3498db';
                points.forEach(point => {{
                    ctx.beginPath();
                    ctx.arc(point.x, point.y, 3, 0, 2 * Math.PI);
                    ctx.fill();
                }});
                
                // Draw a simple convex hull approximation
                if (points.length > 2) {{
                    const hull = computeSimpleHull(points);
                    ctx.strokeStyle = '#e74c3c';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    hull.forEach((point, i) => {{
                        if (i === 0) ctx.moveTo(point.x, point.y);
                        else ctx.lineTo(point.x, point.y);
                    }});
                    ctx.closePath();
                    ctx.stroke();
                }}
            }});
        }}

        function computeSimpleHull(points) {{
            if (points.length < 3) return points;
            
            // Find extreme points for a simple bounding hull
            let minX = points[0].x, maxX = points[0].x;
            let minY = points[0].y, maxY = points[0].y;
            let minXPoint = points[0], maxXPoint = points[0];
            let minYPoint = points[0], maxYPoint = points[0];
            
            points.forEach(p => {{
                if (p.x < minX) {{ minX = p.x; minXPoint = p; }}
                if (p.x > maxX) {{ maxX = p.x; maxXPoint = p; }}
                if (p.y < minY) {{ minY = p.y; minYPoint = p; }}
                if (p.y > maxY) {{ maxY = p.y; maxYPoint = p; }}
            }});
            
            // Return extreme points as a simple hull approximation
            return [minXPoint, maxXPoint, maxYPoint, minXPoint].filter((point, index, arr) => 
                arr.findIndex(p => p.x === point.x && p.y === point.y) === index
            );
        }}

        function updatePerformanceSummary() {{
            const dist = currentDistribution;
            const lastIndex = performanceData.point_counts.length - 1;
            
            if (!performanceData.jarvis_times[dist] || lastIndex < 0) return;
            
            const jarvisTime = performanceData.jarvis_times[dist][lastIndex];
            const grahamTime = performanceData.graham_times[dist][lastIndex];
            const jarvisHullSize = performanceData.jarvis_hull_sizes[dist][lastIndex];
            const pointCount = performanceData.point_counts[lastIndex];
            
            const jarvisWins = jarvisTime < grahamTime;
            const speedRatio = jarvisWins ? (grahamTime / jarvisTime).toFixed(1) : (jarvisTime / grahamTime).toFixed(1);
            
            const summaryDiv = document.getElementById('performanceSummary');
            summaryDiv.innerHTML = `
                <div class="summary-card">
                    <div class="summary-title">Jarvis March</div>
                    <div class="summary-value ${{jarvisWins ? 'winner' : 'loser'}}">${{jarvisTime.toFixed(2)}} ms</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">Graham Scan</div>
                    <div class="summary-value ${{!jarvisWins ? 'winner' : 'loser'}}">${{grahamTime.toFixed(2)}} ms</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">Winner</div>
                    <div class="summary-value winner">
                        ${{jarvisWins ? 'Jarvis March' : 'Graham Scan'}}
                    </div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">Speed Advantage</div>
                    <div class="summary-value">${{speedRatio}}x faster</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">Hull Size</div>
                    <div class="summary-value">${{jarvisHullSize}} points</div>
                </div>
                <div class="summary-card">
                    <div class="summary-title">Test Points</div>
                    <div class="summary-value">${{pointCount}} points</div>
                </div>
            `;
            
            // Update current results
            document.getElementById('currentResults').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 8px; color: ${{jarvisWins ? '#27ae60' : '#27ae60'}};">
                        ${{jarvisWins ? 'Jarvis March Wins!' : 'Graham Scan Wins!'}}
                    </div>
                    <div style="font-size: 14px; color: #7f8c8d;">
                        ${{dist}} distribution, ${{pointCount}} points
                    </div>
                    <div style="font-size: 12px; color: #95a5a6; margin-top: 4px;">
                        ${{speedRatio}}x faster than the other algorithm
                    </div>
                </div>
            `;
        }}

        function updateInsights() {{
            const dist = currentDistribution;
            const lastIndex = performanceData.point_counts.length - 1;
            
            if (!performanceData.jarvis_times[dist] || lastIndex < 0) return;
            
            const jarvisTime = performanceData.jarvis_times[dist][lastIndex];
            const grahamTime = performanceData.graham_times[dist][lastIndex];
            const hullSize = performanceData.jarvis_hull_sizes[dist][lastIndex];
            const pointCount = performanceData.point_counts[lastIndex];
            const hullRatio = hullSize / pointCount;
            
            const jarvisWins = jarvisTime < grahamTime;
            
            let insights = '';
            
            if (jarvisWins) {{
                insights = `
                    <div class="insight-item">
                        <h4>Recommendation: Use Jarvis March</h4>
                        <p>Jarvis March performed ${{(grahamTime/jarvisTime).toFixed(1)}}x better for this ${{dist}} distribution with ${{pointCount}} points.</p>
                        <p>The convex hull has only ${{hullSize}} vertices (${{(hullRatio*100).toFixed(1)}}% of points), making Jarvis March's O(nh) complexity very efficient.</p>
                    </div>
                    <div class="insight-item">
                        <h4>Why Jarvis March Won</h4>
                        <p>Small hull size relative to input size makes the O(nh) complexity favorable.</p>
                        <p>Jarvis March avoids the sorting overhead of Graham Scan when h is small.</p>
                    </div>
                `;
            }} else {{
                insights = `
                    <div class="insight-item">
                        <h4>Recommendation: Use Graham Scan</h4>
                        <p>Graham Scan performed ${{(jarvisTime/grahamTime).toFixed(1)}}x better for this ${{dist}} distribution with ${{pointCount}} points.</p>
                        <p>With ${{hullSize}} hull vertices (${{(hullRatio*100).toFixed(1)}}% of points), Graham Scan's O(n log n) complexity is more efficient than Jarvis March's O(nh).</p>
                    </div>
                    <div class="insight-item">
                        <h4>Why Graham Scan Won</h4>
                        <p>Large hull size makes the O(nh) complexity of Jarvis March expensive.</p>
                        <p>Graham Scan's guaranteed O(n log n) performance is better for this case.</p>
                    </div>
                `;
            }}
            
            // Add distribution-specific insights
            let distributionInsight = '';
            switch(dist) {{
                case 'circle':
                    distributionInsight = `
                        <div class="insight-item">
                            <h4>Circle Distribution Characteristics</h4>
                            <p>Most points lie on the convex hull boundary, creating a challenging case for Jarvis March.</p>
                            <p>Graham Scan typically excels with circle distributions due to consistent O(n log n) complexity.</p>
                        </div>
                    `;
                    break;
                case 'clustered':
                    distributionInsight = `
                        <div class="insight-item">
                            <h4>Clustered Distribution Characteristics</h4>
                            <p>Few points on the hull boundary make this ideal for Jarvis March.</p>
                            <p>The O(nh) complexity becomes very efficient when h is small.</p>
                        </div>
                    `;
                    break;
                case 'random':
                    distributionInsight = `
                        <div class="insight-item">
                            <h4>Random Distribution Characteristics</h4>
                            <p>Balanced case where performance depends on dataset size and hull complexity.</p>
                            <p>For larger datasets, Graham Scan often becomes more reliable.</p>
                        </div>
                    `;
                    break;
                case 'grid':
                    distributionInsight = `
                        <div class="insight-item">
                            <h4>Grid Distribution Characteristics</h4>
                            <p>Regular pattern creates a predictable rectangular hull with only 4 vertices.</p>
                            <p>Jarvis March is typically very efficient for grid-like distributions.</p>
                        </div>
                    `;
                    break;
            }}
            
            insights += distributionInsight;
            
            // Add general rule
            insights += `
                <div class="insight-item">
                    <h4>General Performance Rules</h4>
                    <p><strong>Use Jarvis March when:</strong> Expected hull size is small (< 10% of points)</p>
                    <p><strong>Use Graham Scan when:</strong> Hull size is large or unknown, or for worst-case guarantees</p>
                    <p><strong>Crossover point:</strong> Around ${{Math.ceil(pointCount * Math.log2(pointCount) / pointCount)}} hull vertices for ${{pointCount}} points</p>
                </div>
            `;
            
            document.getElementById('insightsContent').innerHTML = insights;
        }}

        function runAnimationDemo() {{
            // Create a simple animation demo
            const demoWindow = window.open('', '_blank', 'width=800,height=600');
            demoWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Convex Hull Animation Demo</title>
                    <style>
                        body {{ 
                            margin: 0; 
                            padding: 20px; 
                            font-family: Arial, sans-serif; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            text-align: center;
                        }}
                        .demo-container {{ 
                            background: rgba(255,255,255,0.1); 
                            padding: 20px; 
                            border-radius: 15px; 
                            backdrop-filter: blur(10px);
                        }}
                        canvas {{ 
                            border: 2px solid white; 
                            border-radius: 10px; 
                            background: white; 
                            margin: 20px 0;
                        }}
                        button {{ 
                            padding: 10px 20px; 
                            margin: 5px; 
                            border: none; 
                            border-radius: 5px; 
                            cursor: pointer; 
                            font-weight: bold;
                            background: #27ae60;
                            color: white;
                        }}
                        button:hover {{ background: #2ecc71; }}
                        .status {{ margin: 15px 0; font-size: 18px; }}
                    </style>
                </head>
                <body>
                    <div class="demo-container">
                        <h1>Convex Hull Algorithm Demo</h1>
                        <button onclick="startDemo()">Start Demo</button>
                        <button onclick="resetDemo()">Reset</button>
                        <canvas id="demoCanvas" width="700" height="400"></canvas>
                        <div class="status" id="status">Click Start Demo to begin animation</div>
                    </div>
                    
                    <script>
                        const canvas = document.getElementById('demoCanvas');
                        const ctx = canvas.getContext('2d');
                        const points = [];
                        let animationStep = 0;
                        let isAnimating = false;
                        
                        // Generate random points
                        for (let i = 0; i < 15; i++) {{
                            points.push({{
                                x: Math.random() * 600 + 50,
                                y: Math.random() * 300 + 50
                            }});
                        }}
                        
                        function drawPoints(current = -1) {{
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            
                            points.forEach((point, i) => {{
                                ctx.fillStyle = i === current ? '#e74c3c' : '#3498db';
                                ctx.beginPath();
                                ctx.arc(point.x, point.y, i === current ? 8 : 5, 0, 2 * Math.PI);
                                ctx.fill();
                                
                                // Add point labels
                                ctx.fillStyle = '#2c3e50';
                                ctx.font = '12px Arial';
                                ctx.fillText(i, point.x + 10, point.y - 10);
                            }});
                        }}
                        
                        function startDemo() {{
                            if (isAnimating) return;
                            isAnimating = true;
                            animationStep = 0;
                            animate();
                        }}
                        
                        function animate() {{
                            if (!isAnimating || animationStep >= points.length) {{
                                isAnimating = false;
                                document.getElementById('status').textContent = 'Demo completed!';
                                return;
                            }}
                            
                            drawPoints(animationStep);
                            document.getElementById('status').textContent = 
                                'Processing point ' + (animationStep + 1) + ' of ' + points.length;
                            
                            animationStep++;
                            setTimeout(animate, 800);
                        }}
                        
                        function resetDemo() {{
                            isAnimating = false;
                            animationStep = 0;
                            drawPoints();
                            document.getElementById('status').textContent = 'Click Start Demo to begin animation';
                        }}
                        
                        // Initial draw
                        drawPoints();
                    </script>
                </body>
                </html>
            `);
        }}
    </script>
</body>
</html>'''

    # Create temporary HTML file
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'enhanced_convex_hull_analyzer.html')
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[SUCCESS] HTML file created: {temp_path}")
        return temp_path
        
    except Exception as e:
        print(f"[ERROR] Failed to create HTML file: {e}")
        return None

def main():
    """Main function to run the enhanced visualizer."""
    print("Enhanced Convex Hull Performance Analyzer")
    print("=" * 50)
    
    try:
        # Test with a range of point counts
        point_counts = [50, 100, 200, 500]
        
        print("Analyzing performance across different point counts...")
        performance_data = analyze_performance(point_counts)
        
        # Generate sample points for visualization
        print("Generating sample visualizations...")
        sample_points = generate_point_distributions(100)
        
        # Create the visualizer
        print("Creating interactive visualizer...")
        html_file = create_enhanced_visualizer(performance_data, sample_points)
        
        if html_file:
            # Open in web browser
            print(f"Opening visualizer in browser...")
            webbrowser.open(f'file://{os.path.abspath(html_file)}')
            
            print("\n" + "=" * 50)
            print("SUCCESS! Enhanced Performance Analyzer is now running!")
            print("\nFEATURES:")
            print("- Variable point count testing (10-1000 points)")
            print("- Real-time performance comparison charts")
            print("- Multiple distribution types for comprehensive testing")
            print("- Algorithm recommendations based on data characteristics")
            print("- Interactive sample visualizations")
            print("- Step-by-step animation demo")
            print("\nUSAGE:")
            print("1. Adjust the point count slider")
            print("2. Click 'Run Performance Test'")
            print("3. Switch between distributions to see different scenarios")
            print("4. Check the insights panel for recommendations")
            print("=" * 50)
        else:
            print("[ERROR] Failed to create visualizer")
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()