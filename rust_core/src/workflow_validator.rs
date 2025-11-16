// src/workflow_validator.rs
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use serde_yaml;
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct WorkflowPhase {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub inputs: Option<Vec<String>>,
    pub outputs: Option<Vec<String>>,
    pub prompt_template: Option<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Workflow {
    pub name: String,
    pub version: String,
    pub phases: Vec<WorkflowPhase>,
    #[serde(flatten)]
    pub extra: std::collections::HashMap<String, serde_yaml::Value>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct WorkflowValidationIssue {
    pub severity: String, // "error", "warning", "info"
    pub file: String,
    pub line: Option<usize>,
    pub message: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct WorkflowValidationReport {
    pub valid: bool,
    pub total_files: usize,
    pub valid_files: usize,
    pub invalid_files: usize,
    pub issues: Vec<WorkflowValidationIssue>,
    pub workflows_found: Vec<String>,
    pub missing_templates: Vec<String>,
    pub summary: String,
}

/// Encuentra todos los archivos YAML en un directorio
fn find_yaml_files(root: &Path) -> Vec<PathBuf> {
    walkdir::WalkDir::new(root)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .filter(|e| {
            e.path()
                .extension()
                .and_then(|s| s.to_str())
                .map(|s| s == "yml" || s == "yaml" || s == "poml")
                .unwrap_or(false)
        })
        .map(|e| e.path().to_path_buf())
        .collect()
}

/// Valida la sintaxis YAML de un archivo
fn validate_yaml_syntax(path: &Path) -> Result<serde_yaml::Value, String> {
    let content = fs::read_to_string(path)
        .map_err(|e| format!("Failed to read file: {}", e))?;

    serde_yaml::from_str(&content)
        .map_err(|e| format!("Invalid YAML syntax: {}", e))
}

/// Valida un workflow completo
fn validate_workflow_file(path: &Path) -> Vec<WorkflowValidationIssue> {
    let mut issues = Vec::new();
    let path_str = path.to_string_lossy().to_string();

    // Validar sintaxis YAML
    let yaml_value = match validate_yaml_syntax(path) {
        Ok(val) => val,
        Err(e) => {
            issues.push(WorkflowValidationIssue {
                severity: "error".to_string(),
                file: path_str.clone(),
                line: None,
                message: e,
            });
            return issues;
        }
    };

    // Intentar parsear como Workflow
    let workflow: Result<Workflow, _> = serde_yaml::from_value(yaml_value.clone());

    match workflow {
        Ok(wf) => {
            // Validar estructura del workflow
            if wf.phases.is_empty() {
                issues.push(WorkflowValidationIssue {
                    severity: "error".to_string(),
                    file: path_str.clone(),
                    line: None,
                    message: "Workflow has no phases defined".to_string(),
                });
            }

            // Validar IDs únicos
            let mut phase_ids = HashSet::new();
            for (idx, phase) in wf.phases.iter().enumerate() {
                if phase.id.is_empty() {
                    issues.push(WorkflowValidationIssue {
                        severity: "error".to_string(),
                        file: path_str.clone(),
                        line: Some(idx + 1),
                        message: format!("Phase {} has empty ID", idx),
                    });
                }

                if !phase_ids.insert(&phase.id) {
                    issues.push(WorkflowValidationIssue {
                        severity: "error".to_string(),
                        file: path_str.clone(),
                        line: Some(idx + 1),
                        message: format!("Duplicate phase ID: {}", phase.id),
                    });
                }
            }

            // Validar referencias entre fases (inputs/outputs)
            let phase_id_set: HashSet<_> = wf.phases.iter().map(|p| &p.id).collect();
            for phase in &wf.phases {
                if let Some(inputs) = &phase.inputs {
                    for input in inputs {
                        // Verificar si el input referencia otra fase
                        if input.contains('.') {
                            let parts: Vec<&str> = input.split('.').collect();
                            if parts.len() >= 2 && !phase_id_set.contains(&parts[0].to_string()) {
                                issues.push(WorkflowValidationIssue {
                                    severity: "warning".to_string(),
                                    file: path_str.clone(),
                                    line: None,
                                    message: format!(
                                        "Phase '{}' references unknown phase in input: {}",
                                        phase.id, input
                                    ),
                                });
                            }
                        }
                    }
                }
            }

            // Validar templates existen
            let root = path.parent().unwrap_or(path);
            for phase in &wf.phases {
                if let Some(template) = &phase.prompt_template {
                    let template_path = root.join(template);
                    if !template_path.exists() {
                        issues.push(WorkflowValidationIssue {
                            severity: "warning".to_string(),
                            file: path_str.clone(),
                            line: None,
                            message: format!(
                                "Phase '{}' references missing template: {}",
                                phase.id, template
                            ),
                        });
                    }
                }
            }
        }
        Err(e) => {
            issues.push(WorkflowValidationIssue {
                severity: "warning".to_string(),
                file: path_str.clone(),
                line: None,
                message: format!("Could not parse as workflow (might be another YAML type): {}", e),
            });
        }
    }

    issues
}

/// Valida todos los workflows en un proyecto en paralelo
pub fn validate_workflows(root_path: &str) -> Result<WorkflowValidationReport, String> {
    let path = Path::new(root_path);
    if !path.is_dir() {
        return Err(format!("'{}' is not a valid directory.", root_path));
    }

    // Buscar archivos YAML
    let yaml_files = find_yaml_files(path);
    let total_files = yaml_files.len();

    if total_files == 0 {
        return Ok(WorkflowValidationReport {
            valid: true,
            total_files: 0,
            valid_files: 0,
            invalid_files: 0,
            issues: Vec::new(),
            workflows_found: Vec::new(),
            missing_templates: Vec::new(),
            summary: "No YAML files found".to_string(),
        });
    }

    // Validar archivos en paralelo
    let issues_mutex = Mutex::new(Vec::new());
    let workflows_mutex = Mutex::new(Vec::new());

    yaml_files.par_iter().for_each(|file| {
        let file_issues = validate_workflow_file(file);

        // Si no tiene errores graves, considerarlo workflow
        let has_errors = file_issues.iter().any(|i| i.severity == "error");

        if !has_errors {
            workflows_mutex.lock().unwrap().push(
                file.file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .to_string(),
            );
        }

        if !file_issues.is_empty() {
            issues_mutex.lock().unwrap().extend(file_issues);
        }
    });

    let issues = issues_mutex.into_inner().unwrap();
    let workflows_found = workflows_mutex.into_inner().unwrap();

    let invalid_files = issues
        .iter()
        .filter(|i| i.severity == "error")
        .map(|i| &i.file)
        .collect::<HashSet<_>>()
        .len();

    let valid_files = total_files - invalid_files;
    let valid = invalid_files == 0;

    // Encontrar templates faltantes
    let missing_templates: Vec<String> = issues
        .iter()
        .filter(|i| i.message.contains("missing template"))
        .map(|i| {
            // Extraer nombre del template del mensaje
            i.message
                .split(':')
                .last()
                .unwrap_or("")
                .trim()
                .to_string()
        })
        .collect::<HashSet<_>>()
        .into_iter()
        .collect();

    let summary = if valid {
        format!(
            "✅ All {} YAML files are valid. Found {} workflows.",
            total_files,
            workflows_found.len()
        )
    } else {
        format!(
            "⚠️ Found {} issues in {} files. {} workflows validated successfully.",
            issues.len(),
            invalid_files,
            workflows_found.len()
        )
    };

    Ok(WorkflowValidationReport {
        valid,
        total_files,
        valid_files,
        invalid_files,
        issues,
        workflows_found,
        missing_templates,
        summary,
    })
}
