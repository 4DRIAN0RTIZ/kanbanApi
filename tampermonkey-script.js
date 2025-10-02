// ==UserScript==
// @name         Kanban Ticket Viewer
// @namespace    http://tampermonkey.net/
// @version      2025-10-01
// @description  Muestra las notas del ticket actual desde la API Flask
// @author       You
// @match        https://neanderpruebas.com/erp-pruebas/op_requisicion_puntualidad.php
// @icon         https://www.google.com/s2/favicons?sz=64&domain=neanderpruebas.com
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'http://localhost:5000';

    // ============= CONFIGURACIÓN DE TEMA =============
    // Cambia entre: 'purple', 'blue', 'green', 'orange', 'pink', 'dark'
    const THEME = 'purple';

    const THEMES = {
        purple: {
            primary: '#667eea',
            secondary: '#764ba2',
            todo: '#FF9800',
            doing: '#2196F3',
            done: '#4CAF50',
            background: '#ffffff',
            surface: '#f8f9fa',
            text: '#212529',
            textSecondary: '#6c757d',
            border: '#e0e0e0'
        },
        blue: {
            primary: '#2196F3',
            secondary: '#1976D2',
            todo: '#FF9800',
            doing: '#00BCD4',
            done: '#4CAF50',
            background: '#ffffff',
            surface: '#e3f2fd',
            text: '#212529',
            textSecondary: '#546e7a',
            border: '#90caf9'
        },
        green: {
            primary: '#4CAF50',
            secondary: '#388E3C',
            todo: '#FFC107',
            doing: '#00BCD4',
            done: '#66BB6A',
            background: '#ffffff',
            surface: '#e8f5e9',
            text: '#212529',
            textSecondary: '#558b2f',
            border: '#a5d6a7'
        },
        orange: {
            primary: '#FF9800',
            secondary: '#F57C00',
            todo: '#FF5722',
            doing: '#03A9F4',
            done: '#8BC34A',
            background: '#ffffff',
            surface: '#fff3e0',
            text: '#212529',
            textSecondary: '#e65100',
            border: '#ffcc80'
        },
        pink: {
            primary: '#E91E63',
            secondary: '#C2185B',
            todo: '#FF9800',
            doing: '#9C27B0',
            done: '#4CAF50',
            background: '#ffffff',
            surface: '#fce4ec',
            text: '#212529',
            textSecondary: '#880e4f',
            border: '#f8bbd0'
        },
        dark: {
            primary: '#1e293b',
            secondary: '#334155',
            todo: '#f59e0b',
            doing: '#3b82f6',
            done: '#10b981',
            background: '#0f172a',
            surface: '#1e293b',
            text: '#f1f5f9',
            textSecondary: '#94a3b8',
            border: '#334155'
        }
    };

    const theme = THEMES[THEME];
    // =================================================

    // Estilos para el panel
    const styles = `
        #kanban-panel {
            position: fixed;
            top: 10px;
            right: 10px;
            width: 380px;
            max-height: 90vh;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        #kanban-header {
            background: #333;
            color: #fff;
            padding: 10px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
        }

        #kanban-title {
            font-weight: 500;
            font-size: 14px;
        }

        #kanban-close {
            cursor: pointer;
            font-size: 20px;
            background: none;
            border: none;
            color: #fff;
            padding: 0;
            width: 24px;
            height: 24px;
        }

        #kanban-close:hover {
            opacity: 0.7;
        }

        .ticket-info {
            background: #f5f5f5;
            padding: 8px 12px;
            border-bottom: 1px solid #ddd;
        }

        .ticket-id {
            font-size: 12px;
            font-weight: 500;
            color: #333;
        }

        .tabs-container {
            display: flex;
            background: #f9f9f9;
            border-bottom: 1px solid #ddd;
        }

        .tab-button {
            flex: 1;
            padding: 10px 8px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            color: #666;
            transition: color 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }

        .tab-button:hover {
            color: #333;
        }

        .tab-button.active {
            color: #000;
            background: #fff;
            border-bottom: 2px solid #333;
        }

        .tab-badge {
            background: #666;
            color: #fff;
            padding: 1px 6px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 600;
            min-width: 16px;
            text-align: center;
        }

        .tab-button.active .tab-badge {
            background: #333;
        }

        .tab-content {
            display: none;
            padding: 12px;
            overflow-y: auto;
            max-height: calc(90vh - 150px);
        }

        .tab-content.active {
            display: block;
        }

        .task-item {
            padding: 10px;
            margin-bottom: 8px;
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 3px;
        }

        .task-item.todo {
            border-left: 3px solid #ff9800;
        }

        .task-item.doing {
            border-left: 3px solid #2196f3;
            background: #f0f8ff;
        }

        .task-item.done {
            border-left: 3px solid #4caf50;
            opacity: 0.7;
        }

        .task-header {
            display: flex;
            gap: 6px;
        }

        .task-icon {
            font-size: 14px;
            flex-shrink: 0;
        }

        .task-content {
            flex: 1;
        }

        .task-name {
            font-size: 13px;
            color: #333;
            line-height: 1.4;
        }

        .task-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 6px;
        }

        .task-tag {
            display: inline-flex;
            align-items: center;
            padding: 2px 6px;
            border-radius: 2px;
            font-size: 10px;
            font-weight: 500;
            gap: 2px;
        }

        .task-tag.priority-high {
            background: #fee2e2;
            color: #dc2626;
        }

        .task-tag.priority-medium {
            background: #fef3c7;
            color: #d97706;
        }

        .task-tag.priority-low {
            background: #dbeafe;
            color: #2563eb;
        }

        .task-tag.label {
            background: #e0e0e0;
            color: #555;
        }

        .task-tag.date {
            background: #f5f5f5;
            color: #666;
            border: 1px solid #ddd;
        }

        .task-tag.date.urgent {
            background: #fee2e2;
            color: #dc2626;
            border-color: #dc2626;
        }

        .task-tag.date.soon {
            background: #fef3c7;
            color: #d97706;
            border-color: #d97706;
        }

        .task-metadata {
            font-size: 11px;
            color: #666;
            margin-top: 8px;
            padding: 8px;
            background: #f9f9f9;
            border-radius: 2px;
            white-space: pre-wrap;
            line-height: 1.4;
            border-left: 2px solid #ddd;
        }

        .empty-state {
            text-align: center;
            padding: 30px 16px;
            color: #999;
        }

        .empty-state-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .empty-state-text {
            font-size: 12px;
        }

        .loading {
            text-align: center;
            padding: 30px 16px;
            color: #999;
            font-size: 12px;
        }

        .error {
            color: #dc3545;
            padding: 10px;
            background: #f8d7da;
            border-radius: 3px;
            border-left: 3px solid #dc3545;
            font-size: 11px;
            line-height: 1.4;
        }

        .toggle-btn {
            position: fixed;
            top: 10px;
            right: 10px;
            background: #333;
            color: #fff;
            border: none;
            padding: 8px 12px;
            border-radius: 3px;
            cursor: pointer;
            z-index: 9998;
            font-size: 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }

        .toggle-btn:hover {
            background: #444;
        }

        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: #f5f5f5;
        }

        ::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #999;
        }
    `;

    // Inyectar estilos
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // Crear botón de toggle
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'toggle-btn';
    toggleBtn.textContent = '📋';
    toggleBtn.title = 'Ver notas del ticket';
    document.body.appendChild(toggleBtn);

    // Crear panel
    const panel = document.createElement('div');
    panel.id = 'kanban-panel';
    panel.style.display = 'none';
    panel.innerHTML = `
        <div id="kanban-header">
            <span id="kanban-title">📋 Kanban Board</span>
            <button id="kanban-close">×</button>
        </div>
        <div class="ticket-info">
            <div class="ticket-id" id="ticket-display">Cargando...</div>
        </div>
        <div class="tabs-container">
            <button class="tab-button active" data-tab="todo">
                📝 Por Hacer
                <span class="tab-badge" id="badge-todo">0</span>
            </button>
            <button class="tab-button" data-tab="doing">
                🔄 Haciendo
                <span class="tab-badge" id="badge-doing">0</span>
            </button>
            <button class="tab-button" data-tab="done">
                ✅ Completadas
                <span class="tab-badge" id="badge-done">0</span>
            </button>
        </div>
        <div id="tab-todo" class="tab-content active">
            <div class="loading">Cargando...</div>
        </div>
        <div id="tab-doing" class="tab-content">
            <div class="loading">Cargando...</div>
        </div>
        <div id="tab-done" class="tab-content">
            <div class="loading">Cargando...</div>
        </div>
    `;
    document.body.appendChild(panel);

    // Funcionalidad de tabs
    const tabButtons = panel.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');

            // Remover active de todos los botones y contenidos
            tabButtons.forEach(btn => btn.classList.remove('active'));
            panel.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Agregar active al botón y contenido seleccionado
            button.classList.add('active');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        });
    });

    // Funcionalidad de arrastrar
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    const header = document.getElementById('kanban-header');

    header.addEventListener('mousedown', (e) => {
        isDragging = true;
        initialX = e.clientX - panel.offsetLeft;
        initialY = e.clientY - panel.offsetTop;
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            panel.style.left = currentX + 'px';
            panel.style.top = currentY + 'px';
            panel.style.right = 'auto';
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    // Toggle panel
    toggleBtn.addEventListener('click', () => {
        if (panel.style.display === 'none') {
            panel.style.display = 'flex';
            loadTicketData();
        } else {
            panel.style.display = 'none';
        }
    });

    document.getElementById('kanban-close').addEventListener('click', () => {
        panel.style.display = 'none';
    });

    // Parsear etiquetas y fechas
    function parseTaskContent(taskName) {
        let cleanName = taskName;
        const tags = [];

        // Parsear prioridades: !!! (alta), !! (media), ! (baja)
        const priorityMatch = taskName.match(/(!{1,3})/g);
        if (priorityMatch) {
            const level = priorityMatch[0].length;
            const priority = level === 3 ? 'high' : level === 2 ? 'medium' : 'low';
            const priorityLabel = level === 3 ? 'Alta' : level === 2 ? 'Media' : 'Baja';
            tags.push({ type: 'priority', level: priority, text: priorityLabel });
            cleanName = cleanName.replace(/!+/g, '').trim();
        }

        // Parsear etiquetas: #etiqueta
        const labelMatches = taskName.matchAll(/#(\w+)/g);
        for (const match of labelMatches) {
            tags.push({ type: 'label', text: match[1] });
            cleanName = cleanName.replace(match[0], '').trim();
        }

        // Parsear menciones: @persona
        const mentionMatches = taskName.matchAll(/@(\w+)/g);
        for (const match of mentionMatches) {
            tags.push({ type: 'label', text: '@' + match[1] });
            cleanName = cleanName.replace(match[0], '').trim();
        }

        // Parsear fechas: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
        const datePatterns = [
            /\d{4}-\d{2}-\d{2}/,
            /\d{2}\/\d{2}\/\d{4}/,
            /\d{2}-\d{2}-\d{4}/
        ];

        for (const pattern of datePatterns) {
            const dateMatch = taskName.match(pattern);
            if (dateMatch) {
                const dateStr = dateMatch[0];
                const taskDate = parseDate(dateStr);
                const today = new Date();
                today.setHours(0, 0, 0, 0);

                const diffTime = taskDate - today;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

                let urgency = null;
                if (diffDays < 0) {
                    urgency = 'urgent';
                } else if (diffDays <= 3) {
                    urgency = 'soon';
                }

                tags.push({
                    type: 'date',
                    text: dateStr,
                    urgency: urgency,
                    daysUntil: diffDays
                });
                cleanName = cleanName.replace(dateStr, '').trim();
                break;
            }
        }

        return { cleanName, tags };
    }

    function parseDate(dateStr) {
        // Detectar formato y convertir a objeto Date
        if (/\d{4}-\d{2}-\d{2}/.test(dateStr)) {
            return new Date(dateStr);
        } else if (/\d{2}\/\d{2}\/\d{4}/.test(dateStr)) {
            const [day, month, year] = dateStr.split('/');
            return new Date(year, month - 1, day);
        } else if (/\d{2}-\d{2}-\d{4}/.test(dateStr)) {
            const [day, month, year] = dateStr.split('-');
            return new Date(year, month - 1, day);
        }
        return new Date();
    }

    function renderTags(tags) {
        if (!tags || tags.length === 0) return '';

        let html = '<div class="task-tags">';

        tags.forEach(tag => {
            if (tag.type === 'priority') {
                html += `<span class="task-tag priority-${tag.level}">🔥 ${tag.text}</span>`;
            } else if (tag.type === 'label') {
                html += `<span class="task-tag label">#${tag.text}</span>`;
            } else if (tag.type === 'date') {
                const urgencyClass = tag.urgency || '';
                const icon = tag.urgency === 'urgent' ? '⚠️' : tag.urgency === 'soon' ? '⏰' : '📅';
                const suffix = tag.daysUntil === 0 ? ' (hoy)' :
                              tag.daysUntil === 1 ? ' (mañana)' :
                              tag.daysUntil < 0 ? ` (${Math.abs(tag.daysUntil)}d vencido)` :
                              tag.daysUntil <= 7 ? ` (${tag.daysUntil}d)` : '';
                html += `<span class="task-tag date ${urgencyClass}">${icon} ${tag.text}${suffix}</span>`;
            }
        });

        html += '</div>';
        return html;
    }

    // Cargar datos del ticket
    async function loadTicketData() {
        const todoTab = document.getElementById('tab-todo');
        const doingTab = document.getElementById('tab-doing');
        const doneTab = document.getElementById('tab-done');

        todoTab.innerHTML = '<div class="loading">Cargando...</div>';
        doingTab.innerHTML = '<div class="loading">Cargando...</div>';
        doneTab.innerHTML = '<div class="loading">Cargando...</div>';

        try {
            const response = await fetch(`${API_URL}/current-ticket`);

            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }

            const data = await response.json();
            displayTicketData(data);
        } catch (error) {
            const errorHTML = `<div class="error">⚠️ Error al cargar datos: ${error.message}<br><br>Asegúrate de que la API Flask esté corriendo en ${API_URL}</div>`;
            todoTab.innerHTML = errorHTML;
            doingTab.innerHTML = errorHTML;
            doneTab.innerHTML = errorHTML;
        }
    }

    function displayTicketData(data) {
        // Actualizar título del ticket
        document.getElementById('ticket-display').textContent = `Ticket: ${data.ticket_id}`;

        // Separar tareas por estado
        const todoTasks = data.tasks.filter(t => !t.done && !t.in_progress);
        const doingTasks = data.tasks.filter(t => !t.done && t.in_progress);
        const doneTasks = data.tasks.filter(t => t.done);

        // Actualizar badges
        document.getElementById('badge-todo').textContent = todoTasks.length;
        document.getElementById('badge-doing').textContent = doingTasks.length;
        document.getElementById('badge-done').textContent = doneTasks.length;

        // Renderizar cada tab
        renderTab('tab-todo', todoTasks, 'todo', '📝', 'No hay tareas pendientes');
        renderTab('tab-doing', doingTasks, 'doing', '🔄', 'No hay tareas en progreso');
        renderTab('tab-done', doneTasks, 'done', '✅', 'No hay tareas completadas');
    }

    function renderTab(tabId, tasks, className, icon, emptyMessage) {
        const tab = document.getElementById(tabId);

        if (tasks.length === 0) {
            tab.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">${icon}</div>
                    <div class="empty-state-text">${emptyMessage}</div>
                </div>
            `;
            return;
        }

        let html = '';
        tasks.forEach(task => {
            const { cleanName, tags } = parseTaskContent(task.name);

            html += `
                <div class="task-item ${className}">
                    <div class="task-header">
                        <span class="task-icon">${icon}</span>
                        <div class="task-content">
                            <div class="task-name">${cleanName}</div>
                            ${renderTags(tags)}
                        </div>
                    </div>
                    ${task.metadata ? `<div class="task-metadata">${task.metadata}</div>` : ''}
                </div>
            `;
        });

        tab.innerHTML = html;
    }

    // Auto-cargar al inicio
    setTimeout(() => {
        loadTicketData();
    }, 1000);

    console.log('Kanban Ticket Viewer cargado');
})();
