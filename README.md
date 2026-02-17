# Retro CRT Street Map

A Python application that visualizes street maps with a retro CRT aesthetic using Pygame.

## Features

- **Retro Aesthetic**: Simulates a CRT screen with scanlines and glowing vector graphics.
- **Data Driven**: Renders map data from GeoJSON files (OpenStreetMap exports).
- **Interactive**: 
  - **Pan**: Left-click and drag to move the map.
  - **Zoom**: Use the mouse wheel to zoom in and out.
- **Color Coded**: Roads are colored based on their classification (e.g., highways are bright, residential roads are dimmer).

## Prerequisites

- Python 3.x
- `pip`

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Install dependencies**:
    You can use the provided Makefile to install the required Python packages (mainly `pygame`).

    ```bash
    make install.requirements.local
    ```

    Alternatively, install manually:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Prepare Data**:
    The application expects a GeoJSON file at `map/lines.geojson`.
    
    If this file is missing, you can export one from [overpass-turbo.eu](https://overpass-turbo.eu/):
    - Navigate to your desired area.
    - usage wizard to search for `highway=*`.
    - Export -> Download -> GeoJSON.
    - Save the file as `map/lines.geojson`.

2.  **Run the Application**:
    Use the Makefile command:

    ```bash
    make run.local
    ```

    Or run the Python script directly:

    ```bash
    python main.py
    ```

## Controls

- **Left Mouse Button**: Click and drag to pan the map.
- **Mouse Wheel**: Zoom in and out.
- **ESC**: Quit the application.

## Project Structure

- `main.py`: Main application logic and entry point.
- `map/`: Directory for storing GeoJSON map data.
- `Makefile`: Helper commands for installation and running.
- `requirements.txt`: Python dependencies.
