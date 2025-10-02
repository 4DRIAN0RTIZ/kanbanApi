#!/usr/bin/env python3
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from app import (
    app,
    get_current_ticket,
    find_ticket_file,
    parse_ticket_tasks,
    get_task_metadata,
    KANBAN_DIR,
    LAST_TICKET_FILE
)


@pytest.fixture
def client():
    """Fixture de cliente de prueba de Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHelperFunctions:
    """Tests para funciones auxiliares"""

    def test_get_current_ticket_exists(self):
        """Test cuando existe un ticket actual"""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value='T-12345\n'):
                result = get_current_ticket()
                assert result == 'T-12345'

    def test_get_current_ticket_not_exists(self):
        """Test cuando no existe ticket actual"""
        with patch.object(Path, 'exists', return_value=False):
            result = get_current_ticket()
            assert result is None

    def test_find_ticket_file_direct_match(self):
        """Test cuando se encuentra el archivo directamente"""
        with patch.object(Path, 'exists', return_value=True):
            result = find_ticket_file('12345')
            assert result is not None
            assert '12345.md' in str(result)

    def test_find_ticket_file_with_prefix(self):
        """Test cuando el archivo tiene prefijo T-"""
        # El primer candidato (12345.md) no existe, pero el segundo (T-12345.md) sí
        with patch.object(Path, 'exists', side_effect=[False, True]):
            result = find_ticket_file('12345')
            assert result is not None
            assert 'T-12345.md' in str(result)

    def test_find_ticket_file_not_found(self):
        """Test cuando no se encuentra el archivo"""
        with patch.object(Path, 'exists', return_value=False):
            with patch.object(Path, 'glob', return_value=[]):
                result = find_ticket_file('99999')
                assert result is None

    def test_parse_ticket_tasks_with_tasks(self):
        """Test parseo de tareas"""
        content = """
# Ticket T-12345

- [ ] Tarea pendiente
- [x] Tarea completada
- [ ] Otra tarea
"""
        mock_file = MagicMock()
        mock_file.read_text.return_value = content

        with patch('app.get_task_metadata', return_value=None):
            tasks = parse_ticket_tasks(mock_file)

            assert len(tasks) == 3
            assert tasks[0]['name'] == 'Tarea pendiente'
            assert tasks[0]['done'] is False
            assert tasks[1]['name'] == 'Tarea completada'
            assert tasks[1]['done'] is True
            assert tasks[2]['name'] == 'Otra tarea'
            assert tasks[2]['done'] is False

    def test_parse_ticket_tasks_empty(self):
        """Test parseo de ticket sin tareas"""
        content = "# Ticket sin tareas\n\nContenido sin checkboxes."
        mock_file = MagicMock()
        mock_file.read_text.return_value = content

        tasks = parse_ticket_tasks(mock_file)
        assert len(tasks) == 0

    def test_get_task_metadata_exists(self):
        """Test cuando existe metadata de tarea"""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value='Metadata de prueba'):
                result = get_task_metadata('test task')
                assert result == 'Metadata de prueba'

    def test_get_task_metadata_not_exists(self):
        """Test cuando no existe metadata de tarea"""
        with patch.object(Path, 'exists', return_value=False):
            result = get_task_metadata('nonexistent')
            assert result is None


class TestEndpoints:
    """Tests para endpoints de la API"""

    def test_current_ticket_success(self, client):
        """Test endpoint /current-ticket exitoso"""
        content = "- [ ] Tarea 1\n- [x] Tarea 2"

        with patch('app.get_current_ticket', return_value='T-12345'):
            with patch('app.find_ticket_file') as mock_find:
                mock_file = MagicMock()
                mock_file.read_text.return_value = content
                mock_find.return_value = mock_file

                with patch('app.get_task_metadata', return_value=None):
                    response = client.get('/current-ticket')

                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['ticket_id'] == 'T-12345'
                    assert 'tasks' in data
                    assert len(data['tasks']) == 2

    def test_current_ticket_no_ticket(self, client):
        """Test cuando no hay ticket actual"""
        with patch('app.get_current_ticket', return_value=None):
            response = client.get('/current-ticket')

            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data

    def test_current_ticket_file_not_found(self, client):
        """Test cuando el archivo del ticket no existe"""
        with patch('app.get_current_ticket', return_value='T-99999'):
            with patch('app.find_ticket_file', return_value=None):
                response = client.get('/current-ticket')

                assert response.status_code == 404
                data = response.get_json()
                assert 'error' in data

    def test_get_ticket_success(self, client):
        """Test endpoint /ticket/<id> exitoso"""
        content = "- [ ] Tarea A"

        with patch('app.find_ticket_file') as mock_find:
            mock_file = MagicMock()
            mock_file.read_text.return_value = content
            mock_find.return_value = mock_file

            with patch('app.get_task_metadata', return_value=None):
                response = client.get('/ticket/12345')

                assert response.status_code == 200
                data = response.get_json()
                assert data['ticket_id'] == '12345'
                assert len(data['tasks']) == 1

    def test_get_ticket_not_found(self, client):
        """Test cuando el ticket no existe"""
        with patch('app.find_ticket_file', return_value=None):
            response = client.get('/ticket/99999')

            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data

    def test_get_task_success(self, client):
        """Test endpoint /task/<name> exitoso"""
        with patch('app.get_task_metadata', return_value='Metadata de prueba'):
            response = client.get('/task/test_task')

            assert response.status_code == 200
            data = response.get_json()
            assert data['task_name'] == 'test_task'
            assert data['metadata'] == 'Metadata de prueba'

    def test_get_task_not_found(self, client):
        """Test cuando la tarea no tiene metadata"""
        with patch('app.get_task_metadata', return_value=None):
            response = client.get('/task/nonexistent')

            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data

    def test_list_tickets_success(self, client):
        """Test endpoint /tickets exitoso"""
        mock_files = [
            MagicMock(stem='T-12345', __str__=lambda self: '/path/T-12345.md'),
            MagicMock(stem='T-67890', __str__=lambda self: '/path/T-67890.md'),
            MagicMock(stem='tasksTest', __str__=lambda self: '/path/tasksTest.md')
        ]

        with patch.object(Path, 'glob', return_value=mock_files):
            response = client.get('/tickets')

            assert response.status_code == 200
            data = response.get_json()
            assert 'tickets' in data
            # Solo debe incluir T-12345 y T-67890, no tasksTest
            assert len(data['tickets']) == 2
            assert any(t['id'] == 'T-12345' for t in data['tickets'])
            assert any(t['id'] == 'T-67890' for t in data['tickets'])

    def test_list_tickets_empty(self, client):
        """Test cuando no hay tickets"""
        with patch.object(Path, 'glob', return_value=[]):
            response = client.get('/tickets')

            assert response.status_code == 200
            data = response.get_json()
            assert data['tickets'] == []


class TestIntegration:
    """Tests de integración más complejos"""

    def test_ticket_with_metadata(self, client):
        """Test ticket completo con tareas que tienen metadata"""
        content = "- [ ] Implementar feature\n- [x] Revisar código"

        def mock_metadata(task_name):
            if 'Implementar' in task_name:
                return '## Detalles\nMetadata detallada'
            return None

        with patch('app.find_ticket_file') as mock_find:
            mock_file = MagicMock()
            mock_file.read_text.return_value = content
            mock_find.return_value = mock_file

            with patch('app.get_task_metadata', side_effect=mock_metadata):
                response = client.get('/ticket/TEST-1')

                assert response.status_code == 200
                data = response.get_json()
                assert len(data['tasks']) == 2
                assert data['tasks'][0]['metadata'] is not None
                assert data['tasks'][1]['metadata'] is None

    def test_cors_headers(self, client):
        """Test que CORS está habilitado"""
        response = client.get('/tickets')
        assert 'Access-Control-Allow-Origin' in response.headers
