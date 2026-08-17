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

# Initialize Flask app
app = Flask(__name__, template_folder=TEMPLATE_DIR)


def initialize_project():
    """Run all use cases if database or output charts are missing"""
    if not os.path.exists(DB_PATH) or not os.path.exists(OUTPUT_DIR):
        print("Initializing project and generating data/charts...")
        usecase1.run_usecase1()
        usecase2.run_usecase2()
        usecase3.run_usecase3()
        usecase4.run_usecase4()


# Serve CSS stylesheet
@app.route('/style.css')
def serve_css():
    return send_from_directory(TEMPLATE_DIR, 'style.css')


# Serve generated graph images from output folder
@app.route('/output/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


# Main Dashboard route
@app.route('/')
def index():
    uc1_data = usecase1.run_usecase1()
    uc2_data = usecase2.run_usecase2()
    return render_template('index.html', uc1=uc1_data, uc2=uc2_data)


# Use Case 1 route
@app.route('/usecase1')
def page_usecase1():
    uc1_data = usecase1.run_usecase1()
    return render_template('usecase1.html', data=uc1_data)


# Use Case 2 route
@app.route('/usecase2')
def page_usecase2():
    uc2_data = usecase2.run_usecase2()
    return render_template('usecase2.html', data=uc2_data)


# Use Case 3 route
@app.route('/usecase3')
def page_usecase3():
    uc3_data = usecase3.run_usecase3()
    return render_template('usecase3.html', data=uc3_data)


# Use Case 4 route
@app.route('/usecase4')
def page_usecase4():
    uc4_data = usecase4.run_usecase4()
    return render_template('usecase4.html', data=uc4_data)


# Dummy placeholder route for the future "upload your own CSV" feature.
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    return "Custom CSV upload", 200


if __name__ == '__main__':
    initialize_project()
    if '--no-server' in sys.argv:
        print("Initialization complete.")
    else:
        print("Starting Flask app on http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=True)
