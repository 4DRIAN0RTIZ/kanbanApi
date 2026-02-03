#!/usr/bin/env python3
"""
Modelo de Task (tarea individual).
Equivalente a la estructura de task en kanban.nvim
"""
from typing import List as TypingList, Optional
from datetime import datetime, date
import re


class Task:
    """
    Representa una tarea individual en el kanban.

    Estructura similar a:
    {
        lines = {},         -- Array de strings (primera línea es título)
        check = false,      -- Boolean: completado o no
    }
    """

    def __init__(
        self,
        title: str,
        completed: bool = False,
        content: Optional[TypingList[str]] = None
    ):
        self.title = title
        self.completed = completed
        self.content = content or [title]  # Primera línea siempre es el título

        # Metadata extraída del contenido
        self._due_date: Optional[date] = None
        self._tags: TypingList[str] = []
        self._priority: Optional[str] = None
        self._parse_metadata()

    def _parse_metadata(self):
        """Parsea metadata del contenido (due dates, tags, prioridad)"""
        for line in self.content:
            # Due date (@YYYY-MM-DD)
            due_match = re.search(r'@(\d{4}-\d{2}-\d{2})', line)
            if due_match and not self._due_date:
                try:
                    self._due_date = datetime.strptime(
                        due_match.group(1), '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass

            # Tags (#tag)
            tags = re.findall(r'#(\w+)', line)
            self._tags.extend(tags)

            # Prioridad (!!! > !! > !)
            if '!!!' in line and not self._priority:
                self._priority = 'high'
            elif '!!' in line and not self._priority:
                self._priority = 'medium'
            elif '!' in line and not self._priority:
                self._priority = 'low'

        # Eliminar tags duplicados
        self._tags = list(set(self._tags))

    @property
    def due_date(self) -> Optional[str]:
        """Retorna due date como string ISO (YYYY-MM-DD) o None"""
        return self._due_date.isoformat() if self._due_date else None

    @property
    def tags(self) -> TypingList[str]:
        """Retorna lista de tags"""
        return self._tags

    @property
    def priority(self) -> Optional[str]:
        """Retorna prioridad (high, medium, low) o None"""
        return self._priority

    @property
    def days_until_due(self) -> Optional[int]:
        """Calcula días hasta la fecha de vencimiento"""
        if not self._due_date:
            return None
        delta = self._due_date - date.today()
        return delta.days

    @property
    def is_overdue(self) -> bool:
        """Verifica si la tarea está vencida"""
        days = self.days_until_due
        return days is not None and days < 0

    def to_dict(self) -> dict:
        """Serializa la tarea a diccionario"""
        return {
            'title': self.title,
            'completed': self.completed,
            'content': self.content,
            'due_date': self.due_date,
            'tags': self.tags,
            'priority': self.priority,
            'days_until_due': self.days_until_due,
            'is_overdue': self.is_overdue
        }

    def __repr__(self) -> str:
        status = 'x' if self.completed else ' '
        return f"Task([{status}] {self.title})"
