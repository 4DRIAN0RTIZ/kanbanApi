#!/usr/bin/env python3
"""
Rutas para operaciones de tickets.
Blueprint que maneja todos los endpoints relacionados con tickets.
"""
from flask import Blueprint, jsonify, request
from kanban_api.services import TicketService

tickets_bp = Blueprint('tickets', __name__, url_prefix='/api')

# Instancia del servicio
ticket_service = TicketService()

@tickets_bp.route('/set-current-ticket/<ticket_id>', methods=['PUT'])
def set_current_ticket(ticket_id: str):
    """
    Establece un ticket como el ticket actual.
    Args:
        ticket_id: ID del ticket
    Returns:
        JSON con el ticket marcado como actual
    """
    try:
        if not ticket_service.get_ticket_by_id(ticket_id):
            return jsonify({'error': f'Ticket {ticket_id} no encontrado'}), 404
        result = ticket_service.set_current_ticket(ticket_id)
        return jsonify({'message': f'Ticket {ticket_id} establecido como actual'}), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tickets_bp.route('/current-ticket', methods=['GET'])
def get_current_ticket():
    """
    Obtiene el ticket actual.

    Returns:
        JSON con el ticket actual y todas sus listas/tareas
    """
    ticket = ticket_service.get_current_ticket()

    if not ticket:
        return jsonify({'error': 'No hay ticket actual'}), 404

    return jsonify(ticket.to_dict()), 200


@tickets_bp.route('/tickets', methods=['GET'])
def list_tickets():
    """
    Lista todos los tickets disponibles.

    Returns:
        JSON con la lista de tickets
    """
    tickets = ticket_service.list_all_tickets()
    return jsonify({'tickets': tickets}), 200


@tickets_bp.route('/ticket/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id: str):
    """
    Obtiene un ticket específico por ID.

    Args:
        ticket_id: ID del ticket

    Returns:
        JSON con el ticket y sus listas/tareas
    """
    ticket = ticket_service.get_ticket_by_id(ticket_id)

    if not ticket:
        return jsonify({'error': f'Ticket {ticket_id} no encontrado'}), 404

    return jsonify(ticket.to_dict()), 200


@tickets_bp.route('/ticket', methods=['POST'])
def create_ticket():
    """
    Crea un nuevo ticket.

    Body:
        {
            "ticket_id": "T-12345",
            "lists": ["TODO", "Doing", "Done"]  // opcional
        }

    Returns:
        JSON con el ticket creado
    """
    data = request.json

    if not data or 'ticket_id' not in data:
        return jsonify({'error': 'Falta el campo ticket_id'}), 400

    ticket_id = data['ticket_id']
    initial_lists = data.get('lists', None)

    try:
        ticket = ticket_service.create_ticket(ticket_id, initial_lists)
        return jsonify(ticket.to_dict()), 201
    except FileExistsError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tickets_bp.route('/ticket/<ticket_id>/task', methods=['POST'])
def add_task(ticket_id: str):
    """
    Agrega una tarea a un ticket.

    Args:
        ticket_id: ID del ticket

    Body:
        {
            "list": "TODO",
            "title": "Nueva tarea",
            "content": ["Nueva tarea", "Descripción adicional"]  // opcional
        }

    Returns:
        JSON con el ticket actualizado
    """
    data = request.json

    if not data or 'list' not in data or 'title' not in data:
        return jsonify({'error': 'Faltan campos obligatorios: list, title'}), 400

    list_name = data['list']
    task_title = data['title']
    task_content = data.get('content', None)

    try:
        ticket = ticket_service.add_task_to_ticket(
            ticket_id,
            list_name,
            task_title,
            task_content
        )
        return jsonify(ticket.to_dict()), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tickets_bp.route('/ticket/<ticket_id>/task/<path:task_title>', methods=['PUT'])
def update_task(ticket_id: str, task_title: str):
    """
    Actualiza una tarea existente.

    Args:
        ticket_id: ID del ticket
        task_title: Título de la tarea

    Body:
        {
            "completed": true,                              // opcional
            "content": ["Título", "Nueva descripción"],    // opcional
            "move_to_list": "Done"                         // opcional
        }

    Returns:
        JSON con el ticket actualizado
    """
    data = request.json or {}

    completed = data.get('completed', None)
    content = data.get('content', None)
    move_to_list = data.get('move_to_list', None)

    try:
        ticket = ticket_service.update_task(
            ticket_id,
            task_title,
            completed=completed,
            new_content=content,
            move_to_list=move_to_list
        )
        return jsonify(ticket.to_dict()), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tickets_bp.route('/ticket/<ticket_id>/task/<path:task_title>', methods=['DELETE'])
def delete_task(ticket_id: str, task_title: str):
    """
    Elimina una tarea.

    Args:
        ticket_id: ID del ticket
        task_title: Título de la tarea

    Returns:
        JSON con el ticket actualizado
    """
    try:
        ticket = ticket_service.delete_task(ticket_id, task_title)
        return jsonify(ticket.to_dict()), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
