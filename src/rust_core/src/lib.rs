use pyo3::prelude::*;

/// High-performance Rust core for CDE Orchestrator MCP
///
/// This module provides optimized implementations for I/O intensive operations
/// that are critical for the MCP server's performance.
#[pymodule]
mod cde_rust_core {
    use super::*;

    /// Documentation scanning and analysis functions
    #[pymodule]
    mod documentation {
        use super::*;
        use crate::documentation::*;
        use pyo3::prelude::*;

        #[pyfunction]
        pub fn scan_documentation_fast(
            py: Python,
            project_path: String,
        ) -> PyResult<PyObject> {
            // Create a tokio runtime for async operations
            let rt = tokio::runtime::Runtime::new().map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create runtime: {}", e))
            })?;

            let result = rt.block_on(async {
                documentation::scan_documentation_impl(&project_path).await
            });

            match result {
                Ok(scan_result) => Ok(serde_json::to_string(&scan_result).unwrap().into_py(py)),
                Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Scan failed: {}", e))),
            }
        }

        #[pyfunction]
        pub fn analyze_documentation_fast(
            py: Python,
            project_path: String,
        ) -> PyResult<PyObject> {
            // Create a tokio runtime for async operations
            let rt = tokio::runtime::Runtime::new().map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create runtime: {}", e))
            })?;

            let result = rt.block_on(async {
                documentation::analyze_documentation_impl(&project_path).await
            });

            match result {
                Ok(analysis_result) => Ok(serde_json::to_string(&analysis_result).unwrap().into_py(py)),
                Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Analysis failed: {}", e))),
            }
        }
    }

    /// File system operations
    #[pymodule]
    mod filesystem {
        use super::*;
        use crate::filesystem::*;
        use pyo3::prelude::*;

        #[pyfunction]
        pub fn find_files_fast(
            py: Python,
            root_path: String,
            patterns: Vec<String>,
        ) -> PyResult<PyObject> {
            match filesystem::find_files_impl(&root_path, patterns) {
                Ok(results) => Ok(results.into_py(py)),
                Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("File search failed: {}", e))),
            }
        }
    }

    /// Text processing utilities
    #[pymodule]
    mod text {
        use super::*;
        use crate::text::*;
        use pyo3::prelude::*;

        #[pyfunction]
        pub fn extract_metadata_fast(
            py: Python,
            content: String,
        ) -> PyResult<PyObject> {
            match text::extract_metadata_impl(&content) {
                Ok(metadata) => Ok(serde_json::to_string(&metadata).unwrap().into_py(py)),
                Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Metadata extraction failed: {}", e))),
            }
        }

        #[pyfunction]
        pub fn analyze_text_fast(
            py: Python,
            content: String,
            analysis_type: String,
        ) -> PyResult<PyObject> {
            match text::analyze_text_impl(&content, &analysis_type) {
                Ok(results) => Ok(serde_json::to_string(&results).unwrap().into_py(py)),
                Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Text analysis failed: {}", e))),
            }
        }
    }
}

// Internal modules
mod documentation;
mod filesystem;
mod text;
