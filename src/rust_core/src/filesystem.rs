//! High-performance filesystem operations

use pyo3::prelude::*;
use std::path::Path;
use walkdir::WalkDir;
use regex::Regex;

/// Fast file finding with glob pattern support
pub fn find_files_impl(root_path: &str, patterns: Vec<String>) -> anyhow::Result<Vec<String>> {
    let root_path = Path::new(root_path);
    let mut results = Vec::new();

    // Compile regex patterns
    let regex_patterns: Vec<Regex> = patterns
        .iter()
        .map(|p| {
            // Convert glob patterns to regex
            let regex_pattern = p
                .replace(".", r"\.")
                .replace("*", ".*")
                .replace("?", ".");
            Regex::new(&format!("^{}$", regex_pattern))
        })
        .collect::<Result<Vec<_>, _>>()?;

    for entry in WalkDir::new(root_path).into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_file() {
            if let Some(file_name) = path.file_name() {
                let file_name_str = file_name.to_string_lossy();
                // Check if file matches any pattern
                if regex_patterns.iter().any(|re| re.is_match(&file_name_str)) {
                    if let Ok(relative) = path.strip_prefix(root_path) {
                        results.push(relative.to_string_lossy().to_string());
                    }
                }
            }
        }
    }

    Ok(results)
}
