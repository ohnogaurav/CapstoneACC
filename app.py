import os
import sys
from flask import Flask, render_template, send_from_directory

import usecase1
import usecase2
import usecase3
import usecase4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "chicago_crime.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMPLATE_DIR = os.path.join(BASE_DIR, "Template")

# Initialize Flask with custom Template folder
app = Flask(__name__, template_folder=TEMPLATE_DIR)


def check_and_initialize():
    """
    Checks if SQLite database and output graphs exist.
    If not initialized, runs all 4 use cases in order.
    """
    required_charts = [
        "crime_trend_yearly.png",
        "top_10_crime_types.png",
        "heatmap_month_day.png",
        "top_community_areas.png",
        "hourly_crime_intensity.png",
        "community_box_plot.png",
        "correlation_heatmap.png"
    ]
    
    db_exists = os.path.exists(DB_PATH)
    charts_exist = all(os.path.exists(os.path.join(OUTPUT_DIR, c)) for c in required_charts)
    
    if not db_exists or not charts_exist:
        print("[INIT] System uninitialized or missing required outputs. Running Use Cases 1-4...")
        usecase1.run_usecase1()
        usecase2.run_usecase2()
        usecase3.run_usecase3()
        usecase4.run_usecase4()
        print("[INIT] All Use Cases executed and output files generated successfully.")
    else:
        print("[INIT] Database and output charts verified. Ready to serve.")


# Serve static CSS from Template directory
@app.route('/style.css')
def serve_css():
    return send_from_directory(TEMPLATE_DIR, 'style.css')


# Serve generated graph images directly from output directory
@app.route('/output/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


# Route 1: Dashboard Home
@app.route('/')
def index():
    uc1_data = usecase1.run_usecase1()
    uc2_data = usecase2.run_usecase2()
    uc3_data = usecase3.run_usecase3()
    return render_template('index.html', uc1=uc1_data, uc2=uc2_data, uc3=uc3_data)


# Route 2: Use Case 1 Page
@app.route('/usecase1')
def page_usecase1():
    uc1_data = usecase1.run_usecase1()
    return render_template('usecase1.html', data=uc1_data)


# Route 3: Use Case 2 Page
@app.route('/usecase2')
def page_usecase2():
    uc2_data = usecase2.run_usecase2()
    return render_template('usecase2.html', data=uc2_data)


# Route 4: Use Case 3 Page
@app.route('/usecase3')
def page_usecase3():
    uc3_data = usecase3.run_usecase3()
    return render_template('usecase3.html', data=uc3_data)


# Route 5: Use Case 4 Page
@app.route('/usecase4')
def page_usecase4():
    uc4_data = usecase4.run_usecase4()
    return render_template('usecase4.html', data=uc4_data)


if __name__ == '__main__':
    check_and_initialize()
    if '--no-server' in sys.argv:
        print("Initialization test complete (--no-server flag specified).")
    else:
        print("Starting Flask Web Application on http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=True)
