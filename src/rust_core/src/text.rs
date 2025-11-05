//! High-performance text processing utilities

use pyo3::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Extract YAML frontmatter from markdown content
pub fn extract_metadata_impl(content: &str) -> anyhow::Result<HashMap<String, String>> {
    let mut metadata = HashMap::new();

    // Find YAML frontmatter (between --- markers)
    if let Some(start) = content.find("---") {
        if let Some(end) = content[start + 3..].find("---") {
            let yaml_content = &content[start + 3..start + 3 + end];

            // Simple YAML parsing (basic key-value pairs)
            for line in yaml_content.lines() {
                let line = line.trim();
                if line.is_empty() || line.starts_with('#') {
                    continue;
                }

                if let Some(colon_pos) = line.find(':') {
                    let key = line[..colon_pos].trim().to_string();
                    let value = line[colon_pos + 1..].trim().trim_matches('"').to_string();
                    metadata.insert(key, value);
                }
            }
        }
    }

    Ok(metadata)
}

/// Fast text analysis for documentation quality
pub fn analyze_text_quality_impl(content: &str) -> anyhow::Result<TextQualityMetrics> {
    let lines: Vec<&str> = content.lines().collect();
    let total_lines = lines.len();
    let total_chars = content.chars().count();

    // Count different types of content
    let mut code_blocks = 0;
    let mut headings = 0;
    let mut links = 0;
    let mut lists = 0;
    let mut in_code_block = false;

    for line in &lines {
        let trimmed = line.trim();

        if trimmed.starts_with("```") {
            in_code_block = !in_code_block;
            code_blocks += 1;
            continue;
        }

        if in_code_block {
            continue;
        }

        if trimmed.starts_with('#') {
            headings += 1;
        } else if trimmed.starts_with("- ") || trimmed.starts_with("* ") || trimmed.starts_with("1. ") {
            lists += 1;
        } else if trimmed.contains("](") {
            links += 1;
        }
    }

    // Calculate quality score (0-100)
    let mut score = 0.0;

    // Structure bonus
    if headings > 0 {
        score += 20.0 * (headings as f64 / total_lines as f64).min(1.0);
    }

    // Content bonus
    if code_blocks > 0 {
        score += 15.0;
    }

    if links > 0 {
        score += 10.0;
    }

    if lists > 0 {
        score += 10.0;
    }

    // Length bonus (reasonable length)
    if total_lines > 10 && total_lines < 500 {
        score += 20.0;
    }

    // Metadata bonus (assume it's present if called)
    score += 25.0;

    Ok(TextQualityMetrics {
        total_lines,
        total_chars,
        headings,
        code_blocks: code_blocks / 2, // Each code block has 2 markers
        links,
        lists,
        quality_score: score.min(100.0),
    })
}

/// Generic text analysis dispatcher
pub fn analyze_text_impl(content: &str, analysis_type: &str) -> anyhow::Result<serde_json::Value> {
    match analysis_type {
        "quality" => {
            let metrics = analyze_text_quality_impl(content)?;
            Ok(serde_json::to_value(metrics)?)
        },
        "metadata" => {
            let metadata = extract_metadata_impl(content)?;
            Ok(serde_json::to_value(metadata)?)
        },
        "structure" => {
            // Basic structure analysis
            let lines: Vec<&str> = content.lines().collect();
            let structure = analyze_text_structure(&lines);
            Ok(serde_json::to_value(structure)?)
        },
        _ => Err(anyhow::anyhow!("Unknown analysis type: {}", analysis_type)),
    }
}

/// Analyze text structure (headings, sections, etc.)
fn analyze_text_structure(lines: &[&str]) -> HashMap<String, serde_json::Value> {
    let mut structure = HashMap::new();
    let mut sections = Vec::new();
    let mut current_section = None;

    for (i, line) in lines.iter().enumerate() {
        if line.starts_with('#') {
            // Found a heading
            if let Some(section) = current_section.take() {
                sections.push(section);
            }

            let level = line.chars().take_while(|&c| c == '#').count();
            let title = line[level..].trim();
            current_section = Some(serde_json::json!({
                "level": level,
                "title": title,
                "line": i + 1
            }));
        }
    }

    if let Some(section) = current_section {
        sections.push(section);
    }

    let total_sections = sections.len();
    structure.insert("sections".to_string(), serde_json::Value::Array(sections));
    structure.insert("total_sections".to_string(), total_sections.into());

    structure
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextQualityMetrics {
    pub total_lines: usize,
    pub total_chars: usize,
    pub headings: usize,
    pub code_blocks: usize,
    pub links: usize,
    pub lists: usize,
    pub quality_score: f64,
}