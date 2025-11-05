//! High-performance documentation processing functions

use pyo3::prelude::*;
use pyo3::PyResult;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use tokio::fs;
use walkdir::WalkDir;
use regex::Regex;

/// Result of documentation scanning
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    pub total_docs: usize,
    pub by_location: HashMap<String, usize>,
    pub missing_metadata: Vec<String>,
    pub orphaned_docs: Vec<String>,
    pub large_files: Vec<String>,
    pub recommendations: Vec<String>,
}

/// Result of comprehensive documentation analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisResult {
    pub quality_score: f64,
    pub total_files: usize,
    pub files_with_metadata: usize,
    pub orphaned_files: usize,
    pub large_files: usize,
    pub recommendations: Vec<String>,
    pub scan_result: ScanResult,
}

/// Fast documentation scanning using parallel processing
pub async fn scan_documentation_impl(project_path: &str) -> anyhow::Result<ScanResult> {
    let project_path = Path::new(project_path);

    // Compile regex patterns once
    let yaml_pattern = Regex::new(r"^---\s*$")?;
    let md_pattern = Regex::new(r"\.md$")?;

    // Collect all markdown files in parallel
    let mut markdown_files = Vec::new();
    for entry in WalkDir::new(project_path).into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_file() {
            if let Some(ext) = path.extension() {
                if ext == "md" {
                    markdown_files.push(path.to_path_buf());
                }
            }
        }
    }

    let total_docs = markdown_files.len();
    let mut by_location = HashMap::new();
    let mut missing_metadata = Vec::new();
    let mut orphaned_docs = Vec::new();
    let mut large_files = Vec::new();

    // Process files in parallel
    let results: Vec<_> = markdown_files
        .into_iter()
        .map(|path| {
            tokio::spawn(async move {
                process_markdown_file(path).await
            })
        })
        .collect();

    for result in results {
        if let Ok(file_result) = result.await? {
            // Update location counts
            let location = file_result.location;
            *by_location.entry(location.clone()).or_insert(0) += 1;

            // Check for issues
            if !file_result.has_metadata {
                missing_metadata.push(file_result.relative_path.clone());
            }

            if file_result.is_orphaned {
                orphaned_docs.push(file_result.relative_path.clone());
            }

            if file_result.is_large {
                large_files.push(file_result.relative_path.clone());
            }
        }
    }

    // Generate recommendations
    let mut recommendations = Vec::new();
    if missing_metadata.len() > 0 {
        recommendations.push(format!("🔴 {} documents missing YAML frontmatter metadata", missing_metadata.len()));
    }
    if orphaned_docs.len() > 0 {
        recommendations.push(format!("⚠️ {} orphaned documents in root directory", orphaned_docs.len()));
    }
    if large_files.len() > 0 {
        recommendations.push(format!("📏 {} documents exceed 1000 lines", large_files.len()));
    }

    Ok(ScanResult {
        total_docs,
        by_location,
        missing_metadata,
        orphaned_docs,
        large_files,
        recommendations,
    })
}

#[derive(Debug)]
struct FileResult {
    location: String,
    relative_path: String,
    has_metadata: bool,
    is_orphaned: bool,
    is_large: bool,
}

async fn process_markdown_file(path: std::path::PathBuf) -> anyhow::Result<FileResult> {
    let content = fs::read_to_string(&path).await?;
    let lines: Vec<&str> = content.lines().collect();

    // Check for YAML frontmatter
    let has_metadata = lines.len() >= 3 && lines[0] == "---" && content.contains("\n---\n");

    // Determine location category
    let relative_path = path.strip_prefix(std::env::current_dir()?)?
        .to_string_lossy()
        .to_string();

    let location = if relative_path.starts_with("specs/") {
        "specs".to_string()
    } else if relative_path.starts_with("agent-docs/") {
        "agent-docs".to_string()
    } else if relative_path.starts_with("docs/") {
        "docs".to_string()
    } else {
        "other".to_string()
    };

    // Check if orphaned (in root or unexpected location)
    let is_orphaned = !relative_path.contains('/') ||
        (relative_path.split('/').count() == 2 && !relative_path.starts_with("specs/") &&
         !relative_path.starts_with("agent-docs/") && !relative_path.starts_with("docs/"));

    // Check if large file
    let is_large = lines.len() > 1000;

    Ok(FileResult {
        location,
        relative_path,
        has_metadata,
        is_orphaned,
        is_large,
    })
}

/// Comprehensive documentation analysis
pub async fn analyze_documentation_impl(project_path: &str) -> Result<AnalysisResult, Box<dyn std::error::Error + Send + Sync>> {
    let scan_result = scan_documentation_impl(project_path).await?;

    // Calculate quality metrics from scan results
    let total_files = scan_result.total_docs;
    let missing_metadata_count = scan_result.missing_metadata.len();
    let orphaned_files = scan_result.orphaned_docs.len();
    let large_files = scan_result.large_files.len();
    let files_with_metadata = total_files.saturating_sub(missing_metadata_count);

    let quality_score = if total_files > 0 {
        (files_with_metadata as f64 / total_files as f64) * 100.0
    } else {
        0.0
    };

    // Generate recommendations
    let mut recommendations = Vec::new();

    if missing_metadata_count > 0 {
        recommendations.push(format!(
            "Add YAML frontmatter to {} files missing metadata",
            missing_metadata_count
        ));
    }

    if orphaned_files > 0 {
        recommendations.push(format!(
            "Move {} orphaned files to correct directories per governance rules",
            orphaned_files
        ));
    }

    if large_files > 0 {
        recommendations.push(format!(
            "Consider splitting {} large files (>1000 lines) into smaller documents",
            large_files
        ));
    }

    Ok(AnalysisResult {
        quality_score,
        total_files,
        files_with_metadata,
        orphaned_files,
        large_files,
        recommendations,
        scan_result,
    })
}