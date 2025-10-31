#!/usr/bin/env python3
"""
Kanban API - REST API para gestión de tickets Kanban en Markdown
Versión 0.1 - Arquitectura modular inspirada en kanban.nvim
"""
from flask import Flask
from flask_cors import CORS

from kanban_api.core.config import Config
from kanban_api.routes import tickets_bp, tasks_bp


def create_app():
    """
    Application factory para crear y configurar la app Flask.

    Returns:
        Instancia configurada de Flask
    """
    app = Flask(__name__)

    CORS(app, origins=[
    "http://localhost",
    "http://localhost:*",
    "http://127.0.0.1",
    "http://127.0.0.1:*"
])

    app.register_blueprint(tickets_bp)
    app.register_blueprint(tasks_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint para verificar que la API está funcionando"""
        return {
            'status': 'healthy',
            'version': '2.0.0',
            'kanban_dir': str(Config.KANBAN_DIR)
        }, 200

    @app.route('/config', methods=['GET'])
    def get_config():
        """Retorna la configuración actual (útil para debugging)"""
        return Config.get_config_dict(), 200

    @app.route('/', methods=['GET'])
    def index():
        """Información básica de la API"""
        return {
            'name': 'Kanban API',
            'version': '0.1',
            'description': 'REST API para gestión de tickets Kanban en Markdown',
            'endpoints': {
                'tickets': {
                    'GET /api/current-ticket': 'Obtiene el ticket actual',
                    'GET /api/tickets': 'Lista todos los tickets',
                    'GET /api/ticket/<id>': 'Obtiene un ticket específico',
                    'POST /api/ticket': 'Crea un nuevo ticket',
                    'POST /api/ticket/<id>/task': 'Agrega tarea a un ticket',
                    'PUT /api/ticket/<id>/task/<title>': 'Actualiza una tarea',
                    'DELETE /api/ticket/<id>/task/<title>': 'Elimina una tarea'
                },
                'tasks': {
                    'GET /api/ticket/<id>/task/<title>/description': 'Obtiene descripción de tarea',
                    'POST /api/ticket/<id>/task/<title>/description': 'Crea/actualiza descripción',
                    'GET /api/task/<name>': 'Obtiene metadata (legacy)'
                },
                'legacy_v1': {
                    'GET /current-ticket': 'Alias de /api/current-ticket',
                    'GET /tickets': 'Alias de /api/tickets',
                    'GET /ticket/<id>': 'Alias de /api/ticket/<id>',
                    'GET /task/<name>': 'Alias de /api/task/<name>'
                },
                'utility': {
                    'GET /health': 'Health check',
                    'GET /config': 'Configuración actual'
                }
            },
            'documentation': 'https://github.com/4drian0rtiz/kanbanApi'
        }, 200

    from kanban_api.services import TicketService
    _compat_service = TicketService()

    @app.route('/current-ticket', methods=['GET'])
    def current_ticket_compat():
        """Endpoint de compatibilidad v1"""
        ticket = _compat_service.get_current_ticket()
        if not ticket:
            return {'error': 'No hay ticket actual'}, 404
        return ticket.to_dict(), 200

    @app.route('/tickets', methods=['GET'])
    def list_tickets_compat():
        """Endpoint de compatibilidad v1"""
        tickets = _compat_service.list_all_tickets()
        return {'tickets': tickets}, 200

    @app.route('/ticket/<ticket_id>', methods=['GET'])
    def get_ticket_compat(ticket_id: str):
        """Endpoint de compatibilidad v1"""
        ticket = _compat_service.get_ticket_by_id(ticket_id)
        if not ticket:
            return {'error': f'Ticket {ticket_id} no encontrado'}, 404
        return ticket.to_dict(), 200

    @app.route('/task/<path:task_name>', methods=['GET'])
    def get_task_compat(task_name: str):
        """Endpoint de compatibilidad v1"""
        ticket = _compat_service.get_current_ticket()
        if not ticket:
            return {'error': 'No hay ticket actual'}, 404

        description = _compat_service.get_task_description(
            ticket.ticket_id,
            task_name.replace('_', ' ')
        )

        if not description:
            return {'error': f'No se encontró metadata para la tarea {task_name}'}, 404

        return {
            'task_name': task_name,
            'metadata': description
        }, 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=Config.FLASK_DEBUG,
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT
    )
