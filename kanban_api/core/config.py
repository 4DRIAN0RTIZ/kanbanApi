#!/usr/bin/env python3
"""
Configuración centralizada de la aplicación.
Inspirado en la estructura de ops.lua de kanban.nvim
"""
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuración global de la aplicación Kanban API"""

    # Directorios
    KANBAN_DIR = Path.home() / '.local/share/nvim/kanban'
    LAST_TICKET_FILE = Path.home() / '.last_ticket'

    # Configuración de Markdown (similar a kanban.nvim markdown options)
    MARKDOWN = {
        'list_head': '## ',                    # Prefijo de encabezado de lista
        'description_folder': 'tasks',         # Carpeta para archivos de descripción
        'due_format': 'YYYY-MM-DD',           # Formato de fecha
        'header': [                            # Frontmatter del archivo
            '---',
            'kanban-plugin: basic',
            '---',
            ''
        ],
        'footer': [                            # Footer del archivo
            '',
            '%% kanban:settings',
            '```',
            '{"kanban-plugin":"basic"}',
            '```',
            '%%'
        ]
    }

    # Patrones de parsing
    PATTERNS = {
        'task_line': r'- \[([ x])\] (.+)',        # Formato de tarea
        'list_header': r'^## (.+)$',              # Formato de lista
        'due_date': r'@(\d{4}-\d{2}-\d{2})',     # Due date (@YYYY-MM-DD)
        'tag': r'#(\w+)',                         # Tags (#tag)
        'priority_high': r'!!!',                  # Alta prioridad
        'priority_medium': r'!!',                 # Media prioridad
        'priority_low': r'!',                     # Baja prioridad
    }

    # Nombres de secciones reconocidas (mapeo a estados)
    SECTION_MAPPINGS = {
        'todo': ['todo', 'to do', 'pending'],
        'doing': ['work in progress', 'doing', 'in progress', 'wip'],
        'done': ['done', 'completed', 'finished'],
        'archive': ['archive', 'archived']
    }

    # Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    @classmethod
    def get_description_folder(cls, ticket_path: Path) -> Path:
        """Obtiene la carpeta de descripciones para un ticket"""
        return ticket_path.parent / cls.MARKDOWN['description_folder']

    @classmethod
    def normalize_section_name(cls, section: str) -> str:
        """
        Normaliza un nombre de sección a un estado estándar.
        Similar a cómo kanban.nvim identifica secciones.
        """
        section_lower = section.lower().strip()

        for standard_name, aliases in cls.SECTION_MAPPINGS.items():
            if section_lower in aliases:
                return standard_name

        return 'unknown'

    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Retorna la configuración como diccionario"""
        return {
            'kanban_dir': str(cls.KANBAN_DIR),
            'last_ticket_file': str(cls.LAST_TICKET_FILE),
            'markdown': cls.MARKDOWN,
            'patterns': cls.PATTERNS,
            'section_mappings': cls.SECTION_MAPPINGS
        }
