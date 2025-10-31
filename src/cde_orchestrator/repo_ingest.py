"""
Lightweight repository ingestion utilities inspired by gitingest.
Provides a small digest (tree, top files, content snippets) suitable to include in
LLM prompts. Non-invasive: does not write files or modify repo.
"""
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pathspec import PathSpec
except ImportError:  # pragma: no cover
    PathSpec = None

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """Rough token estimate: chars / 4 (safe heuristic)."""
    if not text:
        return 0
    return max(1, int(len(text) / 4))


class RepoIngestor:
    def __init__(self, project_root: Path, include_gitignored: bool = False):
        self.project_root = Path(project_root)
        self.include_gitignored = include_gitignored
        self._gitignore_spec = self._load_gitignore()
        self._cache: Optional[Dict[str, Any]] = None

    def _load_gitignore(self) -> Optional[PathSpec]:
        """Load root .gitignore patterns for fallback scanning."""
        gitignore_path = self.project_root / ".gitignore"
        patterns: List[str] = []

        if gitignore_path.exists():
            try:
                for line in gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        patterns.append(stripped)
            except Exception as exc:
                logger.debug("Failed to read .gitignore: %s", exc)

        info_exclude = self.project_root / ".git" / "info" / "exclude"
        if info_exclude.exists():
            try:
                for line in info_exclude.read_text(encoding="utf-8", errors="ignore").splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        patterns.append(stripped)
            except Exception as exc:
                logger.debug("Failed to read git info exclude: %s", exc)

        if not patterns or PathSpec is None:
            if PathSpec is None:
                logger.debug("pathspec not installed; skipping gitignore support")
            return None

        try:
            return PathSpec.from_lines("gitwildmatch", patterns)
        except Exception as exc:
            logger.warning("Could not compile gitignore patterns: %s", exc)
            return None

    def _git_ls_files(self) -> List[Path]:
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            files = [self.project_root / p for p in result.stdout.splitlines() if p]
            return files
        except Exception as exc:
            logger.debug("git ls-files failed, falling back to filesystem scan: %s", exc)
            # Fallback: walk filesystem
            files = [p for p in self.project_root.rglob("*") if p.is_file()]
            if not self.include_gitignored:
                filtered: List[Path] = []
                for path in files:
                    rel = path.relative_to(self.project_root)
                    if ".git" in rel.parts:
                        continue
                    if str(rel).endswith("~"):
                        continue
                    if self._gitignore_spec and self._gitignore_spec.match_file(str(rel)):
                        continue
                    filtered.append(path)
                files = filtered
            return files

    @staticmethod
    def _is_binary(path: Path) -> bool:
        try:
            with path.open("rb") as fh:
                chunk = fh.read(4096)
            if not chunk:
                return False
            if b"\0" in chunk:
                return True
            try:
                chunk.decode("utf-8")
            except UnicodeDecodeError:
                return True
            return False
        except Exception:
            return True

    def ingest(self, max_files: int = 200, max_snippet_chars: int = 2000, force_refresh: bool = False) -> Dict[str, Any]:
        """Return a small digest of the repo for prompting.

        Returns:
            {
              'summary': str,
              'tree': [{'path': 'src/foo.py','size': 123, 'lines': 10}, ...],
              'top_files': [{'path':..., 'snippet': 'first 200 chars'}...]
            }
        """
        if self._cache and not force_refresh:
            return self._cache

        files = self._git_ls_files()

        # filter out binary-like and very large files
        file_infos: List[Dict[str, Any]] = []
        for f in files:
            try:
                size = f.stat().st_size
                # skip huge files
                if size > 1024 * 1024:  # 1MB
                    continue
                if self._is_binary(f):
                    continue
                # read text safely
                text = f.read_text(encoding='utf-8', errors='ignore')
                lines = text.count('\n') + 1
                tokens = estimate_tokens(text)
                file_infos.append({'path': str(f.relative_to(self.project_root)), 'size': size, 'lines': lines, 'text': text, 'tokens': tokens})
            except Exception:
                continue

        # sort by size desc and pick top N
        file_infos.sort(key=lambda x: x['size'], reverse=True)
        top = file_infos[:min(len(file_infos), max_files)]

        top_files = []
        for fi in top[:20]:
            snippet = fi['text'][:max_snippet_chars]
            top_files.append({'path': fi['path'], 'size': fi['size'], 'lines': fi['lines'], 'tokens': fi.get('tokens', 0), 'snippet': snippet})

        # create a compact tree summary
        tree = [{'path': fi['path'], 'size': fi['size'], 'lines': fi['lines'], 'tokens': fi.get('tokens', 0)} for fi in top[:100]]

        # short summary
        summary_lines = [f"Files analyzed: {len(file_infos)}"]
        languages = set()
        for fi in file_infos:
            suffix = Path(fi['path']).suffix.lower().lstrip('.')
            if suffix:
                languages.add(suffix)
        if languages:
            summary_lines.append(f"Detected file extensions: {', '.join(sorted(list(languages))[:10])}")

        # token totals
        total_tokens = sum(fi.get('tokens', 0) for fi in file_infos)
        summary_lines.append(f"Estimated tokens (repo): {total_tokens}")

        # timestamp
        summary_lines.append(f"Generated at: {datetime.utcnow().isoformat()}Z")

        summary = " | ".join(summary_lines)

        digest = {'summary': summary, 'tree': tree, 'top_files': top_files, 'total_tokens': total_tokens}
        self._cache = digest
        return digest

    def export_digest(self, dest: Optional[str] = 'specs', filename: str = 'repo_digest.json') -> Path:
        """Export a JSON digest to either 'specs' or '.specs' directory under project root.

        Returns the path written.
        """
        dest_dir = self.project_root / (dest or 'specs')
        dest_dir.mkdir(parents=True, exist_ok=True)
        digest = self.ingest()
        out = dest_dir / filename
        out.write_text(json.dumps(digest, indent=2), encoding='utf-8')
        return out
