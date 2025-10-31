// ==UserScript==
// @name         Kanban Ticket Viewer v2.1
// @namespace    http://tampermonkey.net/
// @version      2.1.0
// @description  Vista minimalista con modal y temas - Compatible con API v0.1
// @author       Neandertech
// @match        *://*/*
// @icon         📋
// @grant        GM_setValue
// @grant        GM_getValue
// ==/UserScript==

(function() {
    'use strict';

    const CONFIG = {
        apiUrl: 'http://localhost:5000',
        autoRefresh: 30000,
        position: 'top-right',
    };

    let currentTheme = GM_getValue('kbTheme', 'cyberpunk');

    const THEMES = {
        cyberpunk: {
            name: '🌃 Cyberpunk',
            bg: '#0a0e27',
            bgSecondary: '#1a1f3a',
            bgTertiary: '#252b4a',
            text: '#e0e7ff',
            textMuted: '#94a3b8',
            border: '#334155',
            shadow: '0 8px 16px rgba(139, 92, 246, 0.3)',
            todo: '#fbbf24',
            doing: '#8b5cf6',
            done: '#10b981',
            accent: '#a78bfa',
            accentGlow: 'rgba(167, 139, 250, 0.4)',
        },
        ocean: {
            name: '🌊 Ocean',
            bg: '#0f172a',
            bgSecondary: '#1e293b',
            bgTertiary: '#334155',
            text: '#f1f5f9',
            textMuted: '#94a3b8',
            border: '#475569',
            shadow: '0 8px 16px rgba(14, 165, 233, 0.3)',
            todo: '#fb923c',
            doing: '#0ea5e9',
            done: '#22c55e',
            accent: '#38bdf8',
            accentGlow: 'rgba(56, 189, 248, 0.4)',
        },
        sunset: {
            name: '🌅 Sunset',
            bg: '#1c1917',
            bgSecondary: '#292524',
            bgTertiary: '#44403c',
            text: '#fef3c7',
            textMuted: '#d6d3d1',
            border: '#57534e',
            shadow: '0 8px 16px rgba(251, 146, 60, 0.3)',
            todo: '#fbbf24',
            doing: '#fb923c',
            done: '#22c55e',
            accent: '#f59e0b',
            accentGlow: 'rgba(245, 158, 11, 0.4)',
        },
        forest: {
            name: '🌲 Forest',
            bg: '#14532d',
            bgSecondary: '#166534',
            bgTertiary: '#15803d',
            text: '#f0fdf4',
            textMuted: '#bbf7d0',
            border: '#22c55e',
            shadow: '0 8px 16px rgba(34, 197, 94, 0.3)',
            todo: '#fbbf24',
            doing: '#3b82f6',
            done: '#86efac',
            accent: '#4ade80',
            accentGlow: 'rgba(74, 222, 128, 0.4)',
        },
        rose: {
            name: '🌹 Rose',
            bg: '#1f1024',
            bgSecondary: '#2d1537',
            bgTertiary: '#3d1f47',
            text: '#fce7f3',
            textMuted: '#f9a8d4',
            border: '#ec4899',
            shadow: '0 8px 16px rgba(236, 72, 153, 0.3)',
            todo: '#fbbf24',
            doing: '#a855f7',
            done: '#10b981',
            accent: '#f472b6',
            accentGlow: 'rgba(244, 114, 182, 0.4)',
        },
        light: {
            name: '☀️ Light',
            bg: '#ffffff',
            bgSecondary: '#f8fafc',
            bgTertiary: '#f1f5f9',
            text: '#0f172a',
            textMuted: '#64748b',
            border: '#e2e8f0',
            shadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            todo: '#f59e0b',
            doing: '#3b82f6',
            done: '#10b981',
            accent: '#6366f1',
            accentGlow: 'rgba(99, 102, 241, 0.2)',
        }
    };

    const theme = THEMES[currentTheme];

    const styles = `
        #kb-widget {
            --kb-bg: ${theme.bg};
            --kb-bg-secondary: ${theme.bgSecondary};
            --kb-bg-tertiary: ${theme.bgTertiary};
            --kb-text: ${theme.text};
            --kb-text-muted: ${theme.textMuted};
            --kb-border: ${theme.border};
            --kb-shadow: ${theme.shadow};
            --kb-todo: ${theme.todo};
            --kb-doing: ${theme.doing};
            --kb-done: ${theme.done};
            --kb-accent: ${theme.accent};
            --kb-accent-glow: ${theme.accentGlow};
        }

        .kb-toggle {
            position: fixed;
            ${CONFIG.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
            ${CONFIG.position.includes('top') ? 'top: 20px;' : 'bottom: 20px;'}
            width: 52px;
            height: 52px;
            background: var(--kb-accent);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            z-index: 999998;
            box-shadow: var(--kb-shadow);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .kb-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 0 20px var(--kb-accent-glow);
        }

        .kb-toggle:active {
            transform: scale(0.95);
        }

        .kb-panel {
            position: fixed;
            ${CONFIG.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
            ${CONFIG.position.includes('top') ? 'top: 20px;' : 'bottom: 20px;'}
            width: 420px;
            max-height: 85vh;
            background: var(--kb-bg);
            border: 1px solid var(--kb-border);
            border-radius: 16px;
            box-shadow: var(--kb-shadow);
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: none;
            flex-direction: column;
            overflow: hidden;
        }

        .kb-panel.visible {
            display: flex;
            animation: kb-slide-in 0.3s ease-out;
        }

        @keyframes kb-slide-in {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .kb-header {
            padding: 16px;
            background: var(--kb-bg-secondary);
            border-bottom: 1px solid var(--kb-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: move;
            user-select: none;
        }

        .kb-header-title {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .kb-header-title-main {
            font-weight: 600;
            font-size: 14px;
            color: var(--kb-text);
        }

        .kb-ticket-id {
            font-size: 11px;
            color: var(--kb-text-muted);
        }

        .kb-header-actions {
            display: flex;
            gap: 8px;
        }

        .kb-btn {
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 6px 10px;
            border-radius: 8px;
            color: var(--kb-text-muted);
            transition: all 0.2s;
            font-size: 16px;
        }

        .kb-btn:hover {
            background: var(--kb-bg-tertiary);
            color: var(--kb-text);
        }

        .kb-stats {
            padding: 12px 16px;
            display: flex;
            gap: 12px;
            border-bottom: 1px solid var(--kb-border);
        }

        .kb-stat {
            flex: 1;
            text-align: center;
        }

        .kb-stat-value {
            font-size: 20px;
            font-weight: 700;
            color: var(--kb-text);
        }

        .kb-stat-label {
            font-size: 10px;
            color: var(--kb-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 2px;
        }

        .kb-stat.todo .kb-stat-value { color: var(--kb-todo); }
        .kb-stat.doing .kb-stat-value { color: var(--kb-doing); }
        .kb-stat.done .kb-stat-value { color: var(--kb-done); }

        .kb-tabs {
            display: flex;
            padding: 8px 16px;
            gap: 6px;
            border-bottom: 1px solid var(--kb-border);
            overflow-x: auto;
        }

        .kb-tab {
            padding: 8px 16px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            color: var(--kb-text-muted);
            border-radius: 8px;
            transition: all 0.2s;
            white-space: nowrap;
        }

        .kb-tab:hover {
            background: var(--kb-bg-tertiary);
            color: var(--kb-text);
        }

        .kb-tab.active {
            background: var(--kb-accent);
            color: white;
        }

        .kb-content {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
        }

        .kb-content::-webkit-scrollbar {
            width: 6px;
        }

        .kb-content::-webkit-scrollbar-track {
            background: transparent;
        }

        .kb-content::-webkit-scrollbar-thumb {
            background: var(--kb-border);
            border-radius: 3px;
        }

        .kb-task {
            padding: 12px;
            margin-bottom: 8px;
            background: var(--kb-bg-secondary);
            border-left: 3px solid var(--kb-border);
            border-radius: 8px;
            transition: all 0.2s;
            cursor: pointer;
        }

        .kb-task:hover {
            background: var(--kb-bg-tertiary);
            transform: translateX(2px);
        }

        .kb-task.todo { border-left-color: var(--kb-todo); }
        .kb-task.doing { border-left-color: var(--kb-doing); }
        .kb-task.done {
            border-left-color: var(--kb-done);
            opacity: 0.7;
        }

        .kb-task-title {
            font-size: 13px;
            font-weight: 500;
            color: var(--kb-text);
            line-height: 1.5;
        }

        .kb-task-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }

        .kb-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 600;
        }

        .kb-badge.priority-high {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
        }

        .kb-badge.priority-medium {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
        }

        .kb-badge.priority-low {
            background: rgba(59, 130, 246, 0.15);
            color: #3b82f6;
        }

        .kb-badge.tag {
            background: rgba(99, 102, 241, 0.15);
            color: var(--kb-accent);
        }

        .kb-badge.date {
            background: rgba(107, 114, 128, 0.15);
            color: var(--kb-text-muted);
        }

        .kb-badge.date.overdue {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
        }

        .kb-badge.date.soon {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
        }

        /* Modal */
        .kb-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
            z-index: 1000000;
            display: none;
            align-items: center;
            justify-content: center;
            animation: kb-fade-in 0.2s ease-out;
        }

        .kb-modal-overlay.visible {
            display: flex;
        }

        @keyframes kb-fade-in {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .kb-modal {
            background: var(--kb-bg);
            border: 1px solid var(--kb-border);
            border-radius: 16px;
            width: 90%;
            max-width: 700px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            animation: kb-modal-in 0.3s ease-out;
        }

        @keyframes kb-modal-in {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .kb-modal-header {
            padding: 20px;
            border-bottom: 1px solid var(--kb-border);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        .kb-modal-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--kb-text);
            line-height: 1.4;
            flex: 1;
        }

        .kb-modal-close {
            background: var(--kb-bg-tertiary);
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            cursor: pointer;
            color: var(--kb-text-muted);
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            margin-left: 16px;
        }

        .kb-modal-close:hover {
            background: var(--kb-accent);
            color: white;
        }

        .kb-modal-content {
            padding: 20px;
            overflow-y: auto;
            flex: 1;
        }

        .kb-modal-content::-webkit-scrollbar {
            width: 8px;
        }

        .kb-modal-content::-webkit-scrollbar-track {
            background: var(--kb-bg-secondary);
        }

        .kb-modal-content::-webkit-scrollbar-thumb {
            background: var(--kb-border);
            border-radius: 4px;
        }

        .kb-modal-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--kb-border);
        }

        .kb-modal-markdown {
            color: var(--kb-text);
            line-height: 1.8;
            font-size: 14px;
        }

        .kb-modal-markdown h1,
        .kb-modal-markdown h2,
        .kb-modal-markdown h3 {
            color: var(--kb-text);
            margin-top: 24px;
            margin-bottom: 12px;
        }

        .kb-modal-markdown h1 { font-size: 24px; border-bottom: 2px solid var(--kb-border); padding-bottom: 8px; }
        .kb-modal-markdown h2 { font-size: 20px; }
        .kb-modal-markdown h3 { font-size: 16px; }

        .kb-modal-markdown p {
            margin: 12px 0;
        }

        .kb-modal-markdown code {
            background: var(--kb-bg-secondary);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: var(--kb-accent);
        }

        .kb-modal-markdown pre {
            background: var(--kb-bg-secondary);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 16px 0;
        }

        .kb-modal-markdown pre code {
            background: none;
            padding: 0;
            color: var(--kb-text);
        }

        .kb-modal-markdown ul, .kb-modal-markdown ol {
            margin: 12px 0;
            padding-left: 24px;
        }

        .kb-modal-markdown li {
            margin: 6px 0;
        }

        .kb-modal-markdown blockquote {
            border-left: 3px solid var(--kb-accent);
            padding-left: 16px;
            margin: 16px 0;
            color: var(--kb-text-muted);
        }

        .kb-modal-markdown a {
            color: var(--kb-accent);
            text-decoration: none;
        }

        .kb-modal-markdown a:hover {
            text-decoration: underline;
        }

        /* Theme Selector */
        .kb-theme-selector {
            padding: 12px 16px;
            border-bottom: 1px solid var(--kb-border);
            display: flex;
            gap: 6px;
            overflow-x: auto;
        }

        .kb-theme-btn {
            padding: 6px 12px;
            background: var(--kb-bg-secondary);
            border: 1px solid var(--kb-border);
            border-radius: 8px;
            cursor: pointer;
            font-size: 11px;
            color: var(--kb-text-muted);
            transition: all 0.2s;
            white-space: nowrap;
        }

        .kb-theme-btn:hover {
            background: var(--kb-bg-tertiary);
            color: var(--kb-text);
        }

        .kb-theme-btn.active {
            background: var(--kb-accent);
            color: white;
            border-color: var(--kb-accent);
        }

        .kb-empty {
            text-align: center;
            padding: 40px 20px;
            color: var(--kb-text-muted);
        }

        .kb-empty-icon {
            font-size: 48px;
            margin-bottom: 12px;
            opacity: 0.5;
        }

        .kb-empty-text {
            font-size: 13px;
        }

        .kb-loading {
            text-align: center;
            padding: 40px;
            color: var(--kb-text-muted);
        }

        .kb-error {
            margin: 12px;
            padding: 12px;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 8px;
            color: #ef4444;
            font-size: 12px;
            line-height: 1.5;
        }

        .kb-error-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
    `;

    const styleEl = document.createElement('style');
    styleEl.id = 'kb-styles';
    styleEl.textContent = styles;
    document.head.appendChild(styleEl);

    const html = `
        <div id="kb-widget">
            <button class="kb-toggle" id="kb-toggle" title="Kanban Viewer">📋</button>
            <div class="kb-panel" id="kb-panel">
                <div class="kb-header" id="kb-header">
                    <div class="kb-header-title">
                        <div class="kb-header-title-main">📋 Kanban Board</div>
                        <div class="kb-ticket-id" id="kb-ticket-id">-</div>
                    </div>
                    <div class="kb-header-actions">
                        <button class="kb-btn" id="kb-refresh" title="Actualizar">🔄</button>
                        <button class="kb-btn" id="kb-close" title="Cerrar">✕</button>
                    </div>
                </div>
                <div class="kb-theme-selector" id="kb-theme-selector"></div>
                <div class="kb-stats">
                    <div class="kb-stat todo">
                        <div class="kb-stat-value" id="kb-stat-todo">0</div>
                        <div class="kb-stat-label">Por hacer</div>
                    </div>
                    <div class="kb-stat doing">
                        <div class="kb-stat-value" id="kb-stat-doing">0</div>
                        <div class="kb-stat-label">Haciendo</div>
                    </div>
                    <div class="kb-stat done">
                        <div class="kb-stat-value" id="kb-stat-done">0</div>
                        <div class="kb-stat-label">Completadas</div>
                    </div>
                </div>
                <div class="kb-tabs">
                    <button class="kb-tab active" data-tab="all">Todas</button>
                    <button class="kb-tab" data-tab="todo">Por hacer</button>
                    <button class="kb-tab" data-tab="doing">Haciendo</button>
                    <button class="kb-tab" data-tab="done">Completadas</button>
                </div>
                <div class="kb-content" id="kb-content">
                    <div class="kb-loading">Cargando...</div>
                </div>
            </div>
            <div class="kb-modal-overlay" id="kb-modal-overlay">
                <div class="kb-modal">
                    <div class="kb-modal-header">
                        <div class="kb-modal-title" id="kb-modal-title"></div>
                        <button class="kb-modal-close" id="kb-modal-close">✕</button>
                    </div>
                    <div class="kb-modal-content" id="kb-modal-content"></div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', html);

    let currentData = null;
    let currentTab = 'all';
    let currentTicketId = null;
    let dragState = { isDragging: false, startX: 0, startY: 0 };

    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    function renderThemeSelector() {
        const container = $('#kb-theme-selector');
        container.innerHTML = Object.keys(THEMES).map(key =>
            `<button class="kb-theme-btn ${key === currentTheme ? 'active' : ''}" data-theme="${key}">
                ${THEMES[key].name}
            </button>`
        ).join('');

        $$('.kb-theme-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                currentTheme = btn.dataset.theme;
                GM_setValue('kbTheme', currentTheme);
                location.reload();
            });
        });
    }

    renderThemeSelector();

    $('#kb-toggle').addEventListener('click', () => {
        const panel = $('#kb-panel');
        panel.classList.toggle('visible');
        if (panel.classList.contains('visible') && !currentData) {
            loadData();
        }
    });

    $('#kb-close').addEventListener('click', () => {
        $('#kb-panel').classList.remove('visible');
    });

    $('#kb-refresh').addEventListener('click', loadData);

    $$('.kb-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            $$('.kb-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTab = tab.dataset.tab;
            render();
        });
    });

    const header = $('#kb-header');
    const panel = $('#kb-panel');

    header.addEventListener('mousedown', (e) => {
        if (e.target.closest('.kb-btn')) return;
        dragState.isDragging = true;
        dragState.startX = e.clientX - panel.offsetLeft;
        dragState.startY = e.clientY - panel.offsetTop;
    });

    document.addEventListener('mousemove', (e) => {
        if (!dragState.isDragging) return;
        e.preventDefault();
        panel.style.left = (e.clientX - dragState.startX) + 'px';
        panel.style.top = (e.clientY - dragState.startY) + 'px';
        panel.style.right = 'auto';
        panel.style.bottom = 'auto';
    });

    document.addEventListener('mouseup', () => {
        dragState.isDragging = false;
    });

    async function openModal(task) {
        const overlay = $('#kb-modal-overlay');
        const title = $('#kb-modal-title');
        const content = $('#kb-modal-content');

        title.textContent = task.title || task.name || 'Tarea';

        const meta = extractMeta(task);
        const metaHtml = renderMeta(meta);

        // Mostrar indicador de carga
        content.innerHTML = `
            <div class="kb-modal-meta">${metaHtml}</div>
            <div class="kb-loading">Cargando descripción...</div>
        `;

        overlay.classList.add('visible');

        let markdownContent = 'Sin descripción adicional.';

        if (currentTicketId && task.title) {
            try {
                const taskTitle = encodeURIComponent(task.title);
                const res = await fetch(`${CONFIG.apiUrl}/api/ticket/${currentTicketId}/task/${taskTitle}/description`);

                if (res.ok) {
                    const data = await res.json();
                    markdownContent = data.description || markdownContent;
                } else {
                    let contentLines = task.content || [task.title || task.name || ''];
                    if (contentLines.length > 1) {
                        contentLines = contentLines.slice(1); // Remover primera línea (título)
                        markdownContent = contentLines.join('\n');
                    }
                }
            } catch (err) {
                console.error('Error al cargar descripción:', err);
                let contentLines = task.content || [task.title || task.name || ''];
                if (contentLines.length > 1) {
                    contentLines = contentLines.slice(1); // Remover primera línea (título)
                    markdownContent = contentLines.join('\n');
                }
            }
        } else {
            let contentLines = task.content || [task.title || task.name || ''];
            if (contentLines.length > 1) {
                contentLines = contentLines.slice(1); // Remover primera línea (título)
                markdownContent = contentLines.join('\n');
            }
        }

        content.innerHTML = `
            <div class="kb-modal-meta">${metaHtml}</div>
            <div class="kb-modal-markdown">${renderMarkdown(markdownContent)}</div>
        `;
    }

    function closeModal() {
        $('#kb-modal-overlay').classList.remove('visible');
    }

    $('#kb-modal-close').addEventListener('click', closeModal);
    $('#kb-modal-overlay').addEventListener('click', (e) => {
        if (e.target === $('#kb-modal-overlay')) closeModal();
    });

    function renderMarkdown(md) {
        let html = md;

        // Headers
        html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');

        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.+?)_/g, '<em>$1</em>');

        // Code blocks
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

        // Inline code
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');

        // Links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

        // Blockquotes
        html = html.replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>');

        // Lists
        html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Line breaks
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    async function loadData() {
        const content = $('#kb-content');
        content.innerHTML = '<div class="kb-loading">Cargando...</div>';

        try {
            const res = await fetch(`${CONFIG.apiUrl}/current-ticket`);

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            }

            const data = await res.json();

            if (!data.lists || !Array.isArray(data.lists)) {
                throw new Error('Formato de respuesta inválido. Asegúrate de usar API v2.');
            }

            currentData = data;
            render();
        } catch (err) {
            content.innerHTML = `
                <div class="kb-error">
                    <div class="kb-error-title">⚠️ Error al cargar datos</div>
                    <div>${err.message}</div>
                    <div style="margin-top: 8px; opacity: 0.8;">
                        Verifica que la API esté corriendo en:<br>
                        <code>${CONFIG.apiUrl}</code>
                    </div>
                </div>
            `;
        }
    }

    function render() {
        if (!currentData) return;

        currentTicketId = currentData.ticket_id;

        $('#kb-ticket-id').textContent = `Ticket: ${currentData.ticket_id || '-'}`;

        const allTasks = [];
        currentData.lists.forEach(list => {
            const listName = list.title.toLowerCase();
            const status = getStatus(listName);

            list.tasks.forEach(task => {
                allTasks.push({
                    ...task,
                    list: list.title,
                    status: status,
                    listName: listName
                });
            });
        });

        const stats = {
            todo: allTasks.filter(t => t.status === 'todo').length,
            doing: allTasks.filter(t => t.status === 'doing').length,
            done: allTasks.filter(t => t.status === 'done').length,
        };

        $('#kb-stat-todo').textContent = stats.todo;
        $('#kb-stat-doing').textContent = stats.doing;
        $('#kb-stat-done').textContent = stats.done;

        let filteredTasks = allTasks;
        if (currentTab !== 'all') {
            filteredTasks = allTasks.filter(t => t.status === currentTab);
        }

        const content = $('#kb-content');

        if (filteredTasks.length === 0) {
            const icons = { all: '📋', todo: '📝', doing: '🔄', done: '✅' };
            const messages = {
                all: 'No hay tareas',
                todo: 'No hay tareas pendientes',
                doing: 'No hay tareas en progreso',
                done: 'No hay tareas completadas'
            };
            content.innerHTML = `
                <div class="kb-empty">
                    <div class="kb-empty-icon">${icons[currentTab]}</div>
                    <div class="kb-empty-text">${messages[currentTab]}</div>
                </div>
            `;
            return;
        }

        content.innerHTML = filteredTasks.map(task => renderTask(task)).join('');

        $$('.kb-task').forEach((el, idx) => {
            el.addEventListener('click', () => openModal(filteredTasks[idx]));
        });
    }

    function getStatus(listName) {
        if (listName.includes('todo') || listName.includes('pending') || listName.includes('por hacer')) {
            return 'todo';
        }
        if (listName.includes('doing') || listName.includes('progress') || listName.includes('haciendo')) {
            return 'doing';
        }
        if (listName.includes('done') || listName.includes('completad') || listName.includes('finished')) {
            return 'done';
        }
        return 'todo';
    }

    function renderTask(task) {
        const meta = extractMeta(task);

        return `
            <div class="kb-task ${task.status}">
                <div class="kb-task-title">${escapeHtml(meta.title)}</div>
                ${renderMeta(meta)}
            </div>
        `;
    }

    function extractMeta(task) {
        const title = task.title || task.name || '';
        return {
            title: title,
            priority: task.priority || null,
            tags: task.tags || [],
            dueDate: task.due_date || null,
            daysUntilDue: task.days_until_due,
            isOverdue: task.is_overdue || false
        };
    }

    function renderMeta(meta) {
        const badges = [];

        if (meta.priority) {
            const icons = { high: '🔴', medium: '🟡', low: '🔵' };
            const labels = { high: 'Alta', medium: 'Media', low: 'Baja' };
            badges.push(`<span class="kb-badge priority-${meta.priority}">${icons[meta.priority]} ${labels[meta.priority]}</span>`);
        }

        if (meta.tags && meta.tags.length > 0) {
            meta.tags.forEach(tag => {
                badges.push(`<span class="kb-badge tag">#${escapeHtml(tag)}</span>`);
            });
        }

        if (meta.dueDate) {
            let dateClass = 'date';
            let icon = '📅';

            if (meta.isOverdue) {
                dateClass = 'date overdue';
                icon = '⚠️';
            } else if (meta.daysUntilDue !== null && meta.daysUntilDue <= 3) {
                dateClass = 'date soon';
                icon = '⏰';
            }

            let suffix = '';
            if (meta.daysUntilDue === 0) suffix = ' (hoy)';
            else if (meta.daysUntilDue === 1) suffix = ' (mañana)';
            else if (meta.isOverdue) suffix = ` (${Math.abs(meta.daysUntilDue)}d vencido)`;
            else if (meta.daysUntilDue <= 7) suffix = ` (${meta.daysUntilDue}d)`;

            badges.push(`<span class="kb-badge ${dateClass}">${icon} ${meta.dueDate}${suffix}</span>`);
        }

        return badges.length > 0 ? `<div class="kb-task-meta">${badges.join('')}</div>` : '';
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    if (CONFIG.autoRefresh > 0) {
        setInterval(() => {
            if ($('#kb-panel').classList.contains('visible')) {
                loadData();
            }
        }, CONFIG.autoRefresh);
    }

    setTimeout(loadData, 1000);

    console.log('✅ Kanban Viewer v2.1 cargado');
})();
