// src/documentation.rs
use crate::filesystem::find_markdown_files;
use rayon::prelude::*;
use std::fs;
use std::path::Path;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Document {
    pub path: String,
    pub content: String,
    pub word_count: usize,
}

/// Scans a documentation project, finds all Markdown files, and reads their content in parallel.
pub fn scan_documentation(root_path: &str) -> Result<Vec<Document>, String> {
    let path = Path::new(root_path);
    if !path.is_dir() {
        return Err(format!("'{}' is not a valid directory.", root_path));
    }

    let files = find_markdown_files(path);

    let documents: Vec<Document> = files
        .par_iter()
        .filter_map(|path_str| {
            if let Ok(content) = fs::read_to_string(path_str) {
                let word_count = content.split_whitespace().count();
                Some(Document {
                    path: path_str.clone(),
                    content,
                    word_count,
                })
            } else {
                None // Skip files that can't be read
            }
        })
        .collect();

    Ok(documents)
}
