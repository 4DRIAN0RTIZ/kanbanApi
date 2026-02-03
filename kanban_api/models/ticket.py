#!/usr/bin/env python3
"""
Modelo de Ticket (board completo).
Equivalente a M.items en kanban.nvim
"""
from typing import List as TypingList, Optional
from pathlib import Path
from .list import List
from .task import Task


class Ticket:
    """
    Representa un ticket/board completo del kanban.

    Estructura similar a:
    M.items = {
        lists = {
            { title = "TODO", tasks = {...} },
            { title = "Doing", tasks = {...} },
            ...
        }
    }
    """

    def __init__(self, ticket_id: str, file_path: Optional[Path] = None):
        self.ticket_id = ticket_id
        self.file_path = file_path
        self.lists: TypingList[List] = []

    def add_list(self, list_obj: List):
        """Agrega una lista al ticket"""
        self.lists.append(list_obj)

    def get_list_by_title(self, title: str) -> Optional[List]:
        """Busca una lista por su título"""
        for list_obj in self.lists:
            if list_obj.title.lower() == title.lower():
                return list_obj
        return None

    def get_or_create_list(self, title: str) -> List:
        """Obtiene una lista existente o crea una nueva"""
        list_obj = self.get_list_by_title(title)
        if not list_obj:
            list_obj = List(title)
            self.add_list(list_obj)
        return list_obj

    @property
    def total_tasks(self) -> int:
        """Cuenta total de tareas en el ticket"""
        return sum(lst.total_count for lst in self.lists)

    @property
    def completed_tasks(self) -> int:
        """Cuenta tareas completadas en el ticket"""
        return sum(lst.completed_count for lst in self.lists)

    @property
    def pending_tasks(self) -> int:
        """Cuenta tareas pendientes en el ticket"""
        return sum(lst.pending_count for lst in self.lists)

    def get_all_tasks(self) -> TypingList[Task]:
        """Retorna todas las tareas del ticket"""
        all_tasks = []
        for lst in self.lists:
            all_tasks.extend(lst.tasks)
        return all_tasks

    def to_dict(self) -> dict:
        """Serializa el ticket a diccionario"""
        return {
            'ticket_id': self.ticket_id,
            'file': str(self.file_path) if self.file_path else None,
            'lists': [lst.to_dict() for lst in self.lists],
            'stats': {
                'total_tasks': self.total_tasks,
                'completed_tasks': self.completed_tasks,
                'pending_tasks': self.pending_tasks,
                'total_lists': len(self.lists)
            }
        }

    def __repr__(self) -> str:
        return f"Ticket({self.ticket_id}, {len(self.lists)} lists, {self.total_tasks} tasks)"
