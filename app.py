#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import os
import re
from pathlib import Path

app = Flask(__name__)
# Permitir CORS para todas las rutas
CORS(app)

KANBAN_DIR = Path.home() / '.local/share/nvim/kanban'
LAST_TICKET_FILE = Path.home() / '.last_ticket'

def get_current_ticket():
    """Lee el ticket actual desde ~/.last_ticket"""
    if LAST_TICKET_FILE.exists():
        return LAST_TICKET_FILE.read_text().strip()
    return None

def find_ticket_file(ticket_id):
    """Busca el archivo del ticket (puede ser T-XXXXX.md o XXXXX.md)"""
    candidates = [
        KANBAN_DIR / f'{ticket_id}.md',
        KANBAN_DIR / f'T-{ticket_id}.md'
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Buscar en el directorio si no se encuentra directamente
    for file in KANBAN_DIR.glob('*.md'):
        if ticket_id in file.stem:
            return file

    return None

def parse_ticket_tasks(ticket_file):
    """Parsea las tareas del archivo del ticket según la sección donde están"""
    content = ticket_file.read_text()
    tasks = []

    # Detectar la sección actual
    current_section = None

    for line in content.split('\n'):
        # Detectar cambio de sección
        if line.startswith('## '):
            section_name = line[3:].strip().lower()
            if 'todo' in section_name:
                current_section = 'todo'
            elif 'work in progress' in section_name or 'doing' in section_name:
                current_section = 'doing'
            elif 'done' in section_name:
                current_section = 'done'
            elif 'archive' in section_name:
                current_section = 'archive'
            else:
                current_section = None
            continue

        # Buscar tareas
        task_match = re.match(r'- \[([ x])\] (.+)', line)
        if task_match and current_section:
            status = task_match.group(1)
            task_name = task_match.group(2).strip()

            # Ignorar tareas vacías
            if not task_name:
                continue

            # Determinar estado según sección
            is_done = (status == 'x') or (current_section == 'done')
            is_in_progress = (current_section == 'doing')

            tasks.append({
                'name': task_name,
                'done': is_done,
                'in_progress': is_in_progress,
                'metadata': get_task_metadata(task_name)
            })

    return tasks

def get_task_metadata(task_name):
    """Busca la metadata de una tarea en archivos tasks*"""
    # Normalizar el nombre de la tarea para buscar el archivo
    task_file_name = f'tasks{task_name.replace(" ", "_")}.md'
    task_file = KANBAN_DIR / task_file_name

    if task_file.exists():
        return task_file.read_text()

    return None

@app.route('/current-ticket', methods=['GET'])
def current_ticket():
    """Devuelve el ticket actual con todas sus tareas y metadata"""
    ticket_id = get_current_ticket()

    if not ticket_id:
        return jsonify({'error': 'No hay ticket actual'}), 404

    ticket_file = find_ticket_file(ticket_id)

    if not ticket_file:
        return jsonify({'error': f'No se encontró el archivo para el ticket {ticket_id}'}), 404

    tasks = parse_ticket_tasks(ticket_file)

    return jsonify({
        'ticket_id': ticket_id,
        'file': str(ticket_file),
        'tasks': tasks
    })

@app.route('/ticket/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Devuelve un ticket específico con sus tareas"""
    ticket_file = find_ticket_file(ticket_id)

    if not ticket_file:
        return jsonify({'error': f'No se encontró el ticket {ticket_id}'}), 404

    tasks = parse_ticket_tasks(ticket_file)

    return jsonify({
        'ticket_id': ticket_id,
        'file': str(ticket_file),
        'tasks': tasks
    })

@app.route('/task/<path:task_name>', methods=['GET'])
def get_task(task_name):
    """Devuelve la metadata de una tarea específica"""
    metadata = get_task_metadata(task_name)

    if not metadata:
        return jsonify({'error': f'No se encontró metadata para la tarea {task_name}'}), 404

    return jsonify({
        'task_name': task_name,
        'metadata': metadata
    })

@app.route('/tickets', methods=['GET'])
def list_tickets():
    """Lista todos los tickets disponibles"""
    tickets = []

    for file in KANBAN_DIR.glob('*.md'):
        if not file.stem.startswith('tasks'):
            tickets.append({
                'id': file.stem,
                'file': str(file)
            })

    return jsonify({'tickets': tickets})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
