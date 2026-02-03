#!/usr/bin/env python3
"""
Servicio de gestión de tickets.
Contiene toda la lógica de negocio para operaciones CRUD de tickets.
Similar a la organización de fn/ en kanban.nvim
"""
from pathlib import Path
from typing import Optional

from kanban_api.models import Ticket, List, Task
from kanban_api.parsers import MarkdownReader, MarkdownWriter
from kanban_api.utils import FileUtils
from kanban_api.core.config import Config


class TicketService:
    """Servicio para gestión de tickets"""

    def __init__(self):
        self.reader = MarkdownReader()
        self.writer = MarkdownWriter()
        self.file_utils = FileUtils()
        self.config = Config

    # ========= Para marcar como actual =========
    def set_current_ticket(self, ticket_id: str) -> None:
        """
        Establece el ticket actual (en ~/.last_ticket).
        Args:
            ticket_id: ID del ticket a establecer como actual
        """
        self.file_utils.set_current_ticket_id(ticket_id)

    # ========== Operaciones de lectura ==========

    def get_current_ticket(self) -> Optional[Ticket]:
        """
        Obtiene el ticket actual (desde ~/.last_ticket).

        Returns:
            Objeto Ticket o None si no hay ticket actual
        """
        ticket_id = self.file_utils.get_current_ticket_id()

        if not ticket_id:
            return None

        return self.get_ticket_by_id(ticket_id)

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """
        Obtiene un ticket específico por su ID.

        Args:
            ticket_id: ID del ticket

        Returns:
            Objeto Ticket o None si no se encuentra
        """
        ticket_file = self.file_utils.find_ticket_file(ticket_id)

        if not ticket_file:
            return None

        return self.reader.read(ticket_file, ticket_id)

    def list_all_tickets(self) -> list[dict]:
        """
        Lista todos los tickets disponibles.

        Returns:
            Lista de metadatos de tickets
        """
        return self.file_utils.list_all_tickets()

    def get_task_description(
        self,
        ticket_id: str,
        task_title: str
    ) -> Optional[str]:
        """
        Obtiene la descripción/metadata de una tarea.

        Args:
            ticket_id: ID del ticket
            task_title: Título de la tarea

        Returns:
            Contenido de la descripción o None
        """
        ticket_file = self.file_utils.find_ticket_file(ticket_id)

        if not ticket_file:
            return None

        return self.reader.read_task_description(ticket_file, task_title)

    # ========== Operaciones de escritura ==========

    def create_ticket(
        self,
        ticket_id: str,
        initial_lists: Optional[list[str]] = None
    ) -> Ticket:
        """
        Crea un nuevo ticket.

        Args:
            ticket_id: ID del nuevo ticket
            initial_lists: Nombres de listas iniciales (default: TODO, Doing, Done)

        Returns:
            Objeto Ticket creado
        """
        if initial_lists is None:
            initial_lists = ['TODO', 'Work in Progress', 'Done', 'Archive']

        # Crear ticket
        ticket_file = self.config.KANBAN_DIR / f'{ticket_id}.md'

        if ticket_file.exists():
            raise FileExistsError(f"El ticket {ticket_id} ya existe")

        ticket = Ticket(ticket_id=ticket_id, file_path=ticket_file)

        # Crear listas iniciales
        for list_name in initial_lists:
            ticket.add_list(List(title=list_name))

        # Guardar ticket
        self.writer.write(ticket, ticket_file)

        # Establecer como ticket actual
        self.file_utils.set_current_ticket_id(ticket_id)

        return ticket

    def save_ticket(self, ticket: Ticket) -> None:
        """
        Guarda un ticket existente.

        Args:
            ticket: Objeto Ticket a guardar
        """
        if not ticket.file_path:
            raise ValueError("El ticket no tiene una ruta de archivo asociada")

        self.writer.write(ticket, ticket.file_path)

    def add_task_to_ticket(
        self,
        ticket_id: str,
        list_name: str,
        task_title: str,
        task_content: Optional[list[str]] = None
    ) -> Ticket:
        """
        Agrega una tarea a un ticket.

        Args:
            ticket_id: ID del ticket
            list_name: Nombre de la lista donde agregar la tarea
            task_title: Título de la nueva tarea
            task_content: Contenido adicional de la tarea

        Returns:
            Ticket actualizado
        """
        ticket = self.get_ticket_by_id(ticket_id)

        if not ticket:
            raise FileNotFoundError(f"Ticket {ticket_id} no encontrado")

        # Obtener o crear lista
        target_list = ticket.get_or_create_list(list_name)

        # Crear tarea
        task = Task(
            title=task_title,
            completed=False,
            content=task_content or [task_title]
        )

        target_list.add_task(task)

        # Guardar ticket
        self.save_ticket(ticket)

        return ticket

    def update_task(
        self,
        ticket_id: str,
        task_title: str,
        completed: Optional[bool] = None,
        new_content: Optional[list[str]] = None,
        move_to_list: Optional[str] = None
    ) -> Ticket:
        """
        Actualiza una tarea existente.

        Args:
            ticket_id: ID del ticket
            task_title: Título de la tarea a actualizar
            completed: Nuevo estado de completado (opcional)
            new_content: Nuevo contenido (opcional)
            move_to_list: Nombre de la lista a la que mover la tarea (opcional)

        Returns:
            Ticket actualizado
        """
        ticket = self.get_ticket_by_id(ticket_id)

        if not ticket:
            raise FileNotFoundError(f"Ticket {ticket_id} no encontrado")

        # Buscar tarea en todas las listas
        task = None
        source_list = None

        for lst in ticket.lists:
            task = lst.get_task_by_title(task_title)
            if task:
                source_list = lst
                break

        if not task:
            raise ValueError(f"Tarea '{task_title}' no encontrada")

        # Actualizar estado de completado
        if completed is not None:
            task.completed = completed

        # Actualizar contenido
        if new_content is not None:
            task.content = new_content
            task._parse_metadata()

        # Mover a otra lista
        if move_to_list and source_list:
            target_list = ticket.get_or_create_list(move_to_list)

            if target_list != source_list:
                source_list.remove_task(task)
                target_list.add_task(task)

        # Guardar ticket
        self.save_ticket(ticket)

        return ticket

    def delete_task(
        self,
        ticket_id: str,
        task_title: str
    ) -> Ticket:
        """
        Elimina una tarea.

        Args:
            ticket_id: ID del ticket
            task_title: Título de la tarea a eliminar

        Returns:
            Ticket actualizado
        """
        ticket = self.get_ticket_by_id(ticket_id)

        if not ticket:
            raise FileNotFoundError(f"Ticket {ticket_id} no encontrado")

        # Buscar y eliminar tarea
        for lst in ticket.lists:
            task = lst.get_task_by_title(task_title)
            if task:
                lst.remove_task(task)
                break

        # Guardar ticket
        self.save_ticket(ticket)

        return ticket

    def create_task_description(
        self,
        ticket_id: str,
        task_title: str,
        description: str
    ) -> Path:
        """
        Crea o actualiza el archivo de descripción de una tarea.

        Args:
            ticket_id: ID del ticket
            task_title: Título de la tarea
            description: Contenido de la descripción

        Returns:
            Path al archivo de descripción
        """
        ticket_file = self.file_utils.find_ticket_file(ticket_id)

        if not ticket_file:
            raise FileNotFoundError(f"Ticket {ticket_id} no encontrado")

        return self.writer.create_task_description(
            ticket_file,
            task_title,
            description
        )
