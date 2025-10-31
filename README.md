# Kanban API

A RESTful API built with Flask for managing and querying Kanban tickets stored in Markdown files.

## Overview

This API extends the [kanban.nvim](https://github.com/arakkkkk/kanban.nvim) Neovim plugin to provide programmatic access to ticket-based task management. It offers HTTP endpoints to query tickets and tasks from a Markdown-based Kanban system. The API reads ticket data from `~/.local/share/nvim/kanban` and provides comprehensive access to ticket status, task information, and metadata.

## Key Features

- Query current active tickets with full task details
- Access individual tickets by unique identifier
- List all available tickets in the system
- Retrieve comprehensive task metadata
- Multi-section support (TODO, Work in Progress, Done, Archive)
- CORS-enabled endpoints for seamless frontend integration

## Requirements

- Python 3.x
- Flask 3.0.0
- flask-cors 4.0.0

## Installation

### Step 1: Clone Repository

Clone the repository or download the source files to your local machine.

### Step 2: Set Up Virtual Environment

Create and activate a Python virtual environment:

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python3 -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Launch the API server with the following command:
```bash
python3 app.py
```

The server will be accessible at `http://0.0.0.0:5000`

## API Endpoints

### `GET /current-ticket`

Retrieves the currently active ticket with all associated tasks.

**Response Example:**
```json
{
  "ticket_id": "T-12345",
  "file": "/home/user/.local/share/nvim/kanban/T-12345.md",
  "tasks": [
    {
      "name": "Implement feature X",
      "done": false,
      "in_progress": true,
      "metadata": "..."
    }
  ]
}
```

### `GET /ticket/<ticket_id>`

Retrieves a specific ticket by its unique identifier.

**Example Request:** `/ticket/T-12345`

### `GET /tickets`

Returns a complete list of all available tickets in the system.

**Response Example:**
```json
{
  "tickets": [
    {
      "id": "T-12345",
      "file": "/home/user/.local/share/nvim/kanban/T-12345.md"
    }
  ]
}
```

### `GET /task/<task_name>`

Retrieves comprehensive metadata for a specified task.

**Example Request:** `/task/Implement_feature_X`

## Project Structure

```
kanban-api/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── test_app.py               # Unit test suite
└── tampermonkey-script.js    # Browser integration userscript
```

## Browser Integration

The project includes a Tampermonkey userscript (`tampermonkey-script.js`) that provides an interactive floating panel for displaying and tracking tasks from the current ticket directly in your browser.

### Browser Extension Features

- Draggable floating panel with ticket task overview
- Status-based task organization (TODO, Doing, Done) with tabbed interface
- Priority indicators for task classification (high, medium, low)
- Date parsing with urgency status (overdue, soon, upcoming)
- Hashtag and mention support for enhanced task context
- Customizable theme options (purple, blue, green, orange, pink, dark)
- Real-time synchronization with API endpoints

### Browser Extension Installation

1. Install the [Tampermonkey](https://www.tampermonkey.net/) browser extension for your browser

2. Open the Tampermonkey dashboard and create a new userscript

3. Copy the contents of `tampermonkey-script.js` into the script editor

4. Configure the `@match` directive to target your desired website:
   ```javascript
   // @match        https://your-website.com/*
   ```

5. Save the userscript configuration

6. Ensure the API server is running at `http://localhost:5000` or update the `API_URL` constant accordingly

### Browser Extension Usage

After installation and with the API server running:

- Click the panel toggle button in the top-right corner of your browser to show/hide the task panel
- Tasks are automatically fetched and organized by their current status
- Reposition the panel by dragging its header bar
- Navigate between tabs to view tasks in different categories

### Theme Customization

Modify the `THEME` constant in the userscript to apply a different color scheme:

```javascript
const THEME = 'purple'; // Available options: 'purple', 'blue', 'green', 'orange', 'pink', 'dark'
```

## Testing

Execute the test suite using pytest:

```bash
pytest test_app.py
```

## Ticket Format Specification

Tickets are stored as Markdown files following the kanban.nvim structure:

```markdown
## TODO
- [ ] Pending task

## Work in Progress
- [ ] Task in progress

## Done
- [x] Completed task

## Archive
- [x] Archived task
```

## License

This project is licensed under the GPL-3.0 License.
