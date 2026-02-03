#!/usr/bin/env python3
"""
Markdown Reader - Parsea archivos markdown a objetos Ticket.
Basado en markdown/reader.lua de kanban.nvim
"""
import re
from pathlib import Path
from typing import List as TypingList, Optional

from kanban_api.models import Ticket, List, Task
from kanban_api.core.config import Config


class MarkdownReader:
    """
    Parser de archivos markdown a objetos Ticket.
    Replica la lógica de kanban.nvim/lua/kanban/markdown/reader.lua
    """

    def __init__(self):
        self.config = Config

    def read(self, file_path: Path, ticket_id: Optional[str] = None) -> Ticket:
        """
        Lee un archivo markdown y lo convierte a un objeto Ticket.

        Args:
            file_path: Ruta al archivo markdown
            ticket_id: ID del ticket (opcional, se infiere del nombre del archivo)

        Returns:
            Objeto Ticket con listas y tareas
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        # Inferir ticket_id del nombre del archivo si no se proporciona
        if not ticket_id:
            ticket_id = file_path.stem

        ticket = Ticket(ticket_id=ticket_id, file_path=file_path)
        content = file_path.read_text()

        current_list: Optional[List] = None
        current_task: Optional[Task] = None
        in_frontmatter = False
        in_footer = False

        for line in content.split('\n'):
            # Detectar frontmatter (YAML header)
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue

            # Detectar footer (kanban:settings)
            if line.strip().startswith('%% kanban:settings'):
                in_footer = True
                continue

            # Saltar frontmatter y footer
            if in_frontmatter or in_footer:
                continue

            # Detectar encabezado de lista (## List Title)
            list_match = re.match(self.config.PATTERNS['list_header'], line)
            if list_match:
                # Guardar tarea anterior si existe
                if current_task and current_list:
                    current_list.add_task(current_task)
                    current_task = None

                # Guardar lista anterior si existe
                if current_list:
                    ticket.add_list(current_list)

                # Crear nueva lista
                list_title = list_match.group(1).strip()
                current_list = List(title=list_title)
                continue

            # Detectar tarea (- [ ] Task title)
            task_match = re.match(self.config.PATTERNS['task_line'], line)
            if task_match:
                # Guardar tarea anterior si existe
                if current_task and current_list:
                    current_list.add_task(current_task)

                # Crear nueva tarea
                checkbox_status = task_match.group(1)
                task_title = task_match.group(2).strip()

                # Ignorar tareas vacías
                if not task_title:
                    current_task = None
                    continue

                current_task = Task(
                    title=task_title,
                    completed=(checkbox_status == 'x'),
                    content=[task_title]
                )
                continue

            # Líneas de contenido de tarea (indentadas con tab)
            if line.startswith('\t') and current_task:
                content_line = line[1:]  # Remover tab inicial
                current_task.content.append(content_line)
                # Re-parsear metadata con el nuevo contenido
                current_task._parse_metadata()
                continue

        # Agregar última tarea y lista
        if current_task and current_list:
            current_list.add_task(current_task)

        if current_list:
            ticket.add_list(current_list)

        return ticket

    def read_task_description(
        self,
        ticket_file: Path,
        task_title: str
    ) -> Optional[str]:
        """
        Lee el archivo de descripción de una tarea.

        Args:
            ticket_file: Ruta al archivo del ticket
            task_title: Título de la tarea

        Returns:
            Contenido del archivo de descripción o None
        """
        # Buscar en el mismo directorio que el ticket (raíz de kanban)
        kanban_dir = ticket_file.parent

        # Posibles nombres de archivo (todos con prefijo "tasks")
        possible_names = [
            f'tasks{task_title.replace(" ", "_")}.md',
            f'tasks{task_title.replace(" ", "-")}.md',
            f'tasks{task_title.lower().replace(" ", "_")}.md',
            f'tasks{task_title.upper().replace(" ", "_")}.md',
        ]

        for name in possible_names:
            desc_file = kanban_dir / name
            if desc_file.exists():
                return desc_file.read_text()

        return None
