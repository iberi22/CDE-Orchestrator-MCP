// src/documentation.rs
use crate::filesystem::find_markdown_files;
use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_yaml;
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use std::sync::Mutex;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct YamlFrontmatter {
    pub title: Option<String>,
    pub description: Option<String>,
    #[serde(rename = "type")]
    pub doc_type: Option<String>,
    pub status: Option<String>,
    pub created: Option<String>,
    pub updated: Option<String>,
    pub author: Option<String>,
    pub llm_summary: Option<String>,
    #[serde(flatten)]
    pub extra: HashMap<String, serde_yaml::Value>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct LinkInfo {
    pub text: String,
    pub url: String,
    pub is_internal: bool,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Document {
    pub path: String,
    pub content: String,
    pub word_count: usize,
    pub has_frontmatter: bool,
    pub metadata: Option<YamlFrontmatter>,
    pub links: Vec<LinkInfo>,
    pub headers: Vec<String>,
}

/// Extrae YAML frontmatter de un documento Markdown
fn extract_frontmatter(content: &str) -> Option<YamlFrontmatter> {
    if !content.starts_with("---") {
        return None;
    }

    let parts: Vec<&str> = content.splitn(3, "---").collect();
    if parts.len() < 3 {
        return None;
    }

    let yaml_str = parts[1].trim();
    serde_yaml::from_str(yaml_str).ok()
}

/// Extrae todos los links Markdown de un documento
fn extract_links(content: &str) -> Vec<LinkInfo> {
    let link_regex = Regex::new(r"\[([^\]]+)\]\(([^\)]+)\)").unwrap();

    link_regex
        .captures_iter(content)
        .filter_map(|cap| {
            let text = cap.get(1)?.as_str().to_string();
            let url = cap.get(2)?.as_str().to_string();
            let is_internal = !url.starts_with("http://") && !url.starts_with("https://");

            Some(LinkInfo {
                text,
                url,
                is_internal,
            })
        })
        .collect()
}

/// Extrae todos los headers de un documento Markdown
fn extract_headers(content: &str) -> Vec<String> {
    let header_regex = Regex::new(r"(?m)^#+\s+(.+)$").unwrap();

    header_regex
        .captures_iter(content)
        .filter_map(|cap| cap.get(1).map(|m| m.as_str().to_string()))
        .collect()
}

/// Scans a documentation project, finds all Markdown files, and reads their content in parallel.
/// Extracts YAML frontmatter, links, headers, and word count for each document.
pub fn scan_documentation(root_path: &str) -> Result<Vec<Document>, String> {
    let path = Path::new(root_path);
    if !path.is_dir() {
        return Err(format!("'{}' is not a valid directory.", root_path));
    }

    let files = find_markdown_files(path);

    // Calcular chunk size óptimo basado en CPU cores
    let num_files = files.len();
    let num_threads = rayon::current_num_threads();
    let chunk_size = (num_files / num_threads).max(1);

    // Coleccionar errores de manera thread-safe
    let errors = Mutex::new(Vec::new());

    let documents: Vec<Document> = files
        .par_iter()
        .with_min_len(chunk_size) // Evitar overhead de chunks pequeños
        .filter_map(|path_str| {
            match fs::read_to_string(path_str) {
                Ok(content) => {
                    // Extraer metadata en paralelo
                    let metadata = extract_frontmatter(&content);
                    let has_frontmatter = metadata.is_some();

                    // Word count paralelo solo para archivos grandes (>100KB)
                    let word_count = if content.len() > 100_000 {
                        content.par_split_whitespace().count()
                    } else {
                        content.split_whitespace().count()
                    };

                    // Extraer links y headers (en paralelo para archivos grandes)
                    let (links, headers) = if content.len() > 50_000 {
                        rayon::join(
                            || extract_links(&content),
                            || extract_headers(&content),
                        )
                    } else {
                        (extract_links(&content), extract_headers(&content))
                    };

                    Some(Document {
                        path: path_str.clone(),
                        content,
                        word_count,
                        has_frontmatter,
                        metadata,
                        links,
                        headers,
                    })
                }
                Err(e) => {
                    // Registrar error sin detener el procesamiento
                    errors
                        .lock()
                        .unwrap()
                        .push((path_str.clone(), e.to_string()));
                    None
                }
            }
        })
        .collect();

    // Log warnings pero no fallar
    let error_list = errors.lock().unwrap();
    if !error_list.is_empty() {
        eprintln!("⚠️  Warning: Failed to read {} files", error_list.len());
        for (path, err) in error_list.iter().take(3) {
            eprintln!("   - {}: {}", path, err);
        }
    }

    Ok(documents)
}

#[derive(Serialize, Deserialize, Debug)]
pub struct QualityReport {
    pub quality_score: f32,
    pub total_docs: usize,
    pub docs_with_metadata: usize,
    pub docs_without_metadata: usize,
    pub total_links: usize,
    pub broken_internal_links: Vec<String>,
    pub orphaned_docs: Vec<String>,
    pub large_files: Vec<String>,
    pub issues: Vec<String>,
    pub recommendations: Vec<String>,
}

/// Analiza la calidad de la documentación en paralelo
pub fn analyze_documentation_quality(root_path: &str) -> Result<QualityReport, String> {
    let documents = scan_documentation(root_path)?;

    if documents.is_empty() {
        return Ok(QualityReport {
            quality_score: 0.0,
            total_docs: 0,
            docs_with_metadata: 0,
            docs_without_metadata: 0,
            total_links: 0,
            broken_internal_links: Vec::new(),
            orphaned_docs: Vec::new(),
            large_files: Vec::new(),
            issues: vec!["No documentation files found".to_string()],
            recommendations: vec!["Create documentation files with YAML frontmatter".to_string()],
        });
    }

    // Análisis paralelo de métricas
    let total_docs = documents.len();

    let (docs_with_metadata, docs_without_metadata, total_links, large_files, orphaned_docs) = documents
        .par_iter()
        .fold(
            || (0, 0, 0, Vec::new(), Vec::new()),
            |(with_meta, without_meta, links, mut large, mut orphaned), doc| {
                let has_meta = if doc.has_frontmatter { 1 } else { 0 };
                let no_meta = if doc.has_frontmatter { 0 } else { 1 };
                let link_count = doc.links.len();

                // Archivos grandes (>1000 líneas)
                if doc.content.lines().count() > 1000 {
                    large.push(doc.path.clone());
                }

                // Documentos huérfanos (no en specs/ ni agent-docs/)
                let path_lower = doc.path.to_lowercase();
                if !path_lower.contains("specs/")
                    && !path_lower.contains("agent-docs/")
                    && !path_lower.contains("readme.md")
                    && !path_lower.contains("changelog.md")
                    && !path_lower.contains("contributing.md")
                    && !path_lower.contains("agents.md")
                    && !path_lower.contains("gemini.md") {
                    orphaned.push(doc.path.clone());
                }

                (with_meta + has_meta, without_meta + no_meta, links + link_count, large, orphaned)
            },
        )
        .reduce(
            || (0, 0, 0, Vec::new(), Vec::new()),
            |(w1, wo1, l1, mut lg1, mut o1), (w2, wo2, l2, lg2, o2)| {
                lg1.extend(lg2);
                o1.extend(o2);
                (w1 + w2, wo1 + wo2, l1 + l2, lg1, o1)
            },
        );

    // Validar links internos en paralelo
    let broken_internal_links: Vec<String> = documents
        .par_iter()
        .flat_map(|doc| {
            doc.links
                .par_iter()
                .filter(|link| link.is_internal)
                .filter_map(|link| {
                    // Simplificación: solo verificar si el archivo existe (ruta relativa)
                    let target_path = Path::new(root_path).join(&link.url);
                    if !target_path.exists() {
                        Some(format!("{} -> {}", doc.path, link.url))
                    } else {
                        None
                    }
                })
                .collect::<Vec<_>>()
        })
        .collect();

    // Calcular quality score (0-100)
    let metadata_score = (docs_with_metadata as f32 / total_docs as f32) * 40.0;
    let link_score = if total_links > 0 {
        ((total_links - broken_internal_links.len()) as f32 / total_links as f32) * 30.0
    } else {
        30.0
    };
    let orphan_penalty = (orphaned_docs.len() as f32 / total_docs as f32) * 20.0;
    let large_file_penalty = (large_files.len() as f32 / total_docs as f32) * 10.0;

    let quality_score = (metadata_score + link_score + 30.0 - orphan_penalty - large_file_penalty).max(0.0).min(100.0);

    // Generar issues y recomendaciones
    let mut issues = Vec::new();
    let mut recommendations = Vec::new();

    if docs_without_metadata > 0 {
        issues.push(format!("🔴 {} documents missing YAML frontmatter", docs_without_metadata));
        recommendations.push("→ Add YAML frontmatter to all documentation files".to_string());
    }

    if !broken_internal_links.is_empty() {
        issues.push(format!("🔴 {} broken internal links detected", broken_internal_links.len()));
        recommendations.push("→ Fix broken links or remove references".to_string());
    }

    if !orphaned_docs.is_empty() {
        issues.push(format!("⚠️ {} orphaned documents in root directory", orphaned_docs.len()));
        recommendations.push("→ Move documents to specs/ or agent-docs/ directories".to_string());
    }

    if !large_files.is_empty() {
        issues.push(format!("⚠️ {} files exceed 1000 lines", large_files.len()));
        recommendations.push("→ Consider splitting large files into smaller modules".to_string());
    }

    if quality_score >= 90.0 {
        recommendations.push("✅ Documentation quality is excellent!".to_string());
    } else if quality_score >= 70.0 {
        recommendations.push("✅ Documentation quality is good. Minor improvements recommended.".to_string());
    } else if quality_score >= 50.0 {
        recommendations.push("⚠️ Documentation needs improvement. Focus on metadata and links.".to_string());
    } else {
        recommendations.push("🔴 Documentation quality is poor. Major improvements needed.".to_string());
    }

    Ok(QualityReport {
        quality_score,
        total_docs,
        docs_with_metadata,
        docs_without_metadata,
        total_links,
        broken_internal_links: broken_internal_links.into_iter().take(20).collect(),
        orphaned_docs: orphaned_docs.into_iter().take(20).collect(),
        large_files: large_files.into_iter().take(20).collect(),
        issues,
        recommendations,
    })
}
