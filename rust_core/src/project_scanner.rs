// rust_core/src/project_scanner.rs
// Parallel project scanner with Rayon for CDE Orchestrator
// Now with .gitignore support using the `ignore` crate

use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::time::Instant;
use walkdir::WalkDir;
use ignore::gitignore::{Gitignore, GitignoreBuilder};

/// Result of project analysis
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ProjectAnalysisResult {
    pub file_count: usize,
    pub language_stats: HashMap<String, usize>,
    pub dependency_files: Vec<String>,
    pub excluded_directories: Vec<String>,
    pub excluded_count: usize,
    pub analysis_time_ms: u128,
}

/// Scans a project directory in parallel, excluding specified directories and patterns
///
/// # Arguments
/// * `root_path` - Root directory to scan
/// * `excluded_dirs` - Directories to exclude (e.g., "node_modules", "__pycache__")
/// * `excluded_patterns` - File patterns to exclude (e.g., "*.map", "*.pyc")
///
/// # Returns
/// * `Ok(ProjectAnalysisResult)` - Analysis result with timing
/// * `Err(String)` - Error message
pub fn scan_project(
    root_path: &str,
    excluded_dirs: Vec<String>,
    excluded_patterns: Vec<String>,
) -> Result<ProjectAnalysisResult, String> {
    let start = Instant::now();

    // Load .gitignore rules if they exist
    let gitignore = load_gitignore(root_path).unwrap_or_else(|_| {
        Gitignore::empty()
    });

    // Compile regex patterns for efficient matching
    let patterns: Vec<Regex> = excluded_patterns
        .iter()
        .filter_map(|p| {
            // Convert glob patterns to regex (e.g., "*.map" -> r"\.map$")
            let regex_pattern = glob_to_regex(p);
            match Regex::new(&regex_pattern) {
                Ok(r) => Some(r),
                Err(e) => {
                    eprintln!("Failed to compile pattern {}: {}", p, e);
                    None
                }
            }
        })
        .collect();

    // Parallel filesystem scan with WalkDir
    let walker = WalkDir::new(root_path)
        .into_iter()
        .filter_map(|entry| entry.ok());

    let root_path_buf = PathBuf::from(root_path);

    // Process files in parallel using collect
    let (file_paths, language_stats, excluded_count) = walker
        .par_bridge()
        .fold(
            || (Vec::new(), HashMap::new(), 0usize),
            |(mut files, mut stats, mut excluded), entry| {
                let path = entry.path().to_path_buf();

                // Skip directories
                if path.is_dir() {
                    return (files, stats, excluded);
                }

                // Check if in excluded directories
                if is_in_excluded_dir(&path, &excluded_dirs) {
                    excluded += 1;
                    return (files, stats, excluded);
                }

                // Check if matches excluded patterns
                if is_matching_pattern(&path, &patterns) {
                    excluded += 1;
                    return (files, stats, excluded);
                }

                // Check if in .gitignore
                if is_in_gitignore(&path, &root_path_buf, &gitignore) {
                    excluded += 1;
                    return (files, stats, excluded);
                }

                // Extract file extension and update stats
                if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                    let ext_key = format!(".{}", ext);
                    *stats.entry(ext_key).or_insert(0) += 1;
                }

                files.push(path);
                (files, stats, excluded)
            },
        )
        .reduce(
            || (Vec::new(), HashMap::new(), 0),
            |(mut f1, mut s1, e1), (f2, s2, e2)| {
                f1.extend(f2);
                for (k, v) in s2 {
                    *s1.entry(k).or_insert(0) += v;
                }
                (f1, s1, e1 + e2)
            },
        );

    // Find dependency files
    let dependency_files = find_dependency_files(&file_paths);

    let analysis_time_ms = start.elapsed().as_millis();

    Ok(ProjectAnalysisResult {
        file_count: file_paths.len(),
        language_stats,
        dependency_files,
        excluded_directories: excluded_dirs,
        excluded_count,
        analysis_time_ms,
    })
}

/// Check if a path is in an excluded directory
fn is_in_excluded_dir(path: &Path, excluded_dirs: &[String]) -> bool {
    path.components().any(|component| {
        if let std::path::Component::Normal(name) = component {
            if let Some(name_str) = name.to_str() {
                return excluded_dirs.iter().any(|excluded| excluded == name_str);
            }
        }
        false
    })
}

/// Load .gitignore rules from project root
fn load_gitignore(root_path: &str) -> Result<Gitignore, Box<dyn std::error::Error>> {
    let gitignore_path = PathBuf::from(root_path).join(".gitignore");

    if !gitignore_path.exists() {
        return Ok(Gitignore::empty());
    }

    let mut builder = GitignoreBuilder::new(root_path);
    builder.add(&gitignore_path);

    builder.build()
        .map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
}

/// Check if a file path matches .gitignore rules
fn is_in_gitignore(path: &Path, root: &PathBuf, gitignore: &Gitignore) -> bool {
    match path.strip_prefix(root) {
        Ok(relative_path) => {
            let match_result = gitignore.matched(relative_path, path.is_dir());
            match match_result {
                ignore::Match::None => false,
                ignore::Match::Ignore(_) => true,
                ignore::Match::Whitelist(_) => false,
            }
        }
        Err(_) => false,
    }
}

fn is_matching_pattern(path: &Path, patterns: &[Regex]) -> bool {
    let path_str = path.to_string_lossy();
    patterns.iter().any(|pattern| pattern.is_match(&path_str))
}

/// Find common dependency management files
fn find_dependency_files(file_paths: &[PathBuf]) -> Vec<String> {
    const DEPENDENCY_FILES: &[&str] = &[
        "requirements.txt",
        "package.json",
        "pyproject.toml",
        "pom.xml",
        "build.gradle",
        "Cargo.toml",
    ];

    let mut found = std::collections::HashSet::new();

    for file_path in file_paths {
        if let Some(file_name) = file_path.file_name() {
            if let Some(name_str) = file_name.to_str() {
                if DEPENDENCY_FILES.contains(&name_str) {
                    found.insert(name_str.to_string());
                }
            }
        }
    }

    let mut result: Vec<String> = found.into_iter().collect();
    result.sort();
    result
}

/// Convert glob pattern to regex pattern
fn glob_to_regex(glob_pattern: &str) -> String {
    glob_pattern
        .replace(".", r"\.")
        .replace("*", ".*")
        .replace("?", ".")
        + "$"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_glob_to_regex() {
        assert_eq!(glob_to_regex("*.map"), r".*\.map$");
        assert_eq!(glob_to_regex("*.py[co]"), r".*\.py[co]$");
    }

    #[test]
    fn test_is_matching_pattern() {
        let patterns = vec![
            Regex::new(r".*\.map$").unwrap(),
            Regex::new(r".*\.pyc$").unwrap(),
        ];

        assert!(is_matching_pattern(Path::new("file.map"), &patterns));
        assert!(is_matching_pattern(Path::new("file.pyc"), &patterns));
        assert!(!is_matching_pattern(Path::new("file.py"), &patterns));
    }

    #[test]
    fn test_is_in_excluded_dir() {
        let excluded = vec!["node_modules".to_string(), "__pycache__".to_string()];

        assert!(is_in_excluded_dir(
            Path::new("src/node_modules/package/file.js"),
            &excluded
        ));
        assert!(is_in_excluded_dir(
            Path::new("src/__pycache__/module.pyc"),
            &excluded
        ));
        assert!(!is_in_excluded_dir(Path::new("src/main.py"), &excluded));
    }

    #[test]
    fn test_find_dependency_files() {
        let paths = vec![
            PathBuf::from("src/main.rs"),
            PathBuf::from("Cargo.toml"),
            PathBuf::from("package.json"),
            PathBuf::from("random.txt"),
        ];
        let deps = find_dependency_files(&paths);
        assert!(deps.contains(&"Cargo.toml".to_string()));
        assert!(deps.contains(&"package.json".to_string()));
        assert!(!deps.contains(&"random.txt".to_string()));
        assert_eq!(deps.len(), 2);
    }

    #[test]
    fn test_scan_project_integration() {
        use std::fs::{self, File};
        use std::io::Write;
        use tempfile::TempDir;

        // Create a temp directory
        let temp_dir = TempDir::new().unwrap();
        let root = temp_dir.path();

        // Create some files
        File::create(root.join("main.py")).unwrap();
        File::create(root.join("requirements.txt")).unwrap();

        // Create excluded directory
        let node_modules = root.join("node_modules");
        fs::create_dir(&node_modules).unwrap();
        File::create(node_modules.join("lib.js")).unwrap();

        // Create excluded file by pattern
        File::create(root.join("test.pyc")).unwrap();

        // Create .gitignore
        let mut gitignore = File::create(root.join(".gitignore")).unwrap();
        writeln!(gitignore, "ignored.txt").unwrap();
        File::create(root.join("ignored.txt")).unwrap();

        // Run scan
        let excluded_dirs = vec!["node_modules".to_string()];
        let excluded_patterns = vec!["*.pyc".to_string()];

        let result = scan_project(
            root.to_str().unwrap(),
            excluded_dirs,
            excluded_patterns
        ).unwrap();

        // Verify results
        assert_eq!(result.file_count, 3); // main.py, requirements.txt, .gitignore
        assert!(result.dependency_files.contains(&"requirements.txt".to_string()));
        assert_eq!(result.language_stats.get(".py"), Some(&1));
        assert!(result.excluded_count >= 3); // lib.js (dir), test.pyc (pattern), ignored.txt (gitignore)
    }
}
