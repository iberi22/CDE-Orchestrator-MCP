// src/filesystem.rs
use std::path::Path;
use walkdir::WalkDir;
use rayon::prelude::*;

/// Finds all Markdown files in a directory in parallel, excluding common directories.
pub fn find_markdown_files(root_path: &Path) -> Vec<String> {
    let excluded_dirs = [".git", ".venv", "node_modules", "venv", "__pycache__", ".pytest_cache", "target"];

    WalkDir::new(root_path)
        .into_iter()
        .filter_map(Result::ok)
        .par_bridge() // Process entries in parallel
        .filter(|e| {
            let path = e.path();
            // Exclude directories
            if e.file_type().is_dir() {
                if let Some(dir_name) = path.file_name().and_then(|n| n.to_str()) {
                    return !excluded_dirs.contains(&dir_name);
                }
            }
            // Include only markdown files
            path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("md")
        })
        .map(|e| e.path().to_string_lossy().into_owned())
        .collect()
}
