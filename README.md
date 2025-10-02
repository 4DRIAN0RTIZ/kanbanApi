# Kanban API

REST API built with Flask to manage and query Kanban tickets stored in Markdown files.

## Description

This API is an extension of the [kanban.nvim](https://github.com/arakkkkk/kanban.nvim) Neovim plugin, specifically designed for ticket-based task management. It provides endpoints to access tickets and tasks from a Kanban system based on Markdown files. The API reads tickets from `~/.local/share/nvim/kanban` and allows querying their status, tasks, and metadata.

## Features

- Query the current active ticket
- Access specific tickets by ID
- List all available tickets
- Retrieve task metadata
- Support for multiple sections (TODO, Work in Progress, Done, Archive)
- CORS enabled for frontend integration

## Requirements

- Python 3.x
- Flask 3.0.0
- flask-cors 4.0.0

## Installation

1. Clone the repository or download the files

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Start the server:
```bash
python3 app.py
```

The server will run on `http://0.0.0.0:5000`

## Endpoints

### `GET /current-ticket`
Returns the current ticket with all its tasks.

**Response:**
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
Retrieves a specific ticket by its ID.

**Example:** `/ticket/T-12345`

### `GET /tickets`
Lists all available tickets.

**Response:**
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
Retrieves metadata for a specific task.

**Example:** `/task/Implement_feature_X`

## File Structure

- `app.py`: Main Flask application
- `requirements.txt`: Project dependencies
- `test_app.py`: Unit tests
- `tampermonkey-script.js`: Browser integration script

## Tampermonkey Browser Integration

The project includes a Tampermonkey userscript (`tampermonkey-script.js`) that provides a visual floating panel in your browser to display and track tasks from the current ticket.

### Features

- Floating, draggable panel showing ticket tasks
- Tasks organized by status (TODO, Doing, Done) in separate tabs
- Visual indicators for task priorities (!!! high, !! medium, ! low)
- Date parsing with urgency indicators (overdue, soon, upcoming)
- Support for hashtags and mentions
- Theme customization (purple, blue, green, orange, pink, dark)
- Real-time data fetching from the API

### Installation

1. Install [Tampermonkey](https://www.tampermonkey.net/) browser extension

2. Open the Tampermonkey dashboard and create a new script

3. Copy the contents of `tampermonkey-script.js` into the editor

4. Update the `@match` URL to match your target website:
```javascript
// @match        https://your-website.com/*
```

5. Save the script

6. Make sure the API is running on `http://localhost:5000` (or update the `API_URL` constant)

### Usage

Once installed and the API is running:
- Click the 📋 button in the top-right corner of your browser to toggle the panel
- Tasks are automatically loaded and organized by status
- Drag the panel by its header to reposition it
- Switch between tabs to view different task categories

### Customization

You can customize the theme by changing the `THEME` constant in the script:
```javascript
const THEME = 'purple'; // Options: 'purple', 'blue', 'green', 'orange', 'pink', 'dark'
```

## Tests

Run the tests:
```bash
pytest test_app.py
```

## Ticket Format

Tickets must be in Markdown format with the following structure (like kanban.nvim):

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

GPL-3.0 License
