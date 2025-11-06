---
title: "MCP Progress Feedback UI - Research & Technical Specification"
description: "Research and design document for implementing visual progress feedback for MCP server operations"
type: design
status: active
created: "2025-11-06"
updated: "2025-11-06"
author: "CDE Team"
tags:
  - mcp
  - ui
  - progress
  - feedback
  - vscode
llm_summary: |
  Comprehensive research and technical specification for adding visual progress feedback to MCP server operations.
  Compares 4 approaches: floating Python window, VS Code extension, system notifications, and web-based dashboard.
  Recommends VS Code extension as optimal solution with fallback to system notifications.
---

# MCP Progress Feedback UI - Research & Technical Specification

> **Problem**: VS Code no muestra feedback visual cuando las herramientas MCP se están ejecutando
> **Goal**: Implementar sistema de feedback visual transparente y no intrusivo
> **Target**: Ventana flotante 50x50px en esquina inferior derecha con % de progreso

---

## 🎯 Executive Summary

### Problema Identificado

**Contexto**: VS Code Copilot Chat **NO renderiza** los progress updates del MCP protocol en tiempo real:
- ✅ FastMCP envía correctamente `ctx.report_progress()`
- ✅ Logs del servidor muestran progreso
- ❌ UI de VS Code no muestra nada hasta completar

**Impacto**:
- Operaciones largas (15-30s) parecen "congeladas"
- Usuarios no saben si el MCP está trabajando o crashed
- Mala experiencia de usuario, especialmente en tareas pesadas como `cde_onboardingProject`

### Opciones Evaluadas

| Opción | Viabilidad | Complejidad | UX | Recomendación |
|--------|-----------|-------------|-----|---------------|
| **1. Ventana flotante Python** | ⚠️ Media | 🟡 Media | 😐 Regular | ⚠️ Solo si no hay alternativas |
| **2. VS Code Extension** | ✅ Alta | 🔴 Alta | 😊 Excelente | ✅ **RECOMENDADO** |
| **3. Notificaciones Sistema** | ✅ Alta | 🟢 Baja | 😐 Regular | ✅ Fallback |
| **4. Web Dashboard** | ✅ Alta | 🟡 Media | 😊 Bueno | ⏸️ Futuro |

### Recomendación Final

**Implementar en 2 fases**:

1. **Fase 1 (Quick Win)**: Sistema de notificaciones (1-2 días)
2. **Fase 2 (Ideal)**: VS Code Extension (1-2 semanas)

---

## 📊 Option 1: Ventana Flotante Python

### Overview

Crear una ventana nativa de Python usando `tkinter` o `PyQt5` que se lance automáticamente cuando el MCP server está ejecutando operaciones.

### Technical Implementation

#### Tecnologías

**Option A: tkinter** (Built-in)
```python
import tkinter as tk
from tkinter import ttk
import threading

class ProgressOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CDE MCP Progress")

        # Configuration
        self.root.geometry("200x80+{}+{}".format(
            self.root.winfo_screenwidth() - 220,
            self.root.winfo_screenheight() - 120
        ))

        # Transparency
        self.root.attributes('-alpha', 0.8)  # 80% opacity
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)  # No window decorations

        # Disable interactions
        self.root.attributes('-transparentcolor', 'white')

        # UI Elements
        self.label = tk.Label(self.root, text="Initializing...", font=("Arial", 10))
        self.label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, length=180, mode='determinate')
        self.progress.pack(pady=5)

        self.time_label = tk.Label(self.root, text="0s", font=("Arial", 8))
        self.time_label.pack()

    def update_progress(self, percentage: float, task: str, elapsed: float):
        self.progress['value'] = percentage * 100
        self.label.config(text=f"{task} ({int(percentage*100)}%)")
        self.time_label.config(text=f"{elapsed:.1f}s")
        self.root.update()

    def show(self):
        self.root.deiconify()

    def hide(self):
        self.root.withdraw()

    def destroy(self):
        self.root.destroy()
```

**Option B: PyQt5** (More features)
```python
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor

class ProgressOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # Window flags
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # No frame
            Qt.WindowStaysOnTopHint |  # Always on top
            Qt.Tool  # Don't show in taskbar
        )

        # Transparency
        self.setWindowOpacity(0.8)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Size & position
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - 220,
            screen.height() - 120,
            200, 80
        )

        # UI Layout
        layout = QVBoxLayout()

        self.task_label = QLabel("Initializing...")
        self.task_label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(self.task_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.time_label = QLabel("0s")
        self.time_label.setStyleSheet("color: white; font-size: 10px;")
        layout.addWidget(self.time_label)

        self.setLayout(layout)

    def update_progress(self, percentage: float, task: str, elapsed: float):
        self.progress_bar.setValue(int(percentage * 100))
        self.task_label.setText(f"{task} ({int(percentage*100)}%)")
        self.time_label.setText(f"{elapsed:.1f}s")
```

#### Integration with MCP Server

**File**: `src/cde_orchestrator/ui/progress_overlay.py`

```python
import os
import threading
import time
from typing import Optional
from contextlib import contextmanager

class ProgressManager:
    """Manages progress overlay window lifecycle"""

    def __init__(self):
        self.enabled = os.getenv("CDE_SHOW_PROGRESS", "false").lower() == "true"
        self.overlay: Optional[ProgressOverlay] = None
        self.ui_thread: Optional[threading.Thread] = None
        self.start_time: float = 0

    def start(self, initial_task: str = "Initializing..."):
        """Start progress overlay in separate thread"""
        if not self.enabled:
            return

        self.start_time = time.time()

        def run_ui():
            # Create QApplication or tkinter root
            app = QApplication([])
            self.overlay = ProgressOverlay()
            self.overlay.show()
            self.overlay.update_progress(0.0, initial_task, 0.0)
            app.exec_()

        self.ui_thread = threading.Thread(target=run_ui, daemon=True)
        self.ui_thread.start()
        time.sleep(0.1)  # Wait for window to initialize

    def update(self, percentage: float, task: str):
        """Update progress display"""
        if not self.enabled or not self.overlay:
            return

        elapsed = time.time() - self.start_time
        self.overlay.update_progress(percentage, task, elapsed)

    def finish(self):
        """Close progress overlay"""
        if not self.enabled or not self.overlay:
            return

        self.overlay.destroy()
        self.overlay = None

    @contextmanager
    def progress_context(self, initial_task: str = "Starting..."):
        """Context manager for automatic progress lifecycle"""
        try:
            self.start(initial_task)
            yield self
        finally:
            self.finish()

# Global instance
progress_manager = ProgressManager()
```

**Integration in MCP Tools**:

```python
# src/mcp_tools/onboarding.py
from cde_orchestrator.ui.progress_overlay import progress_manager

async def cde_onboardingProject(ctx: Context, project_path: str = ".") -> str:
    """Onboarding with visual progress overlay"""

    with progress_manager.progress_context("CDE Onboarding"):
        # Checkpoint 1
        await ctx.info("📁 Scanning structure...")
        await ctx.report_progress(0.2, 1.0, "Scanning")
        progress_manager.update(0.2, "Scanning structure...")

        # ... rest of implementation

        # Checkpoint 6
        await ctx.info("✅ Complete!")
        await ctx.report_progress(1.0, 1.0, "Complete")
        progress_manager.update(1.0, "Complete!")

    return result
```

### Pros & Cons

**✅ Pros**:
- ✅ Funciona **inmediatamente** sin necesidad de extensiones
- ✅ Control total sobre UI y estilo
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Se puede activar/desactivar vía ENV (`CDE_SHOW_PROGRESS`)
- ✅ No intrusivo (pequeño, transparente, esquina)

**❌ Cons**:
- ❌ **Problema crítico**: VS Code ejecuta MCP server como proceso hijo sin GUI
- ❌ Requiere dependencias adicionales (`PyQt5` o `tkinter`)
- ❌ Puede causar problemas en entornos headless (servidores, Docker)
- ❌ Threading complexity (UI en thread separado)
- ❌ **No funciona en WSL** sin X11 forwarding
- ❌ Puede ser bloqueado por políticas de seguridad corporativas

### Viabilidad Assessment

**Rating**: ⚠️ **Media** - Funcional pero con limitaciones significativas

**Blockers**:
1. **VS Code subprocess**: MCP server corre como proceso hijo sin acceso a GUI
2. **Headless environments**: No funcionará en CI/CD, Docker, SSH
3. **Platform issues**: macOS sandbox puede bloquear ventanas flotantes

**Workaround**: Lanzar proceso separado:
```python
# En server.py
if os.getenv("CDE_SHOW_PROGRESS") == "true":
    subprocess.Popen(["python", "src/ui/progress_daemon.py"])
```

---

## 📊 Option 2: VS Code Extension

### Overview

Crear una extensión de VS Code que:
1. Se comunica con el MCP server via WebSocket o archivo compartido
2. Muestra progreso en la UI nativa de VS Code (status bar o notification)
3. Se integra perfectamente con el ecosistema de VS Code

### Technical Implementation

#### Extension Architecture

```
cde-progress-extension/
├── package.json              # Extension manifest
├── src/
│   ├── extension.ts          # Main entry point
│   ├── progressTracker.ts    # Progress monitoring
│   ├── statusBarUI.ts        # Status bar integration
│   └── webSocketClient.ts    # Communication with MCP
└── resources/
    └── icons/                # Progress icons
```

#### Key Components

**1. Extension Manifest** (`package.json`)

```json
{
  "name": "cde-mcp-progress",
  "displayName": "CDE MCP Progress Tracker",
  "description": "Visual progress feedback for CDE Orchestrator MCP operations",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.85.0"
  },
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "title": "CDE MCP Progress",
      "properties": {
        "cde.progress.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable visual progress tracking"
        },
        "cde.progress.location": {
          "type": "string",
          "enum": ["statusBar", "notification", "both"],
          "default": "statusBar",
          "description": "Where to display progress"
        }
      }
    }
  }
}
```

**2. Progress Tracker** (`src/progressTracker.ts`)

```typescript
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface ProgressState {
    taskId: string;
    percentage: number;
    message: string;
    elapsed: number;
    startTime: number;
}

export class ProgressTracker {
    private statusBarItem: vscode.StatusBarItem;
    private progressFile: string;
    private watcher: fs.FSWatcher | null = null;
    private currentProgress: ProgressState | null = null;

    constructor(private context: vscode.ExtensionContext) {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.context.subscriptions.push(this.statusBarItem);

        // Watch for progress file changes
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (workspaceRoot) {
            this.progressFile = path.join(workspaceRoot, '.cde', 'progress.json');
            this.startWatching();
        }
    }

    private startWatching() {
        // Ensure directory exists
        const progressDir = path.dirname(this.progressFile);
        if (!fs.existsSync(progressDir)) {
            fs.mkdirSync(progressDir, { recursive: true });
        }

        // Watch for file changes
        this.watcher = fs.watch(this.progressFile, (eventType) => {
            if (eventType === 'change') {
                this.updateProgress();
            }
        });
    }

    private updateProgress() {
        try {
            if (!fs.existsSync(this.progressFile)) {
                this.hideProgress();
                return;
            }

            const data = fs.readFileSync(this.progressFile, 'utf8');
            const progress: ProgressState = JSON.parse(data);

            this.currentProgress = progress;
            this.showProgress(progress);
        } catch (error) {
            console.error('Error reading progress file:', error);
        }
    }

    private showProgress(progress: ProgressState) {
        const percentage = Math.round(progress.percentage * 100);
        const elapsed = progress.elapsed.toFixed(1);

        this.statusBarItem.text = `$(sync~spin) ${progress.message} ${percentage}% (${elapsed}s)`;
        this.statusBarItem.tooltip = `CDE MCP: ${progress.message}`;
        this.statusBarItem.show();

        // Also show notification for major milestones
        if (percentage === 0 || percentage === 100 || percentage % 25 === 0) {
            vscode.window.showInformationMessage(
                `CDE MCP: ${progress.message} (${percentage}%)`
            );
        }
    }

    private hideProgress() {
        this.statusBarItem.hide();
        this.currentProgress = null;
    }

    public dispose() {
        this.watcher?.close();
        this.statusBarItem.dispose();
    }
}
```

**3. Extension Activation** (`src/extension.ts`)

```typescript
import * as vscode from 'vscode';
import { ProgressTracker } from './progressTracker';

export function activate(context: vscode.ExtensionContext) {
    console.log('CDE MCP Progress extension activated');

    const config = vscode.workspace.getConfiguration('cde.progress');
    const enabled = config.get<boolean>('enabled', true);

    if (enabled) {
        const tracker = new ProgressTracker(context);
        context.subscriptions.push(tracker);
    }
}

export function deactivate() {}
```

#### MCP Server Integration

**File**: `src/cde_orchestrator/ui/vscode_progress.py`

```python
import json
import os
import time
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

class VSCodeProgressReporter:
    """Reports progress to VS Code extension via shared file"""

    def __init__(self, workspace_root: Path):
        self.enabled = os.getenv("CDE_SHOW_PROGRESS", "true").lower() == "true"
        self.progress_file = workspace_root / ".cde" / "progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.start_time: float = 0
        self.task_id: str = ""

    def start(self, task_id: str, initial_message: str = "Starting..."):
        """Initialize progress tracking"""
        if not self.enabled:
            return

        self.start_time = time.time()
        self.task_id = task_id
        self._write_progress(0.0, initial_message)

    def update(self, percentage: float, message: str):
        """Update progress"""
        if not self.enabled:
            return

        self._write_progress(percentage, message)

    def finish(self):
        """Complete progress tracking"""
        if not self.enabled:
            return

        self._write_progress(1.0, "Complete")
        time.sleep(0.5)  # Give extension time to show 100%

        # Clean up file
        if self.progress_file.exists():
            self.progress_file.unlink()

    def _write_progress(self, percentage: float, message: str):
        """Write progress state to file"""
        elapsed = time.time() - self.start_time

        state = {
            "taskId": self.task_id,
            "percentage": percentage,
            "message": message,
            "elapsed": elapsed,
            "startTime": self.start_time
        }

        try:
            self.progress_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            # Silently fail - don't crash MCP operation
            pass

    @contextmanager
    def progress_context(self, task_id: str, initial_message: str = "Starting..."):
        """Context manager for automatic progress lifecycle"""
        try:
            self.start(task_id, initial_message)
            yield self
        finally:
            self.finish()

# Usage in MCP tools
async def cde_onboardingProject(ctx: Context, project_path: str = ".") -> str:
    """Onboarding with VS Code progress"""

    project_root = Path(project_path).resolve()
    reporter = VSCodeProgressReporter(project_root)

    with reporter.progress_context("onboarding", "CDE Onboarding Started"):
        # Checkpoint 1
        await ctx.info("📁 Scanning structure...")
        reporter.update(0.2, "Scanning structure...")

        # ... implementation

        # Checkpoint 6
        await ctx.info("✅ Complete!")
        reporter.update(1.0, "Complete!")

    return result
```

### Pros & Cons

**✅ Pros**:
- ✅ **Perfecta integración** con VS Code UI
- ✅ Usa componentes nativos (status bar, notifications)
- ✅ No requiere procesos separados ni threading
- ✅ Funciona en **todos los entornos** (local, remote, WSL, Docker)
- ✅ Usuarios ya confían en extensiones de VS Code
- ✅ Puede publicarse en VS Code Marketplace
- ✅ Soporta themes (respeta dark/light mode)
- ✅ Acceso a todas las APIs de VS Code (commands, settings, etc.)

**❌ Cons**:
- ❌ **Alto esfuerzo de desarrollo** (1-2 semanas)
- ❌ Requiere aprender TypeScript + VS Code Extension API
- ❌ Necesita publicación y distribución separada
- ❌ Usuarios deben instalar la extensión manualmente
- ❌ Requiere mantenimiento independiente del MCP server

### Viabilidad Assessment

**Rating**: ✅ **Alta** - Solución ideal a largo plazo

**Recomendación**:
- ✅ **Fase 2** después de implementar quick wins
- ✅ Vale la pena para experiencia profesional
- ✅ Diferenciador competitivo vs otros MCP servers

**Roadmap**:
1. **Week 1**: Setup extension project, basic file watcher
2. **Week 2**: Status bar UI, configuration, testing
3. **Week 3**: Polish, documentation, marketplace submission

---

## 📊 Option 3: System Notifications

### Overview

Usar notificaciones del sistema operativo (Windows Toast, macOS Notification Center, Linux libnotify) para mostrar progreso en puntos clave.

### Technical Implementation

#### Library: `plyer` (Cross-platform)

```bash
pip install plyer
```

**Implementation**:

```python
# src/cde_orchestrator/ui/system_notifications.py
import os
from typing import Optional
from plyer import notification
import time

class SystemNotifier:
    """Send system notifications for MCP progress"""

    def __init__(self):
        self.enabled = os.getenv("CDE_NOTIFY_PROGRESS", "true").lower() == "true"
        self.app_name = "CDE Orchestrator"
        self.icon_path = None  # TODO: Add .ico file

    def notify_start(self, task_name: str):
        """Notify task started"""
        if not self.enabled:
            return

        notification.notify(
            title=f"🚀 {self.app_name}",
            message=f"Started: {task_name}",
            app_name=self.app_name,
            app_icon=self.icon_path,
            timeout=3
        )

    def notify_progress(self, task_name: str, percentage: int, message: str):
        """Notify progress milestone (only 25%, 50%, 75%)"""
        if not self.enabled:
            return

        if percentage not in [25, 50, 75]:
            return  # Only notify key milestones

        notification.notify(
            title=f"📊 {self.app_name} - {percentage}%",
            message=f"{task_name}: {message}",
            app_name=self.app_name,
            app_icon=self.icon_path,
            timeout=2
        )

    def notify_complete(self, task_name: str, duration: float):
        """Notify task completed"""
        if not self.enabled:
            return

        notification.notify(
            title=f"✅ {self.app_name} - Complete",
            message=f"{task_name} finished in {duration:.1f}s",
            app_name=self.app_name,
            app_icon=self.icon_path,
            timeout=5
        )

    def notify_error(self, task_name: str, error: str):
        """Notify task failed"""
        if not self.enabled:
            return

        notification.notify(
            title=f"❌ {self.app_name} - Error",
            message=f"{task_name}: {error}",
            app_name=self.app_name,
            app_icon=self.icon_path,
            timeout=10
        )

# Usage
notifier = SystemNotifier()

async def cde_onboardingProject(ctx: Context, project_path: str = ".") -> str:
    """Onboarding with system notifications"""

    start_time = time.time()
    notifier.notify_start("Project Onboarding")

    try:
        # Checkpoint 1 (20%)
        await ctx.info("📁 Scanning structure...")
        # No notification - too early

        # Checkpoint 2 (50%)
        await ctx.info("📊 Analyzing Git history...")
        notifier.notify_progress("Onboarding", 50, "Analyzing Git history")

        # Checkpoint 3 (75%)
        await ctx.info("🤖 Detecting AI assistants...")
        notifier.notify_progress("Onboarding", 75, "Detecting AI assistants")

        # Complete
        duration = time.time() - start_time
        notifier.notify_complete("Project Onboarding", duration)

        return result

    except Exception as e:
        notifier.notify_error("Project Onboarding", str(e))
        raise
```

### Alternative: Windows-specific (richer UI)

```python
# For Windows only - richer toast notifications
from win10toast import ToastNotifier

class WindowsNotifier:
    def __init__(self):
        self.toaster = ToastNotifier()

    def notify_progress(self, title: str, message: str, duration: int = 3):
        """Show Windows 10/11 toast notification"""
        self.toaster.show_toast(
            title,
            message,
            icon_path="path/to/icon.ico",
            duration=duration,
            threaded=True
        )
```

### Pros & Cons

**✅ Pros**:
- ✅ **Muy fácil de implementar** (< 1 día)
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ No requiere procesos adicionales
- ✅ Nativo del OS - usuarios ya están familiarizados
- ✅ Funciona en **cualquier entorno** (incluso remote)
- ✅ Ligero - casi sin overhead
- ✅ Fácil de activar/desactivar vía ENV

**❌ Cons**:
- ❌ **No es continuo** - solo notifica en milestones
- ❌ Puede ser intrusivo si muchas notificaciones
- ❌ No muestra % en tiempo real
- ❌ Usuario debe tener notificaciones habilitadas
- ❌ Puede ser bloqueado por Do Not Disturb
- ❌ No muestra tiempo transcurrido

### Viabilidad Assessment

**Rating**: ✅ **Alta** - Excelente quick win

**Recomendación**:
- ✅ **Fase 1** - Implementar **inmediatamente**
- ✅ Bajo riesgo, alto valor
- ✅ Funciona mientras se desarrolla VS Code extension

**Implementation Time**: 1-2 días

---

## 📊 Option 4: Web Dashboard (Future)

### Overview

Crear un dashboard web local que muestre progreso en tiempo real de todas las operaciones MCP.

### Technical Implementation (Brief)

```python
# FastAPI dashboard running on localhost:8765
from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

class ProgressBroadcaster:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def broadcast(self, data: dict):
        for ws in self.connections:
            await ws.send_json(data)

broadcaster = ProgressBroadcaster()

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    broadcaster.connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except:
        broadcaster.connections.remove(websocket)

@app.get("/")
async def dashboard():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CDE MCP Progress</title>
        <script>
            const ws = new WebSocket('ws://localhost:8765/ws/progress');
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateProgress(data);
            };
        </script>
    </head>
    <body>
        <h1>CDE MCP Operations</h1>
        <div id="progress-list"></div>
    </body>
    </html>
    """)
```

### Pros & Cons

**✅ Pros**:
- ✅ Rich UI possibilities (charts, logs, history)
- ✅ Multiple operations visible simultaneously
- ✅ Can show detailed logs and metrics
- ✅ Accessible from any browser
- ✅ Easy to style and customize

**❌ Cons**:
- ❌ Requires running separate web server
- ❌ User must open browser manually
- ❌ Port conflicts possible
- ❌ Security concerns (localhost exposure)
- ❌ Overkill for simple progress display

### Viabilidad Assessment

**Rating**: ⏸️ **Future** - No para MVP

**Recomendación**: Considerar para **Fase 3** si hay demanda

---

## 🎯 Final Recommendation

### Recommended Approach: Hybrid 2-Phase Implementation

#### Phase 1: System Notifications (Quick Win) ✅ IMMEDIATE

**Timeline**: 1-2 días
**Effort**: 🟢 Low
**Impact**: 😊 Medium-High

**Implementation**:
1. Add `plyer` dependency
2. Create `SystemNotifier` class
3. Integrate into all MCP tools (only milestone notifications)
4. Add ENV toggle: `CDE_NOTIFY_PROGRESS=true`
5. Test on Windows, macOS, Linux

**Why First**:
- ✅ Can ship **this week**
- ✅ Immediate value for users
- ✅ Low risk, minimal code changes
- ✅ Works as fallback while building extension

#### Phase 2: VS Code Extension (Ideal Solution) ✅ RECOMMENDED

**Timeline**: 2-3 semanas
**Effort**: 🔴 High
**Impact**: 😊😊😊 Excellent

**Implementation**:
1. **Week 1**: Extension scaffold + file watcher
2. **Week 2**: Status bar UI + notifications
3. **Week 3**: Polish + documentation + publish

**Why Second**:
- ✅ Professional, polished solution
- ✅ Perfect integration with VS Code
- ✅ Competitive advantage
- ✅ Can iterate based on Phase 1 feedback

**Deliverables**:
- VS Code extension published to Marketplace
- Automatic progress updates in status bar
- Optional notification popups
- Configuration via VS Code settings
- Works in all environments (local, remote, WSL)

### Configuration via ENV

Update `.vscode/mcp.json`:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "env": {
        "PYTHONPATH": "src",
        "CDE_AUTO_DISCOVER": "true",
        "CDE_LOG_LEVEL": "INFO",

        // ✨ NEW: Progress feedback settings
        "CDE_NOTIFY_PROGRESS": "true",        // Phase 1: System notifications
        "CDE_NOTIFY_MILESTONES_ONLY": "true", // Only 25%, 50%, 75%, 100%
        "CDE_VSCODE_PROGRESS": "true"         // Phase 2: VS Code extension
      }
    }
  }
}
```

---

## 📝 Implementation Checklist

### Phase 1: System Notifications ✅

- [ ] Install `plyer` library
- [ ] Create `src/cde_orchestrator/ui/system_notifications.py`
- [ ] Implement `SystemNotifier` class
- [ ] Add notifications to `cde_onboardingProject`
- [ ] Add notifications to `cde_scanDocumentation`
- [ ] Add notifications to `cde_analyzeDocumentation`
- [ ] Add notifications to `cde_executeFullImplementation`
- [ ] Add ENV configuration to `mcp.json`
- [ ] Test on Windows
- [ ] Test on macOS (if available)
- [ ] Test on Linux (if available)
- [ ] Update documentation (AGENTS.md, README.md)
- [ ] Commit and deploy

### Phase 2: VS Code Extension 📋

- [ ] Initialize VS Code extension project
- [ ] Setup TypeScript configuration
- [ ] Implement `ProgressTracker` class
- [ ] Implement file watcher for `.cde/progress.json`
- [ ] Add status bar UI
- [ ] Add notification UI (optional)
- [ ] Create `VSCodeProgressReporter` in Python
- [ ] Integrate reporter into all MCP tools
- [ ] Add extension configuration settings
- [ ] Write extension tests
- [ ] Write documentation for extension
- [ ] Package extension (`.vsix`)
- [ ] Test extension locally
- [ ] Publish to VS Code Marketplace
- [ ] Update MCP server documentation
- [ ] Announce to users

---

## 🔗 References

### Documentation

- **VS Code Extension API**: https://code.visualstudio.com/api
- **MCP Protocol Spec**: https://modelcontextprotocol.io/docs
- **FastMCP Context API**: https://github.com/modelcontextprotocol/python-sdk
- **plyer Notifications**: https://github.com/kivy/plyer

### Related Documents

- `agent-docs/feedback/vscode-mcp-progress-limitations-2025-11-02.md` - Original problem analysis
- `agent-docs/execution/mcp-progress-tracking-implementation-2025-11-02.md` - Current progress implementation
- `specs/design/ARCHITECTURE.md` - MCP server architecture

### Tools & Libraries

- **Python UI**: tkinter (built-in), PyQt5, plyer (notifications)
- **VS Code Extension**: TypeScript, VS Code Extension API
- **Web Dashboard**: FastAPI, WebSockets, React (future)

---

## 📈 Success Metrics

### Phase 1 Success Criteria

- ✅ Notifications appear at 25%, 50%, 75%, 100%
- ✅ Start/complete notifications always show
- ✅ Error notifications include context
- ✅ Works on Windows (primary target)
- ✅ Can be toggled via ENV variable
- ✅ No performance degradation

### Phase 2 Success Criteria

- ✅ Extension installs cleanly from Marketplace
- ✅ Status bar updates in real-time (< 1s latency)
- ✅ Works in local, remote, and WSL environments
- ✅ Configuration persists across sessions
- ✅ No crashes or errors in extension host
- ✅ Positive user feedback (survey)

---

## 🚀 Next Steps

1. **TODAY**: Review this document with team
2. **Day 1-2**: Implement Phase 1 (System Notifications)
3. **Day 3**: Test and refine Phase 1
4. **Week 1**: Deploy Phase 1 to users, gather feedback
5. **Week 2-3**: Start Phase 2 (VS Code Extension)
6. **Week 4**: Test and publish Phase 2
7. **Week 5+**: Monitor metrics, iterate based on feedback

---

**Status**: ✅ Ready for Implementation
**Owner**: CDE Team
**Timeline**: Phase 1 (This Week), Phase 2 (Next Month)
