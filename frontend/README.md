# AEO Agent View (Frontend)

This is a **Vite + React + Tailwind** dashboard to visualize the AEO Report.

## Setup
Because of environment restrictions, the dependencies were not installed automatically.

1.  **Install Dependencies**:
    ```bash
    cd frontend
    npm install
    # OR
    yarn install
    ```

2.  **Load Data**:
    Run a backend scan first:
    ```bash
    cd ..
    python -m backend.aeo scan https://your-site.com
    ```
    Then copy the report to the public folder:
    ```bash
    cp backend/output/aeo-report.json frontend/public/data.json
    ```

3.  **Run Dev Server**:
    ```bash
    npm run dev
    ```
    Open `http://localhost:5173` to see the dashboard.
