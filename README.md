Convex Hull Visualizer

This project implements and visualizes Convex Hull algorithms – specifically Jarvis March (Gift Wrapping) and Graham Scan.
It is designed to help understand the working of convex hull algorithms through interactive visualization and corner-case analysis.

🚀 Features

Implementation of:

Jarvis March (Gift Wrapping)

Graham Scan

Step-by-step visualization of algorithm progress.

Handles corner cases (collinear points, duplicate points, minimal input).

Comparison of algorithm efficiency and behavior.

User-friendly interface to add or generate random points.

📂 Project Structure
├── convex_hull_visualizer.py   # Main script with algorithms & visualization
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation

⚙️ Installation

Clone the repository:

git clone https://github.com/your-username/convex-hull-visualizer.git
cd convex-hull-visualizer


Install dependencies:

pip install -r requirements.txt

▶️ Usage

Run the visualizer:

python convex_hull_visualizer.py


Left-click: Add points manually.

Random Button: Generate random points.

Run Button: Choose algorithm (Jarvis March or Graham Scan) and visualize.

📊 Algorithms Explained

Jarvis March (Gift Wrapping):

Time Complexity: O(nh)

Simple to understand, works well for small sets.

Graham Scan:

Time Complexity: O(n log n)

Efficient and widely used.

🖼️ Demo

(Add a screenshot or GIF of your visualization here)

📝 Future Improvements

Add QuickHull algorithm.

Compare runtime between algorithms.

Export convex hull results to CSV or image.

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss.

📄 License

This project is licensed under the MIT License.
