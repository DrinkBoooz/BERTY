# BERT & Naive Bayes Emotion Analysis App

This project is a web application that uses a Python/Flask backend with BERT and Naive Bayes models for emotion analysis, and a modern JavaScript frontend for the user interface.

## Project Structure

The project is divided into two main parts: a frontend application and a backend server.

## Example file tree

```bash
BERTY/BERTUI/
├── backend/
│ ├── app.py
│ ├── BAYES/
│ │ └── naive_bayes_emotion_classifier.joblib
│ ├── requirements.txt (assumed)
│ └── .env (included)
│
└── thesis-app/
├── package.json
├── vite.config.js (or .ts)
└── ... (other frontend files)
```

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   **Node.js and npm:** For running the frontend application. ([Download Node.js](https://nodejs.org/))
-   **Python 3.x and pip:** For running the backend server. ([Download Python](https://python.org/))
-   **A terminal or command prompt:** You will need **two separate terminal windows** to run the backend and frontend servers simultaneously.

## Installation

Follow these steps to install the necessary dependencies for both the frontend and backend.

### 1. Backend (Flask API)

First, set up the Python environment and install the required packages.

```bash
# Navigate to the backend directory
cd path/to/BERTY/BERTUI/backend

# (Recommended) Create and activate a virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install the required Python packages
# (A requirements.txt file is assumed to exist)
pip install -r requirements.txt
```
**Note: If a requirements.txt file is not available, you will need to manually install the packages, which likely include flask, flask-cors, torch, transformers, scikit-learn, and python-dotenv.**

### 2. Frontend (Vite App)

Next, install the Node.js packages for the user interface.

```bash
# Navigate to the frontend directory from the project root
cd path/to/BERTY/BERTUI/thesis-app

# Install npm dependencies
npm install
```

## Running the Application

To run the application, you must start both the backend and frontend servers in separate terminals.

### 1. Start the Backend Server

Open your **first terminal window**.

```bash
# Navigate to the backend directory
cd path/to/BERTY/BERTUI/backend

# (If you are not already in it) Activate the virtual environment
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Start the Flask server
python app.py
```

You should see output indicating that the models are loading and the Flask server is running on port 5001. **Leave this terminal running**.
#### Example Terminal Output for running **python app.py**

```
INFO:__main__:Starting Flask server for local development on 0.0.0.0:5001...
* Running on http://127.0.0.1:5001
* Running on http://192.168.1.7:5001
```

### 2. Start the Frontend Server

Open a second, new terminal window.

```bash
# Navigate to the frontend directory
cd path/to/BERTY/BERTUI/thesis-app

# Start the Vite development server
npm run dev --host
```

The **--host** flag makes the application accessible on your local network. You should see output confirming the server is ready.

#### Example Terminal Output for running **npm run dev --host**

```
  VITE v6.3.4  ready in 576 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.7:5173/
  ➜  press h + enter to show help
```

### 2. Start the Frontend Server

The application is now running! Open your web browser and navigate to the local URL provided by Vite:

#### Example Terminal Output for running **npm run dev --host**

```
  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.X:5173/
```

## You can now use the web interface. Any requests made from the frontend will be proxied to your backend Flask server for processing.