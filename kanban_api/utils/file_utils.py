#!/usr/bin/env python3
"""
Utilidades para operaciones de archivos.
Similar a utils.lua en kanban.nvim
"""
from pathlib import Path
from typing import Optional

from kanban_api.core.config import Config


class FileUtils:
    """Utilidades para manejo de archivos del kanban"""

    @staticmethod
    def get_current_ticket_id() -> Optional[str]:
        """Lee el ticket actual desde ~/.last_ticket"""
        last_ticket_file = Config.LAST_TICKET_FILE

        if not last_ticket_file.exists():
            return None

        return last_ticket_file.read_text().strip()

    @staticmethod
    def set_current_ticket_id(ticket_id: str) -> None:
        """Guarda el ticket actual en ~/.last_ticket"""
        Config.LAST_TICKET_FILE.write_text(ticket_id)

    @staticmethod
    def find_ticket_file(ticket_id: str) -> Optional[Path]:
        """
        Busca el archivo del ticket (puede ser T-XXXXX.md, XXXXX.md, etc.)

        Args:
            ticket_id: ID del ticket a buscar

        Returns:
            Path al archivo del ticket o None si no se encuentra
        """
        kanban_dir = Config.KANBAN_DIR

        if not kanban_dir.exists():
            return None

        # Candidatos posibles
        candidates = [
            kanban_dir / f'{ticket_id}.md',
            kanban_dir / f'T-{ticket_id}.md',
            kanban_dir / f't-{ticket_id}.md'
        ]

        # Buscar en candidatos directos
        for candidate in candidates:
            if candidate.exists():
                return candidate

        # Buscar en el directorio si no se encuentra directamente
        for file in kanban_dir.glob('*.md'):
            # Ignorar archivos de descripción
            if file.stem.startswith('tasks'):
                continue

            if ticket_id.lower() in file.stem.lower():
                return file

        return None

    @staticmethod
    def list_all_tickets() -> list[dict]:
        """
        Lista todos los tickets disponibles.

        Returns:
            Lista de diccionarios con información de tickets
        """
        kanban_dir = Config.KANBAN_DIR

        if not kanban_dir.exists():
            return []

        tickets = []

        for file in kanban_dir.glob('*.md'):
            # Ignorar archivos de descripción
            if file.stem.startswith('tasks'):
                continue

            tickets.append({
                'id': file.stem,
                'file': str(file),
                'modified': file.stat().st_mtime
            })

        # Ordenar por fecha de modificación (más reciente primero)
        tickets.sort(key=lambda x: x['modified'], reverse=True)

        return tickets
