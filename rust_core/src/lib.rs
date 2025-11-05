// src/lib.rs
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod filesystem;
mod documentation;
// No incluyo doc_validator ya que revertí esa funcionalidad

/// Scans a documentation project, finds all Markdown files, and returns their content.
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

/// A Python module implemented in Rust.
#[pymodule]
fn cde_rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(scan_documentation_py, m)?)?;
    Ok(())
}
