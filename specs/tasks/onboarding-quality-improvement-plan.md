---
title: "Plan de Mejora: Sistema de Onboarding - Generación de Archivos Ricos en Contexto"
description: "Plan completo para transformar el onboarding de templates genéricos a documentación rica en contexto automático"
type: task
status: active
created: "2025-01-23"
updated: "2025-01-23"
author: "GitHub Copilot - Análisis Detallado"
tags:
  - onboarding
  - ai-config
  - documentation-quality
  - context-enrichment
  - metadata
priority: high
estimated_effort: "3-5 días"
llm_summary: |
  Plan para mejorar el sistema de onboarding que actualmente genera archivos pobres (AGENTS.md, copilot-instructions.md).
  Implementa ProjectContextEnricher, GitHistoryAnalyzer, DocumentationSynthesizer, y FrameworkDetector
  para reemplazar templates genéricos con contexto real del proyecto.
---

# Plan de Mejora: Sistema de Onboarding

## 🎯 Problema Identificado

**Reporte del Usuario**:
> "use el onboarding y genero unos archivos de agentes y copilot instruccion muy pobres de rules y contextos del proyecto"

**Evidencia Técnica**:
- ✅ AGENTS.md actual (1232 líneas): **Rico en contexto** (escrito manualmente)
- ✅ .github/copilot-instructions.md actual (1014 líneas): **Rico en contexto** (escrito manualmente)
- ❌ Templates del sistema (`_get_agents_md_template`): **Genéricos con placeholders**
- ❌ ProjectAnalysisUseCase: **Análisis superficial** (solo cuenta archivos)

**Quality Score Actual**: 64.1/100

**Problemas Detectados**:
1. 📊 **156 archivos sin metadata YAML** (71% del total)
2. 🔗 **78 enlaces rotos** en la documentación
3. 📝 **Templates no usan análisis de proyecto**
4. 🧠 **Falta Git history analysis**
5. 📚 **No lee documentación existente**
6. 🏗️ **No detecta arquitectura real del código**

---

## 🔍 Análisis Comparativo

### Template Actual (Genérico) ❌

```markdown
## 🎯 Project Overview

What: [Brief description of what this project does]  # ❌ PLACEHOLDER
Architecture: [Architecture pattern used]            # ❌ PLACEHOLDER
Language: [Primary language and version]             # ❌ PLACEHOLDER
```

**Problemas**:
- Placeholders no son reemplazados
- No usa datos del análisis de proyecto
- Sin ejemplos de comandos reales
- Sin contexto de arquitectura
- Sin información de Git history

### Archivo Manual (Rico) ✅

```markdown
## 🎯 Project Overview

**What**: Nexus AI (formerly CDE Orchestrator) is an **AI CEO** system that manages software development.
**Role**: It acts as your manager. You are the "Employee" agent.
**Architecture**: Hexagonal (Ports & Adapters) / Clean Architecture + LLM-First Documentation
**Language**: Python 3.14, FastMCP framework

**🆕 NEW**: Nexus AI now acts as your **intelligent orchestrator** - you interact with it via MCP tools, and it:
1.  Analyzes your requests and selects optimal workflows automatically
2.  Downloads and updates skills from external repositories
3.  Performs web research to keep knowledge current
4.  Manages documentation following Spec-Kit governance
```

**Fortalezas**:
- ✅ Contexto específico del proyecto
- ✅ Descripción clara de arquitectura
- ✅ Stack tecnológico específico (Python 3.14, FastMCP)
- ✅ Funcionalidades concretas
- ✅ Flujo de trabajo explicado

---

## 🏗️ Arquitectura Propuesta

### 1. ProjectContextEnricher (Nuevo)

**Responsabilidad**: Enriquecer análisis básico con contexto profundo

```python
# src/cde_orchestrator/application/onboarding/project_context_enricher.py

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class EnrichedProjectContext:
    """Contexto enriquecido del proyecto."""

    # Análisis básico (ya existe)
    file_count: int
    language_stats: Dict[str, int]
    dependency_files: List[str]

    # Git insights (nuevo)
    git_insights: Dict[str, Any]
    recent_commits: List[Dict[str, str]]
    active_branches: List[str]
    main_contributors: List[str]

    # Documentación sintetizada (nuevo)
    architecture_description: str
    tech_stack: List[str]
    build_commands: List[str]
    test_commands: List[str]
    coding_conventions: List[str]

    # Framework detection (nuevo)
    detected_frameworks: List[str]
    architecture_pattern: str  # "Hexagonal", "Clean", "MVC", etc.
    project_type: str  # "web-app", "api", "library", "mcp-server", etc.

    # Code patterns (nuevo)
    common_imports: List[str]
    class_hierarchies: List[str]
    naming_patterns: str


class ProjectContextEnricher:
    """
    Enriquece el análisis básico con contexto profundo.

    Integra:
    - GitHistoryAnalyzer: Historia de commits, branches, contribuciones
    - DocumentationSynthesizer: README, CONTRIBUTING, docs/
    - FrameworkDetector: Next.js, FastAPI, Django, FastMCP, etc.
    - CodePatternExtractor: Imports comunes, jerarquías de clases
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.git_analyzer = GitHistoryAnalyzer(project_path)
        self.doc_synthesizer = DocumentationSynthesizer(project_path)
        self.framework_detector = FrameworkDetector(project_path)
        self.code_extractor = CodePatternExtractor(project_path)

    async def enrich(self, basic_analysis: Dict[str, Any]) -> EnrichedProjectContext:
        """
        Transforma análisis superficial en contexto rico.

        Args:
            basic_analysis: Output de ProjectAnalysisUseCase._execute_rust

        Returns:
            EnrichedProjectContext con toda la información necesaria
        """
        logger.info("Starting context enrichment")

        # Análisis de Git (5-10ms con gitpython)
        git_insights = await self.git_analyzer.analyze()

        # Síntesis de documentación (10-20ms)
        docs = await self.doc_synthesizer.synthesize()

        # Detección de frameworks (5ms)
        frameworks = await self.framework_detector.detect()

        # Extracción de patrones de código (50ms con Rust o 200ms con Python)
        patterns = await self.code_extractor.extract()

        return EnrichedProjectContext(
            # Básico
            file_count=basic_analysis["file_count"],
            language_stats=basic_analysis["language_stats"],
            dependency_files=basic_analysis["dependency_files"],

            # Git
            git_insights=git_insights,
            recent_commits=git_insights.get("recent_commits", []),
            active_branches=git_insights.get("branches", []),
            main_contributors=git_insights.get("contributors", []),

            # Docs
            architecture_description=docs.get("architecture", "Not documented"),
            tech_stack=docs.get("tech_stack", []),
            build_commands=docs.get("build_commands", []),
            test_commands=docs.get("test_commands", []),
            coding_conventions=docs.get("conventions", []),

            # Frameworks
            detected_frameworks=frameworks.get("frameworks", []),
            architecture_pattern=frameworks.get("architecture_pattern", "Unknown"),
            project_type=frameworks.get("project_type", "unknown"),

            # Patterns
            common_imports=patterns.get("imports", []),
            class_hierarchies=patterns.get("hierarchies", []),
            naming_patterns=patterns.get("naming", ""),
        )
```

### 2. GitHistoryAnalyzer (Nuevo)

**Responsabilidad**: Extraer insights de la historia de Git

```python
# src/cde_orchestrator/application/onboarding/git_history_analyzer.py

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from git import Repo, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class GitInsights:
    """Insights extraídos del repositorio Git."""

    recent_commits: List[Dict[str, str]]  # {"hash": "abc123", "message": "feat: ...", "author": "..."}
    branches: List[str]
    contributors: List[str]
    commit_frequency: str  # "Very active", "Moderate", "Low"
    architectural_decisions: List[str]  # Commits con "refactor", "architecture", etc.


class GitHistoryAnalyzer:
    """
    Analiza la historia de Git para extraer contexto del proyecto.

    - Commits recientes (últimos 30)
    - Branches activos
    - Principales contribuidores
    - Decisiones arquitectónicas (commits de refactor)
    - Frecuencia de desarrollo
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.repo_path = self._find_git_root()

    def _find_git_root(self) -> Optional[Path]:
        """Busca el directorio .git recursivamente hacia arriba."""
        current = self.project_path
        while current != current.parent:
            git_dir = current / ".git"
            if git_dir.exists():
                return current
            current = current.parent
        return None

    async def analyze(self) -> Dict[str, Any]:
        """
        Analiza el repositorio Git.

        Returns:
            Dict con insights de Git
        """
        if not GIT_AVAILABLE:
            logger.warning("GitPython not available, skipping Git analysis")
            return self._empty_insights()

        if not self.repo_path:
            logger.info("Not a Git repository, skipping Git analysis")
            return self._empty_insights()

        try:
            repo = Repo(self.repo_path)

            # Commits recientes (últimos 30 días)
            recent_commits = self._get_recent_commits(repo, days=30)

            # Branches
            branches = [b.name for b in repo.branches]

            # Contribuidores
            contributors = self._get_contributors(repo)

            # Frecuencia de commits
            commit_frequency = self._calculate_frequency(recent_commits)

            # Decisiones arquitectónicas
            arch_decisions = self._find_architectural_commits(recent_commits)

            return {
                "recent_commits": recent_commits,
                "branches": branches,
                "contributors": contributors,
                "commit_frequency": commit_frequency,
                "architectural_decisions": arch_decisions,
            }

        except GitCommandError as e:
            logger.error(f"Git command failed: {e}")
            return self._empty_insights()

    def _get_recent_commits(self, repo: Repo, days: int = 30) -> List[Dict[str, str]]:
        """Obtiene commits de los últimos N días."""
        cutoff_date = datetime.now() - timedelta(days=days)
        commits = []

        try:
            for commit in list(repo.iter_commits('HEAD', max_count=100)):
                commit_date = datetime.fromtimestamp(commit.committed_date)
                if commit_date < cutoff_date:
                    break

                commits.append({
                    "hash": commit.hexsha[:7],
                    "message": commit.message.strip().split('\n')[0],  # Primera línea
                    "author": commit.author.name,
                    "date": commit_date.strftime("%Y-%m-%d"),
                })

        except Exception as e:
            logger.error(f"Error reading commits: {e}")

        return commits

    def _get_contributors(self, repo: Repo) -> List[str]:
        """Obtiene lista de contribuidores únicos."""
        contributors = set()
        try:
            for commit in list(repo.iter_commits('HEAD', max_count=100)):
                contributors.add(commit.author.name)
        except Exception as e:
            logger.error(f"Error reading contributors: {e}")

        return sorted(list(contributors))

    def _calculate_frequency(self, commits: List[Dict[str, str]]) -> str:
        """Calcula frecuencia de desarrollo."""
        if len(commits) > 20:
            return "Very active"
        elif len(commits) > 10:
            return "Moderate"
        else:
            return "Low"

    def _find_architectural_commits(self, commits: List[Dict[str, str]]) -> List[str]:
        """Encuentra commits relacionados con arquitectura."""
        keywords = ["refactor", "architecture", "redesign", "restructure", "migration"]
        arch_commits = []

        for commit in commits:
            message = commit["message"].lower()
            if any(keyword in message for keyword in keywords):
                arch_commits.append(f"{commit['hash']}: {commit['message']}")

        return arch_commits

    def _empty_insights(self) -> Dict[str, Any]:
        """Retorna insights vacíos cuando Git no está disponible."""
        return {
            "recent_commits": [],
            "branches": [],
            "contributors": [],
            "commit_frequency": "Unknown",
            "architectural_decisions": [],
        }
```

### 3. DocumentationSynthesizer (Nuevo)

**Responsabilidad**: Leer y sintetizar documentación existente

```python
# src/cde_orchestrator/application/onboarding/documentation_synthesizer.py

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DocumentationSynthesizer:
    """
    Lee y sintetiza documentación existente del proyecto.

    - README.md: Descripción general, stack tecnológico, comandos
    - CONTRIBUTING.md: Convenciones de código, workflow
    - docs/: Arquitectura, guías técnicas
    - pyproject.toml, package.json: Dependencias y scripts
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path

    async def synthesize(self) -> Dict[str, Any]:
        """
        Sintetiza toda la documentación del proyecto.

        Returns:
            Dict con información extraída de documentación
        """
        result = {
            "architecture": "",
            "tech_stack": [],
            "build_commands": [],
            "test_commands": [],
            "conventions": [],
        }

        # Leer README.md
        readme_path = self.project_path / "README.md"
        if readme_path.exists():
            readme_content = readme_path.read_text(encoding="utf-8")
            result["architecture"] = self._extract_architecture(readme_content)
            result["tech_stack"].extend(self._extract_tech_stack(readme_content))
            result["build_commands"].extend(self._extract_commands(readme_content, "build"))
            result["test_commands"].extend(self._extract_commands(readme_content, "test"))

        # Leer CONTRIBUTING.md
        contributing_path = self.project_path / "CONTRIBUTING.md"
        if contributing_path.exists():
            contrib_content = contributing_path.read_text(encoding="utf-8")
            result["conventions"].extend(self._extract_conventions(contrib_content))

        # Leer pyproject.toml o package.json
        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            pyproject_content = pyproject_path.read_text(encoding="utf-8")
            result["tech_stack"].extend(self._extract_dependencies_toml(pyproject_content))

        package_json_path = self.project_path / "package.json"
        if package_json_path.exists():
            import json
            try:
                package_data = json.loads(package_json_path.read_text(encoding="utf-8"))
                result["tech_stack"].extend(self._extract_dependencies_json(package_data))
                result["build_commands"].extend(self._extract_scripts(package_data, "build"))
                result["test_commands"].extend(self._extract_scripts(package_data, "test"))
            except json.JSONDecodeError:
                logger.warning("Failed to parse package.json")

        return result

    def _extract_architecture(self, content: str) -> str:
        """Extrae descripción de arquitectura del README."""
        # Buscar secciones comunes de arquitectura
        patterns = [
            r"## Architecture\n\n([^\n#]+)",
            r"## Design\n\n([^\n#]+)",
            r"\*\*Architecture\*\*: ([^\n]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Not documented"

    def _extract_tech_stack(self, content: str) -> List[str]:
        """Extrae stack tecnológico del README."""
        stack = []

        # Patrones comunes
        tech_patterns = [
            r"Python\s+([\d.]+)",
            r"Node\.js\s+([\d.]+)",
            r"TypeScript",
            r"React",
            r"Next\.js",
            r"FastAPI",
            r"Django",
            r"Flask",
            r"FastMCP",
        ]

        for pattern in tech_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                stack.append(pattern.replace(r"\.", ".").replace(r"\s+", " "))

        return stack

    def _extract_commands(self, content: str, command_type: str) -> List[str]:
        """Extrae comandos de build/test del README."""
        commands = []

        # Buscar bloques de código con comandos
        code_blocks = re.findall(r"```(?:bash|sh|shell)?\n(.*?)```", content, re.DOTALL)

        for block in code_blocks:
            if command_type.lower() in block.lower():
                lines = block.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.strip().startswith('#'):
                        commands.append(line.strip())

        return commands

    def _extract_conventions(self, content: str) -> List[str]:
        """Extrae convenciones de código de CONTRIBUTING."""
        conventions = []

        # Buscar secciones de código style
        patterns = [
            r"## Code Style\n\n(.*?)(?=\n##|\Z)",
            r"## Coding Conventions\n\n(.*?)(?=\n##|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section = match.group(1)
                # Extraer bullets
                bullets = re.findall(r"- (.+)", section)
                conventions.extend(bullets)

        return conventions

    def _extract_dependencies_toml(self, content: str) -> List[str]:
        """Extrae dependencias principales de pyproject.toml."""
        deps = []

        # Buscar sección de dependencies
        match = re.search(r"\[project\.dependencies\].*?\[(.*?)\]", content, re.DOTALL)
        if match:
            dep_section = match.group(1)
            # Extraer nombres de paquetes
            deps_found = re.findall(r'"([a-zA-Z0-9_-]+)[>=<]', dep_section)
            deps.extend(deps_found[:10])  # Top 10

        return deps

    def _extract_dependencies_json(self, data: Dict[str, Any]) -> List[str]:
        """Extrae dependencias principales de package.json."""
        deps = []

        if "dependencies" in data:
            deps.extend(list(data["dependencies"].keys())[:10])  # Top 10

        return deps

    def _extract_scripts(self, data: Dict[str, Any], script_type: str) -> List[str]:
        """Extrae scripts de build/test de package.json."""
        scripts = []

        if "scripts" in data:
            for name, command in data["scripts"].items():
                if script_type.lower() in name.lower():
                    scripts.append(f"npm run {name}")

        return scripts
```

### 4. FrameworkDetector (Nuevo)

**Responsabilidad**: Detectar frameworks y patrones arquitectónicos

```python
# src/cde_orchestrator/application/onboarding/framework_detector.py

import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """
    Detecta frameworks, bibliotecas y patrones arquitectónicos.

    - Web: Next.js, React, Vue, Angular
    - Backend: FastAPI, Django, Flask, Express
    - MCP: FastMCP
    - Architecture: Hexagonal, Clean, MVC, MVVM
    """

    FRAMEWORK_SIGNATURES = {
        # Python
        "FastAPI": ["from fastapi import", "fastapi"],
        "Django": ["from django", "django.conf"],
        "Flask": ["from flask import", "Flask(__name__)"],
        "FastMCP": ["from mcp import", "FastMCP"],

        # JavaScript/TypeScript
        "Next.js": ["next.config", "pages/", "app/"],
        "React": ["react", "react-dom"],
        "Vue": ["vue", "@vue/"],
        "Express": ["express"],

        # Architecture patterns
        "Hexagonal": ["domain/", "application/", "adapters/", "ports"],
        "Clean Architecture": ["entities.py", "use_cases", "gateways"],
    }

    def __init__(self, project_path: Path):
        self.project_path = project_path

    async def detect(self) -> Dict[str, Any]:
        """
        Detecta frameworks y patrones.

        Returns:
            Dict con frameworks detectados
        """
        detected = {
            "frameworks": [],
            "architecture_pattern": "Unknown",
            "project_type": "unknown",
        }

        # Detectar por archivos de configuración
        if (self.project_path / "next.config.js").exists():
            detected["frameworks"].append("Next.js")
            detected["project_type"] = "web-app"

        if (self.project_path / "pyproject.toml").exists():
            toml_content = (self.project_path / "pyproject.toml").read_text()
            if "fastapi" in toml_content.lower():
                detected["frameworks"].append("FastAPI")
                detected["project_type"] = "api"
            if "fastmcp" in toml_content.lower():
                detected["frameworks"].append("FastMCP")
                detected["project_type"] = "mcp-server"

        # Detectar arquitectura por estructura de directorios
        src_path = self.project_path / "src"
        if src_path.exists():
            dirs = [d.name for d in src_path.iterdir() if d.is_dir()]
            if "domain" in dirs and "application" in dirs and "adapters" in dirs:
                detected["architecture_pattern"] = "Hexagonal (Ports & Adapters)"
            elif "entities" in dirs and "use_cases" in dirs:
                detected["architecture_pattern"] = "Clean Architecture"

        return detected
```

### 5. AIConfigUseCase (Actualizado)

**Modificación**: Usar `ProjectContextEnricher` para generar templates dinámicos

```python
# src/cde_orchestrator/application/ai_config/ai_config_use_case.py (modificado)

def _get_agents_md_template(self, project_name: str, context: EnrichedProjectContext) -> str:
    """
    Genera AGENTS.md con contexto real del proyecto.

    Args:
        project_name: Nombre del proyecto
        context: Contexto enriquecido del proyecto

    Returns:
        Content para AGENTS.md
    """
    # Stack tecnológico
    tech_stack_str = ", ".join(context.tech_stack[:5]) if context.tech_stack else "Not detected"

    # Comandos de build/test
    build_commands_str = "\n".join([f"# {cmd}" for cmd in context.build_commands[:3]]) or "# (Add your build command)"
    test_commands_str = "\n".join([f"# {cmd}" for cmd in context.test_commands[:3]]) or "# (Add your test command)"

    # Git activity
    commit_activity = f"{len(context.recent_commits)} commits in last 30 days ({context.git_insights.get('commit_frequency', 'Unknown')})"

    return f"""# {project_name} - Agent Instructions

> Format: AGENTS.md (OpenAI Standard)
> Target: AI Coding Agents (Cursor, Windsurf, Aider, Bolt, etc.)
> Last Updated: Auto-generated during onboarding
> Priority: High-level guidelines and project navigation

---
## 🎯 Project Overview

What: {context.architecture_description}
Scale: {context.file_count} files across {len(context.language_stats)} languages
Architecture: {context.architecture_pattern}
Tech Stack: {tech_stack_str}
Project Type: {context.project_type}

---
## 📁 Quick Navigation

### Start Here (First-time agents)
1. Check `README.md` for project overview
2. Review `CONTRIBUTING.md` for coding conventions
3. See Git history: {commit_activity}

### Core Directories
```
src/                 # Source code
tests/               # Test suites
```

---
## 🛠️ Development Workflow

### Build Commands
```bash
{build_commands_str}
```

### Test Commands
```bash
{test_commands_str}
```

---
## 📊 Recent Activity

**Git Insights**:
- Active branches: {", ".join(context.active_branches[:3])}
- Main contributors: {", ".join(context.main_contributors[:3])}
- {commit_activity}

**Recent Architectural Decisions**:
{chr(10).join([f"- {decision}" for decision in context.git_insights.get('architectural_decisions', [])[:3]]) or "- No major refactorings detected"}

---
## 🎨 Code Conventions

{chr(10).join([f"- {conv}" for conv in context.coding_conventions[:5]]) or "- Follow language-specific best practices"}

---
For detailed GitHub Copilot instructions: see `.github/copilot-instructions.md`
For Google AI Studio (Gemini) instructions: see `GEMINI.md` (if using Gemini)
"""
```

---

## 📋 Plan de Implementación

### Fase 1: Análisis Profundo ✅ COMPLETADO

- [x] Analizar templates actuales
- [x] Comparar con archivos manuales
- [x] Identificar gaps de información
- [x] Documentar arquitectura propuesta

### Fase 2: Implementación Core (3 días)

#### Día 1: GitHistoryAnalyzer
- [ ] Crear `src/cde_orchestrator/application/onboarding/git_history_analyzer.py`
- [ ] Implementar análisis de commits (últimos 30 días)
- [ ] Implementar detección de branches activos
- [ ] Implementar análisis de contribuidores
- [ ] Tests unitarios para GitHistoryAnalyzer

#### Día 2: DocumentationSynthesizer + FrameworkDetector
- [ ] Crear `src/cde_orchestrator/application/onboarding/documentation_synthesizer.py`
- [ ] Implementar lectura de README.md
- [ ] Implementar lectura de CONTRIBUTING.md
- [ ] Implementar extracción de comandos
- [ ] Crear `src/cde_orchestrator/application/onboarding/framework_detector.py`
- [ ] Implementar detección de frameworks comunes
- [ ] Tests unitarios para ambos

#### Día 3: ProjectContextEnricher + Integración
- [ ] Crear `src/cde_orchestrator/application/onboarding/project_context_enricher.py`
- [ ] Integrar GitHistoryAnalyzer, DocumentationSynthesizer, FrameworkDetector
- [ ] Modificar `AIConfigUseCase._get_agents_md_template` para usar contexto enriquecido
- [ ] Modificar `AIConfigUseCase._get_copilot_instructions_template`
- [ ] Tests de integración end-to-end

### Fase 3: Validación y Mejoras de Calidad (2 días)

#### Día 4: Pruebas con Proyectos Reales
- [ ] Ejecutar `cde_onboardingProject` en CDE Orchestrator
- [ ] Comparar output con archivos manuales actuales
- [ ] Ajustar templates según feedback
- [ ] Ejecutar en 3-5 proyectos de prueba adicionales

#### Día 5: Limpieza de Documentación
- [ ] Usar MCP tools para agregar metadata a 156 archivos faltantes
- [ ] Reparar 78 enlaces rotos
- [ ] Mejorar Quality Score de 64.1 a 85+
- [ ] Actualizar índices y referencias cruzadas

---

## 🎯 Métricas de Éxito

### Before (Estado Actual)
- ❌ Quality Score: 64.1/100
- ❌ 156 archivos sin metadata (71%)
- ❌ 78 enlaces rotos
- ❌ Templates genéricos con placeholders
- ❌ Análisis superficial (solo cuenta archivos)

### After (Objetivo)
- ✅ Quality Score: 85+/100
- ✅ 0 archivos sin metadata
- ✅ 0 enlaces rotos
- ✅ Templates dinámicos con contexto real
- ✅ Análisis profundo (Git + Docs + Frameworks + Código)

### KPIs de Calidad de AGENTS.md Generado
- ✅ Descripción específica del proyecto (no placeholder)
- ✅ Stack tecnológico detectado automáticamente
- ✅ Comandos de build/test extraídos de docs
- ✅ Arquitectura identificada (Hexagonal, Clean, etc.)
- ✅ Git insights incluidos (commits, branches, contributors)
- ✅ Convenciones de código extraídas de CONTRIBUTING.md

---

## 🚀 Próximos Pasos Inmediatos

1. **Crear GitHistoryAnalyzer** (1 día)
   - Usar GitPython para análisis de repositorio
   - Extraer commits, branches, contributors
   - Identificar decisiones arquitectónicas

2. **Crear DocumentationSynthesizer** (1 día)
   - Leer README.md, CONTRIBUTING.md
   - Extraer comandos, convenciones, tech stack
   - Parsear pyproject.toml / package.json

3. **Crear FrameworkDetector** (0.5 días)
   - Detectar frameworks comunes
   - Identificar patrones arquitectónicos
   - Clasificar tipo de proyecto

4. **Integrar en ProjectContextEnricher** (0.5 días)
   - Orquestar los 3 analizadores nuevos
   - Combinar con análisis básico existente
   - Retornar `EnrichedProjectContext`

5. **Actualizar AIConfigUseCase** (1 día)
   - Modificar `_get_agents_md_template` para usar contexto
   - Modificar `_get_copilot_instructions_template`
   - Eliminar todos los placeholders
   - Generar ejemplos reales de comandos

6. **Validar con CDE Orchestrator** (1 día)
   - Ejecutar onboarding en este proyecto
   - Comparar con AGENTS.md manual actual
   - Iterar hasta alcanzar calidad similar

---

## 📖 Referencias

- **Archivos Clave Actuales**:
  - `AGENTS.md` (1232 líneas) - Ejemplo de calidad objetivo
  - `.github/copilot-instructions.md` (1014 líneas) - Ejemplo de calidad objetivo
  - `src/cde_orchestrator/application/ai_config/ai_config_use_case.py` - Sistema actual
  - `src/cde_orchestrator/application/onboarding/project_analysis_use_case.py` - Análisis actual

- **Documentación de Diseño**:
  - `specs/design/onboarding-system-redesign.md` - Diseño anterior
  - `specs/features/onboarding-system.md` - Feature spec
  - `specs/governance/DOCUMENTATION_GOVERNANCE.md` - Reglas de documentación

- **Herramientas MCP Relevantes**:
  - `cde_onboardingProject` - Entry point del sistema
  - `cde_scanDocumentation` - Para análisis de documentación
  - `cde_analyzeDocumentation` - Para quality score

---

**Autor**: GitHub Copilot - Análisis Detallado
**Fecha**: 2025-01-23
**Estimación**: 3-5 días de trabajo
**Prioridad**: ALTA - Mejora crítica de calidad
