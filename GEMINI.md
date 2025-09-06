# GEMINI.md: OurLibrary Project

## Project Overview

This project, "OurLibrary", is a cross-platform desktop application built with Electron, designed to provide free access to a large collection of educational books. It also functions as a web application, likely for broader accessibility and testing purposes.

The application's mission is to democratize education by providing a completely free, offline-capable digital library.

### Core Technologies:

*   **Frontend:** HTML, Tailwind CSS, and vanilla JavaScript.
*   **Desktop Application:** Electron, using Node.js for the main process.
*   **Database:** SQLite. In the desktop app, it uses the `sqlite3` Node.js module. In the web version, it uses `sql.js`, a WebAssembly port of SQLite.
*   **Authentication:** Firebase is used for user authentication, supporting both Google OAuth and email/password registration.
*   **Web Server (for testing):** A simple Python HTTP server.

### Architecture:

The application has a clever dual-mode architecture:

1.  **Desktop Mode (Electron):** The `main.js` file is the entry point. It creates a native window and loads the frontend. A `preload.js` script securely exposes backend functionality (like database access) to the frontend via an `api` object on the `window`.

2.  **Web Mode:** The `launch_server.py` script starts a simple web server. The `web-shim.js` file is crucial here. It detects that it's running in a browser, loads `sql.js` and the SQLite database file, and then creates a compatible `window.api` object that mimics the one provided by Electron's preload script. This allows the same frontend code to run in both environments.

## Building and Running

### Desktop Application

To run the application in desktop mode, use the following commands:

1.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

2.  **Run the application:**
    ```bash
    npm start
    ```
    This command executes `electron . --no-sandbox`.

### Web Browser Testing

To run the application in a web browser for testing:

1.  **Run the Python web server:**
    ```bash
    python launch_server.py
    ```
    This will start a local server on an available port (e.g., `http://localhost:8080`) and attempt to open the main library page.

## Development Conventions

*   **Dual-Mode Compatibility:** All frontend code, especially database interactions, should be written to work with the `window.api` object. This object is provided by `preload.js` in Electron and polyfilled by `web-shim.js` in the browser.
*   **Database:** The database schema is located in `Data/Databases/OurLibrary.db`. Any changes to the schema must be compatible with both `sqlite3` and `sql.js`.
*   **Configuration:**
    *   Main application settings are in `Config/ourlibrary_config.json`.
    *   Google/Firebase settings are in `Config/ourlibrary_google_config.json`.
*   **Dependencies:**
    *   Node.js dependencies are managed in `package.json`.
    *   Python dependencies (for helper scripts) are in `requirements.txt`.
*   **Entry Points:**
    *   **Desktop:** `main.js`
    *   **Web/Registration:** `index.html`
    *   **Main Library UI:** `new-desktop-library.html`