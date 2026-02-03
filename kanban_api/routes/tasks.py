#!/usr/bin/env python3
"""
Rutas para operaciones de tareas individuales (metadata/descripciones).
Blueprint que maneja endpoints de descripciones de tareas.
"""
from flask import Blueprint, jsonify, request
from kanban_api.services import TicketService

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')

# Instancia del servicio
ticket_service = TicketService()


@tasks_bp.route('/ticket/<ticket_id>/task/<path:task_title>/description', methods=['GET'])
def get_task_description(ticket_id: str, task_title: str):
    """
    Obtiene la descripción/metadata de una tarea.

    Args:
        ticket_id: ID del ticket
        task_title: Título de la tarea

    Returns:
        JSON con la descripción de la tarea
    """
    description = ticket_service.get_task_description(ticket_id, task_title)

    if not description:
        return jsonify({
            'error': f'No se encontró descripción para la tarea {task_title}'
        }), 404

    return jsonify({
        'ticket_id': ticket_id,
        'task_title': task_title,
        'description': description
    }), 200


@tasks_bp.route('/ticket/<ticket_id>/task/<path:task_title>/description', methods=['POST', 'PUT'])
def create_or_update_task_description(ticket_id: str, task_title: str):
    """
    Crea o actualiza la descripción de una tarea.

    Args:
        ticket_id: ID del ticket
        task_title: Título de la tarea

    Body:
        {
            "description": "Contenido de la descripción en markdown"
        }

    Returns:
        JSON con la ruta al archivo de descripción
    """
    data = request.json

    if not data or 'description' not in data:
        return jsonify({'error': 'Falta el campo description'}), 400

    description = data['description']

    try:
        desc_file = ticket_service.create_task_description(
            ticket_id,
            task_title,
            description
        )

        return jsonify({
            'ticket_id': ticket_id,
            'task_title': task_title,
            'description_file': str(desc_file),
            'message': 'Descripción creada/actualizada exitosamente'
        }), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Compatibilidad con endpoint antiguo
@tasks_bp.route('/task/<path:task_name>', methods=['GET'])
def get_task_metadata_legacy(task_name: str):
    """
    Endpoint legacy para compatibilidad con versión anterior.
    Busca en el ticket actual.

    Args:
        task_name: Nombre de la tarea

    Returns:
        JSON con la metadata de la tarea
    """
    ticket = ticket_service.get_current_ticket()

    if not ticket:
        return jsonify({'error': 'No hay ticket actual'}), 404

    description = ticket_service.get_task_description(
        ticket.ticket_id,
        task_name.replace('_', ' ')
    )

    if not description:
        return jsonify({
            'error': f'No se encontró metadata para la tarea {task_name}'
        }), 404

    return jsonify({
        'task_name': task_name,
        'metadata': description
    }), 200
