#!/usr/bin/env python3
"""
Markdown Writer - Serializa objetos Ticket a archivos markdown.
Basado en markdown/writer.lua de kanban.nvim
"""
from pathlib import Path
from typing import List as TypingList

from kanban_api.models import Ticket
from kanban_api.core.config import Config


class MarkdownWriter:
    """
    Serializador de objetos Ticket a archivos markdown.
    Replica la lógica de kanban.nvim/lua/kanban/markdown/writer.lua
    """

    def __init__(self):
        self.config = Config

    def write(self, ticket: Ticket, file_path: Path) -> None:
        """
        Escribe un objeto Ticket a un archivo markdown.

        Args:
            ticket: Objeto Ticket a serializar
            file_path: Ruta donde guardar el archivo
        """
        lines: TypingList[str] = []

        # 1. Header (frontmatter)
        lines.extend(self.config.MARKDOWN['header'])
        lines.append('')  # Línea en blanco después del header

        # 2. Listas y tareas
        for list_obj in ticket.lists:
            # Título de la lista
            list_header = f"{self.config.MARKDOWN['list_head']}{list_obj.title}"
            lines.append(list_header)
            lines.append('')  # Línea en blanco después del título

            # Tareas de la lista
            for task in list_obj.tasks:
                # Checkbox basado en estado de completado
                checkbox = '[x]' if task.completed else '[ ]'
                task_line = f"- {checkbox} {task.title}"
                lines.append(task_line)

                # Contenido adicional de la tarea (tab-indented)
                # Primera línea es el título, las demás son contenido adicional
                for content_line in task.content[1:]:
                    lines.append(f"\t{content_line}")

            lines.append('')  # Línea en blanco después de las tareas

        # 3. Footer (settings)
        lines.extend(self.config.MARKDOWN['footer'])

        # Escribir archivo
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text('\n'.join(lines))

    def create_task_description(
        self,
        ticket_file: Path,
        task_title: str,
        content: str
    ) -> Path:
        """
        Crea o actualiza el archivo de descripción de una tarea.

        Args:
            ticket_file: Ruta al archivo del ticket
            task_title: Título de la tarea
            content: Contenido de la descripción

        Returns:
            Ruta al archivo de descripción creado
        """
        desc_folder = self.config.get_description_folder(ticket_file)
        desc_folder.mkdir(parents=True, exist_ok=True)

        # Nombre del archivo (usando underscores)
        filename = f"{task_title.replace(' ', '_')}.md"
        desc_file = desc_folder / filename

        desc_file.write_text(content)
        return desc_file
