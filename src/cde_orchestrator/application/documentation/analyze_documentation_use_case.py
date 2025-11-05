"""
Analyze Documentation Use Case - Deep analysis with recommendations.

Provides detailed insights about documentation quality and structure.
"""

import re
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict


class AnalyzeDocumentationUseCase:
    """
    Deep analysis of documentation quality and structure.

    Analyzes:
    - Link integrity (broken internal links)
    - Document relationships
    - Metadata consistency
    - Content quality indicators
    - Duplication detection
    """

    def execute(self, project_path: str) -> Dict[str, Any]:
        """
        Perform deep documentation analysis.

        Args:
            project_path: Root path of project

        Returns:
            Dict with analysis including:
                - link_analysis: Broken/valid links
                - metadata_analysis: Consistency checks
                - quality_score: Overall quality rating
                - issues: List of problems found
                - suggestions: Actionable improvements
        """
        project = Path(project_path)

        if not project.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        # Find all markdown files
        md_files = list(project.rglob("*.md"))
        excluded_dirs = {".git", ".venv", "node_modules", "venv", "__pycache__"}
        md_files = [
            f for f in md_files
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]

        results = {
            "total_analyzed": len(md_files),
            "link_analysis": self._analyze_links(md_files, project),
            "metadata_analysis": self._analyze_metadata(md_files),
            "quality_indicators": self._analyze_quality(md_files),
            "issues": [],
            "suggestions": [],
            "quality_score": 0.0,
        }

        # Calculate quality score
        results["quality_score"] = self._calculate_quality_score(results)

        # Generate issues and suggestions
        results["issues"] = self._generate_issues(results)
        results["suggestions"] = self._generate_suggestions(results)

        return results

    def _analyze_links(self, md_files: List[Path], project: Path) -> Dict[str, Any]:
        """Analyze internal links between documents."""
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

        total_links = 0
        broken_links = []
        valid_links = 0
        external_links = 0

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                links = re.findall(link_pattern, content)

                for link_text, link_url in links:
                    total_links += 1

                    # Skip external links
                    if link_url.startswith(("http://", "https://", "mailto:")):
                        external_links += 1
                        continue

                    # Check if internal link exists
                    if link_url.startswith("#"):
                        # Anchor link, skip for now
                        continue

                    # Resolve relative path
                    target = (md_file.parent / link_url).resolve()

                    if target.exists():
                        valid_links += 1
                    else:
                        broken_links.append({
                            "source": str(md_file.relative_to(project)),
                            "target": link_url,
                            "link_text": link_text,
                        })
            except Exception:
                continue

        return {
            "total_links": total_links,
            "valid_links": valid_links,
            "broken_links": broken_links, # Return the list itself
            "external_links": external_links,
        }

    def _analyze_metadata(self, md_files: List[Path]) -> Dict[str, Any]:
        """Analyze metadata consistency across documents."""
        metadata_fields = defaultdict(int)
        files_with_metadata = 0
        files_without_metadata = 0

        required_fields = {"title", "description", "type", "status", "created", "updated"}
        missing_required = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")

                # Check for YAML frontmatter
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)

                if match:
                    files_with_metadata += 1
                    yaml_content = match.group(1)

                    # Extract field names (simple parsing)
                    fields = re.findall(r"^(\w+):", yaml_content, re.MULTILINE)

                    for field in fields:
                        metadata_fields[field] += 1

                    # Check required fields
                    missing = required_fields - set(fields)
                    if missing:
                        missing_required.append({
                            "file": md_file.name,
                            "missing": list(missing),
                        })
                else:
                    files_without_metadata += 1
            except Exception:
                files_without_metadata += 1

        return {
            "files_with_metadata": files_with_metadata,
            "files_without_metadata": files_without_metadata,
            "common_fields": dict(sorted(metadata_fields.items(), key=lambda x: -x[1])[:10]),
            "missing_required_fields": len(missing_required),
            "missing_required_details": missing_required[:5],
        }

    def _analyze_quality(self, md_files: List[Path]) -> Dict[str, Any]:
        """Analyze content quality indicators."""
        total_lines = 0
        total_words = 0
        files_with_headers = 0
        files_with_code_blocks = 0
        very_short_files = []
        very_long_files = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")
                words = len(content.split())

                total_lines += len(lines)
                total_words += words

                # Check for headers
                if any(line.startswith("#") for line in lines):
                    files_with_headers += 1

                # Check for code blocks
                if "```" in content:
                    files_with_code_blocks += 1

                # Check file length
                if len(lines) < 10:
                    very_short_files.append(md_file.name)
                elif len(lines) > 1000:
                    very_long_files.append(md_file.name)
            except Exception:
                continue

        avg_lines = total_lines / len(md_files) if md_files else 0
        avg_words = total_words / len(md_files) if md_files else 0

        return {
            "average_lines_per_file": round(avg_lines, 1),
            "average_words_per_file": round(avg_words, 1),
            "files_with_headers": files_with_headers,
            "files_with_code_blocks": files_with_code_blocks,
            "very_short_files": len(very_short_files),
            "very_long_files": len(very_long_files),
            "very_short_details": very_short_files[:5],
            "very_long_details": very_long_files[:5],
        }

    def _calculate_quality_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0

        # Metadata coverage (30 points)
        meta = results["metadata_analysis"]
        total_files = meta["files_with_metadata"] + meta["files_without_metadata"]
        if total_files > 0:
            metadata_ratio = meta["files_with_metadata"] / total_files
            score -= (1 - metadata_ratio) * 30

        # Link integrity (30 points)
        links = results["link_analysis"]
        num_broken_links = len(links["broken_links"])
        if links["total_links"] > 0:
            link_health = links["valid_links"] / (links["valid_links"] + num_broken_links)
            score -= (1 - link_health) * 30

        # Content quality (20 points)
        quality = results["quality_indicators"]
        if quality["very_short_files"] > 0:
            score -= min(quality["very_short_files"] * 2, 10)
        if quality["very_long_files"] > 0:
            score -= min(quality["very_long_files"], 10)

        # Structure (20 points)
        if quality["files_with_headers"] < total_files * 0.8:
            score -= 10

        return max(0.0, min(100.0, round(score, 1)))

    def _generate_issues(self, results: Dict[str, Any]) -> List[str]:
        """Generate list of issues found."""
        issues = []

        meta = results["metadata_analysis"]
        links = results["link_analysis"]
        quality = results["quality_indicators"]

        if meta["files_without_metadata"] > 0:
            issues.append(
                f"🔴 {meta['files_without_metadata']} files missing YAML frontmatter"
            )

        num_broken_links = len(links["broken_links"])
        if num_broken_links > 0:
            issues.append(
                f"🔴 {num_broken_links} broken internal links detected"
            )

        if quality["very_short_files"] > 5:
            issues.append(
                f"⚠️  {quality['very_short_files']} files have < 10 lines (may be stubs)"
            )

        if quality["very_long_files"] > 0:
            issues.append(
                f"⚠️  {quality['very_long_files']} files exceed 1000 lines (consider splitting)"
            )

        if meta["missing_required_fields"] > 0:
            issues.append(
                f"⚠️  {meta['missing_required_fields']} files missing required metadata fields"
            )

        return issues

    def _generate_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable improvement suggestions."""
        suggestions = []

        score = results["quality_score"]

        if score < 50:
            suggestions.append(
                "🚨 Documentation quality is low. Consider a comprehensive audit."
            )
        elif score < 70:
            suggestions.append(
                "⚠️  Documentation quality needs improvement. Focus on metadata and links."
            )
        elif score < 90:
            suggestions.append(
                "✅ Documentation quality is good. Minor improvements recommended."
            )
        else:
            suggestions.append(
                "🎉 Excellent documentation quality! Keep up the good work."
            )

        # Specific suggestions
        meta = results["metadata_analysis"]
        if meta["files_without_metadata"] > 0:
            suggestions.append(
                "→ Add YAML frontmatter to all documents using cde_addMetadata tool"
            )

        links = results["link_analysis"]
        if len(links["broken_links"]) > 0:
            suggestions.append(
                "→ Fix broken links to improve navigation and discoverability"
            )

        quality = results["quality_indicators"]
        if quality["very_long_files"] > 0:
            suggestions.append(
                "→ Split long documents (>1000 lines) into focused sub-documents"
            )

        return suggestions
