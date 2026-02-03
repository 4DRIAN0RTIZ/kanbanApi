#!/usr/bin/env python3
"""
Modelo de List (columna de tareas).
Equivalente a la estructura de list en kanban.nvim
"""
from typing import List as TypingList
from .task import Task


class List:
    """
    Representa una columna/lista en el kanban.

    Estructura similar a:
    {
        title = "TODO",
        tasks = { ... }
    }
    """

    def __init__(self, title: str):
        self.title = title
        self.tasks: TypingList[Task] = []

    def add_task(self, task: Task):
        """Agrega una tarea a la lista"""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> bool:
        """Elimina una tarea de la lista"""
        try:
            self.tasks.remove(task)
            return True
        except ValueError:
            return False

    def get_task_by_title(self, title: str) -> Task | None:
        """Busca una tarea por su título"""
        for task in self.tasks:
            if task.title == title:
                return task
        return None

    @property
    def completed_count(self) -> int:
        """Cuenta tareas completadas"""
        return sum(1 for task in self.tasks if task.completed)

    @property
    def pending_count(self) -> int:
        """Cuenta tareas pendientes"""
        return sum(1 for task in self.tasks if not task.completed)

    @property
    def total_count(self) -> int:
        """Cuenta total de tareas"""
        return len(self.tasks)

    def to_dict(self) -> dict:
        """Serializa la lista a diccionario"""
        return {
            'title': self.title,
            'tasks': [task.to_dict() for task in self.tasks],
            'stats': {
                'total': self.total_count,
                'completed': self.completed_count,
                'pending': self.pending_count
            }
        }

    def __repr__(self) -> str:
        return f"List({self.title}, {self.total_count} tasks)"
