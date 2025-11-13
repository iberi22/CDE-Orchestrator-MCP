// src/documentation.rs
use crate::filesystem::find_markdown_files;
use rayon::prelude::*;
use std::fs;
use std::path::Path;
use std::sync::Mutex;
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

    // Calcular chunk size óptimo basado en CPU cores
    let num_files = files.len();
    let num_threads = rayon::current_num_threads();
    let chunk_size = (num_files / num_threads).max(1);

    // Coleccionar errores de manera thread-safe
    let errors = Mutex::new(Vec::new());

    let documents: Vec<Document> = files
        .par_iter()
        .with_min_len(chunk_size)  // Evitar overhead de chunks pequeños
        .filter_map(|path_str| {
            match fs::read_to_string(path_str) {
                Ok(content) => {
                    // Word count paralelo solo para archivos grandes (>100KB)
                    let word_count = if content.len() > 100_000 {
                        // Nested parallelism para archivos grandes
                        content.par_split_whitespace().count()
                    } else {
                        // Sequential para archivos pequeños (menos overhead)
                        content.split_whitespace().count()
                    };

                    Some(Document {
                        path: path_str.clone(),
                        content,
                        word_count,
                    })
                },
                Err(e) => {
                    // Registrar error sin detener el procesamiento
                    errors.lock().unwrap().push((path_str.clone(), e.to_string()));
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
