// src/lib.rs
use pyo3::prelude::*;
use rayon::ThreadPoolBuilder;
use std::sync::Once;

mod filesystem;
mod documentation;
mod workflow_validator;

static INIT: Once = Once::new();

/// Initialize Rayon thread pool with optimal settings
/// Called once when the module is loaded
fn init_rayon() {
    INIT.call_once(|| {
        let num_threads = num_cpus::get();

        ThreadPoolBuilder::new()
            .num_threads(num_threads)  // Auto-detect: usa todos los cores
            .thread_name(|i| format!("cde-rayon-{}", i))
            .panic_handler(|_| {
                // Prevenir panic unwinding en threads paralelos
                eprintln!("Rayon thread panicked, but continuing execution");
            })
            .build_global()
            .expect("Failed to initialize Rayon thread pool");

        eprintln!("✅ Rayon initialized with {} threads", num_threads);
    });
}

/// Scans a documentation project, finds all Markdown files, and returns their content.
/// Extracts YAML frontmatter, links, headers, and word count in parallel.
#[pyfunction]
fn scan_documentation_py(root_path: String) -> PyResult<String> {
    match documentation::scan_documentation(&root_path) {
        Ok(documents) => {
            let json_result = serde_json::to_string(&documents).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to serialize result: {}", e))
            })?;
            Ok(json_result)
        }
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(e)),
    }
}

/// Analyzes documentation quality in parallel.
/// Returns quality score, broken links, missing metadata, and recommendations.
#[pyfunction]
fn analyze_documentation_quality_py(root_path: String) -> PyResult<String> {
    match documentation::analyze_documentation_quality(&root_path) {
        Ok(report) => {
            let json_result = serde_json::to_string(&report).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to serialize result: {}", e))
            })?;
            Ok(json_result)
        }
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(e)),
    }
}

/// Validates workflow YAML files in parallel.
/// Returns validation report with issues, missing templates, and summary.
#[pyfunction]
fn validate_workflows_py(root_path: String) -> PyResult<String> {
    match workflow_validator::validate_workflows(&root_path) {
        Ok(report) => {
            let json_result = serde_json::to_string(&report).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to serialize result: {}", e))
            })?;
            Ok(json_result)
        }
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(e)),
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn cde_rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Inicializar Rayon thread pool al cargar el módulo
    init_rayon();

    m.add_function(wrap_pyfunction!(scan_documentation_py, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_documentation_quality_py, m)?)?;
    m.add_function(wrap_pyfunction!(validate_workflows_py, m)?)?;
    Ok(())
}
