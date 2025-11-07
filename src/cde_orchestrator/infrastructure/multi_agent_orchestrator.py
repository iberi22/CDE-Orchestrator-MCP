"""
Multi-Agent Orchestration Module

Coordina la delegación de tareas a múltiples agentes CLI (Claude Code, Aider, Codex)
usando la infraestructura del CDE Orchestrator. Utiliza skills, workflows y lógica
de orquestación para completar el 100% de funcionalidad.

Flujo:
1. cde_selectWorkflow() -> Analiza tarea y selecciona workflow óptimo
2. cde_sourceSkill() -> Descarga skills necesarios
3. _select_best_agent() -> Selecciona agente CLI según capacidad
4. _execute_with_agent_cli() -> Delega a Claude Code, Aider o Codex
5. _manage_context() -> Mantiene contexto entre agentes
6. _validate_and_publish() -> Valida resultados y publica cambios
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Tipos de agentes CLI disponibles."""

    CLAUDE_CODE = "claude-code"  # Bedrock via CloudCode
    AIDER = "aider"  # Aider CLI
    CODEX = "codex"  # GitHub Copilot CLI
    JULES = "jules"  # Jules AI agent
    CODEIUM = "codeium"  # Codeium CLI


@dataclass
class AgentCapability:
    """Capacidades de cada agente."""

    agent_type: AgentType
    strengths: List[str]  # Lo que hace bien
    limitations: List[str]  # Lo que NO hace
    requires_auth: bool  # Requiere autenticación
    requires_bedrock: bool  # Requiere AWS Bedrock
    installed: bool = False  # Detectado en sistema
    version: Optional[str] = None  # Versión instalada


@dataclass
class TaskDefinition:
    """Define una tarea de implementación."""

    task_id: str
    title: str
    description: str
    phase: str  # "verify", "implement", "test", "document"
    complexity: str  # "trivial", "simple", "moderate", "complex"
    required_skills: List[str]
    estimated_hours: float
    acceptance_criteria: List[str]
    suggested_agent: Optional[AgentType] = None


class MultiAgentOrchestrator:
    """
    Orquestador de múltiples agentes CLI para completar tareas del CDE Orchestrator.

    Usa la lógica de skills, workflows y state management del proyecto mismo
    para coordinar el trabajo entre agentes.
    """

    def __init__(self, project_path: str = "."):
        """Inicializa el orquestador."""
        self.project_path = Path(project_path)
        self.agent_capabilities = self._detect_available_agents()
        self.context_stack: Dict[str, Any] = {}
        self.execution_log: List[Dict[str, Any]] = []

    def _detect_available_agents(self) -> Dict[AgentType, AgentCapability]:
        """Detecta qué agentes están disponibles en el sistema."""
        agents = {}

        # Claude Code via CloudCode CLI (con Bedrock)
        if self._check_command("claude-code"):
            agents[AgentType.CLAUDE_CODE] = AgentCapability(
                agent_type=AgentType.CLAUDE_CODE,
                strengths=[
                    "Análisis de código completo",
                    "Refactoring de arquitectura",
                    "Integración con sistemas existentes",
                    "Debugging avanzado",
                ],
                limitations=["No acceso a filesystem directo", "Requiere Bedrock"],
                requires_auth=True,
                requires_bedrock=True,
                installed=True,
                version=self._get_command_version("claude-code"),
            )

        # Aider CLI
        if self._check_command("aider"):
            agents[AgentType.AIDER] = AgentCapability(
                agent_type=AgentType.AIDER,
                strengths=[
                    "Edición de archivos multilenguaje",
                    "Pair programming interactivo",
                    "Tests y debugging",
                    "Refactoring seguro",
                ],
                limitations=[
                    "Sesiones largas son lentas",
                    "Menos análisis de alto nivel",
                ],
                requires_auth=False,
                requires_bedrock=False,
                installed=True,
                version=self._get_command_version("aider"),
            )

        # Codex via GitHub CLI
        if self._check_command("gh copilot"):
            agents[AgentType.CODEX] = AgentCapability(
                agent_type=AgentType.CODEX,
                strengths=[
                    "Sugerencias de código rápidas",
                    "Generación de tests",
                    "Snippets y templates",
                    "Explicaciones de código",
                ],
                limitations=["Limpio para contexto largo", "Sin acceso a filesystem"],
                requires_auth=True,
                requires_bedrock=False,
                installed=True,
                version=self._get_command_version("gh"),
            )

        logger.info(
            f"Detectados {len(agents)} agentes disponibles: {list(agents.keys())}"
        )
        return agents

    @staticmethod
    def _check_command(cmd: str) -> bool:
        """Verifica si un comando está disponible en PATH."""
        try:
            subprocess.run(
                ["where" if os.name == "nt" else "which", cmd.split()[0]],
                capture_output=True,
                timeout=2,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def _get_command_version(cmd: str) -> Optional[str]:
        """Obtiene la versión de un comando."""
        try:
            result = subprocess.run(
                [cmd.split()[0], "--version"], capture_output=True, text=True, timeout=3
            )
            return result.stdout.strip().split("\n")[0]
        except Exception as e:
            logger.warning(f"No se pudo obtener versión de {cmd}: {e}")
            return None

    def _select_best_agent(
        self, task: TaskDefinition, available_agents: Optional[List[AgentType]] = None
    ) -> AgentType:
        """
        Selecciona el mejor agente para una tarea.

        Lógica:
        - Tareas complejas de arquitectura -> Claude Code (mejor análisis)
        - Edición de múltiples archivos -> Aider (filesystem seguro)
        - Snippets y sugerencias rápidas -> Codex (rápido)
        - Tareas complejas multi-fase -> Jules (full context)
        """
        if available_agents is None:
            available_agents = list(self.agent_capabilities.keys())

        # Preferencias según complejidad
        if task.complexity == "complex" and task.phase in ["implement", "refactor"]:
            # Tareas complejas -> Claude Code (mejor análisis)
            if AgentType.CLAUDE_CODE in available_agents:
                return AgentType.CLAUDE_CODE
            elif AgentType.AIDER in available_agents:
                return AgentType.AIDER

        elif task.complexity in ["simple", "moderate"] and task.phase == "implement":
            # Ediciones múltiples -> Aider (seguro)
            if AgentType.AIDER in available_agents:
                return AgentType.AIDER
            elif AgentType.CLAUDE_CODE in available_agents:
                return AgentType.CLAUDE_CODE

        elif task.phase in ["test", "verify"]:
            # Tests y verificación -> Codex (rápido) o Aider (completo)
            if AgentType.CODEX in available_agents:
                return AgentType.CODEX
            elif AgentType.AIDER in available_agents:
                return AgentType.AIDER

        # Default: primer agente disponible
        return available_agents[0] if available_agents else AgentType.JULES

    async def execute_task(
        self, task: TaskDefinition, skills_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una tarea delegándola al agente más apropiado.

        Args:
            task: Definición de la tarea
            skills_context: Skills necesarios (descargados previamente)

        Returns:
            Resultado de ejecución con archivos modificados, logs, etc.
        """
        logger.info(f"🎯 Ejecutando tarea: {task.title} (ID: {task.task_id})")

        # Seleccionar agente
        agent = self._select_best_agent(task)
        logger.info(f"✅ Agente seleccionado: {agent.value}")

        # Guardar en contexto
        self.context_stack[task.task_id] = {
            "task": asdict(task),
            "agent": agent.value,
            "skills": skills_context or {},
            "status": "in_progress",
        }

        try:
            # Ejecutar con el agente seleccionado
            result = await self._execute_with_agent(agent, task, skills_context)

            # Actualizar contexto
            self.context_stack[task.task_id]["status"] = "completed"
            self.context_stack[task.task_id]["result"] = result

            # Registrar en log
            self.execution_log.append(
                {
                    "task_id": task.task_id,
                    "agent": agent.value,
                    "status": "success",
                    "duration": result.get("duration", 0),
                    "files_modified": result.get("files_modified", []),
                }
            )

            return result

        except Exception as e:
            logger.error(f"❌ Error ejecutando tarea {task.task_id}: {e}")
            self.context_stack[task.task_id]["status"] = "failed"
            self.context_stack[task.task_id]["error"] = str(e)
            raise

    async def _execute_with_agent(
        self,
        agent: AgentType,
        task: TaskDefinition,
        skills_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Ejecuta tarea con un agente específico."""

        if agent == AgentType.CLAUDE_CODE:
            return await self._execute_with_claude_code(task, skills_context)
        elif agent == AgentType.AIDER:
            return await self._execute_with_aider(task, skills_context)
        elif agent == AgentType.CODEX:
            return await self._execute_with_codex(task, skills_context)
        elif agent == AgentType.JULES:
            return await self._execute_with_jules(task, skills_context)
        else:
            raise ValueError(f"Agente no soportado: {agent}")

    async def _execute_with_claude_code(
        self, task: TaskDefinition, skills_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta tarea usando Claude Code CLI con Bedrock.

        ```bash
        claude-code run --provider bedrock --model anthropic.claude-sonnet-4-5 \
          --prompt "tu prompt aquí"
        ```
        """
        import time

        # Construir prompt con contexto de skills
        prompt = self._build_prompt_with_context(task, skills_context)

        logger.info("🔄 Delegando a Claude Code...")
        start_time = time.time()

        try:
            # Ejecutar Claude Code CLI
            cmd = [
                "claude-code",
                "run",
                "--provider",
                "bedrock",
                "--model",
                "anthropic.claude-sonnet-4-5-20250929-v1:0",
                "--prompt",
                prompt,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hora max
                cwd=str(self.project_path),
            )

            elapsed = time.time() - start_time

            if result.returncode != 0:
                logger.error(f"Claude Code falló: {result.stderr}")
                raise RuntimeError(f"Claude Code error: {result.stderr}")

            # Parsear output
            output = result.stdout
            files_modified = self._extract_modified_files(output)

            logger.info(f"✅ Claude Code completado en {elapsed:.1f}s")
            logger.info(f"📝 Archivos modificados: {len(files_modified)}")

            return {
                "status": "success",
                "agent": "claude-code",
                "duration": elapsed,
                "files_modified": files_modified,
                "output": output,
                "errors": [],
            }

        except subprocess.TimeoutExpired:
            logger.error("⏱️ Claude Code timeout (> 1 hora)")
            raise
        except Exception as e:
            logger.error(f"❌ Error ejecutando Claude Code: {e}")
            raise

    async def _execute_with_aider(
        self, task: TaskDefinition, skills_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta tarea usando Aider CLI.

        ```bash
        aider --message "tu prompt aquí" file1.py file2.py ...
        ```
        """
        import time

        prompt = self._build_prompt_with_context(task, skills_context)
        logger.info("🔄 Delegando a Aider...")
        start_time = time.time()

        try:
            # Construir comando Aider
            cmd = [
                "aider",
                "--message",
                prompt,
                "--yes",  # No preguntar confirmación
                "--no-auto-commits",  # No hacer commits automáticos
            ]

            # Agregar archivos relevantes (si existen)
            relevant_files = self._find_relevant_files(task)
            cmd.extend(relevant_files)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutos max
                cwd=str(self.project_path),
            )

            elapsed = time.time() - start_time

            if result.returncode != 0:
                logger.warning(f"Aider warning: {result.stderr}")
                # No es error, Aider devuelve código 1 a veces

            files_modified = self._extract_modified_files(result.stdout)

            logger.info(f"✅ Aider completado en {elapsed:.1f}s")
            logger.info(f"📝 Archivos modificados: {len(files_modified)}")

            return {
                "status": "success",
                "agent": "aider",
                "duration": elapsed,
                "files_modified": files_modified,
                "output": result.stdout,
                "errors": [result.stderr] if result.stderr else [],
            }

        except subprocess.TimeoutExpired:
            logger.error("⏱️ Aider timeout (> 30 minutos)")
            raise
        except Exception as e:
            logger.error(f"❌ Error ejecutando Aider: {e}")
            raise

    async def _execute_with_codex(
        self, task: TaskDefinition, skills_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta tarea usando GitHub Copilot CLI (Codex).

        ```bash
        gh copilot suggest "tu prompt aquí"
        ```
        """
        import time

        prompt = self._build_prompt_with_context(task, skills_context)
        logger.info("🔄 Delegando a Codex (GitHub Copilot)...")
        start_time = time.time()

        try:
            cmd = ["gh", "copilot", "suggest", prompt]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos max
                cwd=str(self.project_path),
            )

            elapsed = time.time() - start_time

            if result.returncode != 0:
                logger.error(f"Codex error: {result.stderr}")
                raise RuntimeError(f"Codex error: {result.stderr}")

            logger.info(f"✅ Codex completado en {elapsed:.1f}s")

            return {
                "status": "success",
                "agent": "codex",
                "duration": elapsed,
                "files_modified": [],
                "output": result.stdout,
                "suggestion": result.stdout,
            }

        except Exception as e:
            logger.error(f"❌ Error ejecutando Codex: {e}")
            raise

    async def _execute_with_jules(
        self, task: TaskDefinition, skills_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta tarea usando Jules AI agent.
        Delegado al MCP tool existente cde_delegateToJules.
        """
        from mcp_tools.agents import cde_delegateToJules

        prompt = self._build_prompt_with_context(task, skills_context)
        logger.info("🔄 Delegando a Jules...")

        result = await cde_delegateToJules(
            user_prompt=prompt, require_plan_approval=False, timeout=3600
        )

        try:
            result_json = json.loads(result)
            return {
                "status": result_json.get("state", "unknown"),
                "agent": "jules",
                "duration": result_json.get("duration", 0),
                "files_modified": result_json.get("modified_files", []),
                "session_id": result_json.get("session_id"),
                "output": result_json.get("log", ""),
            }
        except json.JSONDecodeError:
            return {"status": "completed", "agent": "jules", "output": result}

    def _build_prompt_with_context(
        self, task: TaskDefinition, skills_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construye un prompt enriquecido con contexto de skills."""
        skills_str = ""
        if skills_context:
            skills_str = "\n\n## Skills Disponibles:\n"
            for skill_name, skill_data in skills_context.items():
                if isinstance(skill_data, dict):
                    summary = skill_data.get("summary", "")
                    skills_str += f"- **{skill_name}**: {summary}\n"

        return f"""
# Tarea de Implementación

## Información de la Tarea
- **ID**: {task.task_id}
- **Título**: {task.title}
- **Fase**: {task.phase}
- **Complejidad**: {task.complexity}

## Descripción
{task.description}

## Criterios de Aceptación
{chr(10).join(f'- {c}' for c in task.acceptance_criteria)}

## Skills Necesarios
{chr(10).join(f'- {s}' for s in task.required_skills)}

{skills_str}

## Contexto del Proyecto
- **Path**: {self.project_path}
- **Lenguaje**: Python 3.14+ con Rust/PyO3
- **Arquitectura**: Hexagonal (Domain → Application → Adapters)
- **Estructura**: FastMCP MCP Server con orquestación de agentes

## Instrucciones
1. Entender completamente la tarea y criterios
2. Usar los skills disponibles como referencia
3. Seguir la arquitectura hexagonal del proyecto
4. Escribir tests para cualquier cambio
5. Actualizar documentación según governance
6. No hacer commits automáticos (Aider) ni push a Git

## Output Esperado
Descripción clara de:
1. Archivos modificados/creados
2. Tests agregados/actualizados
3. Documentación actualizada
4. Cualquier issue o bloqueador encontrado

---

Comienza la implementación:
"""

    def _find_relevant_files(self, task: TaskDefinition) -> List[str]:
        """Encuentra archivos relevantes para una tarea."""
        relevant = []

        # Basado en la fase de la tarea
        if task.phase == "implement":
            # Archivos de aplicación
            relevant.extend(self.project_path.glob("src/**/*.py"))
        elif task.phase == "test":
            # Archivos de tests
            relevant.extend(self.project_path.glob("tests/**/*.py"))
        elif task.phase == "document":
            # Archivos de documentación
            relevant.extend(self.project_path.glob("specs/**/*.md"))
            relevant.extend(self.project_path.glob("docs/**/*.md"))

        # Limitar a 10 archivos máximo (para no saturar al agente)
        return [str(f) for f in relevant[:10]]

    def _extract_modified_files(self, output: str) -> List[str]:
        """Extrae lista de archivos modificados del output del agente."""
        modified = []

        # Buscar patrones comunes
        for line in output.split("\n"):
            if any(
                x in line.lower()
                for x in ["modified:", "created:", "updated:", "wrote"]
            ):
                # Intenta extraer nombre de archivo
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        file_path = parts[-1].strip().strip("'\"")
                        if file_path and not file_path.startswith("//"):
                            modified.append(file_path)

        return list(set(modified))  # Remover duplicados

    async def orchestrate_phase1_verification(self) -> Dict[str, Any]:
        """
        Orquesta Fase 1: Verificación de Rust + Compilación.

        Tareas:
        1. Instalar Rust toolchain
        2. Compilar cde_rust_core
        3. Ejecutar tests
        4. Generar coverage report
        """
        tasks = [
            TaskDefinition(
                task_id="rust-install",
                title="Instalar Rust Toolchain",
                description="""
Instala Rust toolchain completo (rustc, cargo, rustup) en el sistema.

Pasos:
1. Detectar sistema operativo (Windows/Linux/macOS)
2. Descargar rustup según SO
3. Ejecutar instalación
4. Verificar: rustc --version, cargo --version
5. Documentar versiones instaladas
                """,
                phase="verify",
                complexity="simple",
                required_skills=["rust-installation", "system-administration"],
                estimated_hours=0.5,
                acceptance_criteria=[
                    "rustc --version devuelve 1.75+",
                    "cargo --version devuelve 1.75+",
                    "Archivo de versiones registrado",
                ],
            ),
            TaskDefinition(
                task_id="rust-compile",
                title="Compilar Núcleo Rust (cde_rust_core)",
                description="""
Compila el núcleo Rust con PyO3 usando maturin.

Comandos:
```bash
cd rust_core
maturin develop --release
```

Validación:
```python
import cde_rust_core
result = cde_rust_core.scan_documentation_py(".")
print(f"✅ Compuesto correctamente: {len(result)} bytes")
```
                """,
                phase="verify",
                complexity="simple",
                required_skills=["rust-compilation", "pyo3-integration"],
                estimated_hours=0.25,
                acceptance_criteria=[
                    "No errores de compilación",
                    "cde_rust_core se importa sin excepciones",
                    "scan_documentation_py devuelve JSON válido",
                ],
            ),
            TaskDefinition(
                task_id="run-all-tests",
                title="Ejecutar Suite Completa de Tests",
                description="""
Ejecuta todos los tests y verifica que pasen sin skipped.

```bash
pytest tests/ -v --tb=short
```

Esperado: 23+ tests pasando, 0 skipped
                """,
                phase="test",
                complexity="simple",
                required_skills=["pytest", "testing"],
                estimated_hours=0.25,
                acceptance_criteria=[
                    "pytest ejecuta sin errores",
                    "0 tests skipped",
                    "Todos los tests pasando",
                ],
            ),
            TaskDefinition(
                task_id="coverage-report",
                title="Generar Coverage Report",
                description="""
Genera reporte de cobertura y valida que sea >85%.

```bash
pytest --cov=src/cde_orchestrator --cov-report=html --cov-report=term-missing
```

Expected: Coverage >85%
                """,
                phase="verify",
                complexity="simple",
                required_skills=["pytest", "coverage-analysis"],
                estimated_hours=0.25,
                acceptance_criteria=[
                    "Coverage >85%",
                    "HTML report generado en htmlcov/",
                    "Reporte mínimo registrado",
                ],
            ),
        ]

        results = {}
        for task in tasks:
            try:
                result = await self.execute_task(task)
                results[task.task_id] = result
            except Exception as e:
                logger.error(f"Error en tarea {task.task_id}: {e}")
                results[task.task_id] = {"status": "failed", "error": str(e)}

        return results

    def get_execution_summary(self) -> Dict[str, Any]:
        """Devuelve resumen de ejecución."""
        total_tasks = len(self.execution_log)
        successful = sum(1 for t in self.execution_log if t.get("status") == "success")
        failed = total_tasks - successful
        total_time = sum(t.get("duration", 0) for t in self.execution_log)

        return {
            "total_tasks": total_tasks,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_tasks * 100) if total_tasks > 0 else 0,
            "total_time_seconds": total_time,
            "execution_log": self.execution_log,
            "context_stack": self.context_stack,
        }


async def main():
    """Ejemplo de uso: Ejecutar Fase 1 con orquestación multi-agente."""
    logger.basicConfig(level=logging.INFO)

    # Inicializar orquestador
    orchestrator = MultiAgentOrchestrator(".")

    # Mostrar agentes disponibles
    logger.info(f"Agentes disponibles: {list(orchestrator.agent_capabilities.keys())}")

    # Ejecutar Fase 1
    logger.info("🚀 Iniciando Fase 1: Verificación y Compilación")
    results = await orchestrator.orchestrate_phase1_verification()

    # Mostrar resumen
    summary = orchestrator.get_execution_summary()
    logger.info(
        f"✅ Fase 1 completada: {summary['successful']}/{summary['total_tasks']} tareas exitosas"
    )
    logger.info(f"⏱️  Tiempo total: {summary['total_time_seconds']:.1f}s")

    return summary


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
