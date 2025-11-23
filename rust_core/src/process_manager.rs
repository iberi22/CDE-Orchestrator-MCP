// rust_core/src/process_manager.rs
//! Process management for parallel agent execution
//!
//! This module provides high-performance process spawning and monitoring
//! for CLI-based AI agents using Rayon (parallelization) and Tokio (async I/O).

use pyo3::prelude::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command as TokioCommand;

/// Represents a spawned agent process
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentProcess {
    pub pid: u32,
    pub command: String,
    pub status: ProcessStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProcessStatus {
    Running,
    Completed { exit_code: i32 },
    Failed { error: String },
}

/// Spawn multiple CLI agents in parallel using Rayon
///
/// # Arguments
/// * `commands` - List of commands to execute, each as Vec<String>
///
/// # Returns
/// * Vec of spawned process information
///
/// # Example
/// ```python
/// commands = [
///     ["gh", "copilot", "suggest", "create auth"],
///     ["gemini", "generate", "add tests"]
/// ]
/// processes = rust_utils.spawn_agents_parallel(commands)
/// ```
#[pyfunction]
pub fn spawn_agents_parallel(commands: Vec<Vec<String>>) -> PyResult<Vec<AgentProcess>> {
    let results: Vec<AgentProcess> = commands
        .par_iter()
        .map(|cmd| {
            if cmd.is_empty() {
                return AgentProcess {
                    pid: 0,
                    command: String::new(),
                    status: ProcessStatus::Failed {
                        error: "Empty command".to_string(),
                    },
                };
            }

            match spawn_agent_sync(cmd) {
                Ok(process) => process,
                Err(e) => AgentProcess {
                    pid: 0,
                    command: cmd.join(" "),
                    status: ProcessStatus::Failed {
                        error: e.to_string(),
                    },
                },
            }
        })
        .collect();

    Ok(results)
}

/// Spawn a single agent synchronously
fn spawn_agent_sync(cmd: &[String]) -> Result<AgentProcess, std::io::Error> {
    let mut command = Command::new(&cmd[0]);
    command
        .args(&cmd[1..])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Windows-specific: Use cmd.exe if command starts with "cmd"
    #[cfg(windows)]
    if cmd[0].to_lowercase() == "cmd" {
        command.creation_flags(0x08000000); // CREATE_NO_WINDOW
    }

    let child = command.spawn()?;
    let pid = child.id();

    Ok(AgentProcess {
        pid,
        command: cmd.join(" "),
        status: ProcessStatus::Running,
    })
}

/// Spawn agent with async log streaming (Tokio)
///
/// # Arguments
/// * `command` - Command to execute as Vec<String>
/// * `callback` - Python callback for log lines (optional)
///
/// # Returns
/// * Process ID and initial status
#[pyfunction]
pub fn spawn_agent_async(command: Vec<String>) -> PyResult<AgentProcess> {
    if command.is_empty() {
        return Ok(AgentProcess {
            pid: 0,
            command: String::new(),
            status: ProcessStatus::Failed {
                error: "Empty command".to_string(),
            },
        });
    }

    // Spawn in tokio runtime (requires tokio::main elsewhere)
    let rt = tokio::runtime::Runtime::new().unwrap();
    let result = rt.block_on(async {
        let mut cmd = TokioCommand::new(&command[0]);
        cmd.args(&command[1..])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        #[cfg(windows)]
        if command[0].to_lowercase() == "cmd" {
            cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
        }

        let mut child = cmd.spawn().map_err(|e| e.to_string())?;
        let pid = child.id().unwrap_or(0);

        // Spawn log streaming task
        if let Some(stdout) = child.stdout.take() {
            tokio::spawn(async move {
                let reader = BufReader::new(stdout);
                let mut lines = reader.lines();
                while let Ok(Some(line)) = lines.next_line().await {
                    eprintln!("[Agent {}] {}", pid, line);
                }
            });
        }

        if let Some(stderr) = child.stderr.take() {
            tokio::spawn(async move {
                let reader = BufReader::new(stderr);
                let mut lines = reader.lines();
                while let Ok(Some(line)) = lines.next_line().await {
                    eprintln!("[Agent {} ERROR] {}", pid, line);
                }
            });
        }

        Ok::<AgentProcess, String>(AgentProcess {
            pid,
            command: command.join(" "),
            status: ProcessStatus::Running,
        })
    });

    result.map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))
}

/// Monitor process health (CPU, memory usage)
///
/// # Arguments
/// * `pid` - Process ID to monitor
///
/// # Returns
/// * JSON string with health metrics
#[pyfunction]
pub fn monitor_process_health(pid: u32) -> PyResult<String> {
    use sysinfo::{Pid, System};

    let mut system = System::new_all();
    system.refresh_all();

    let pid = Pid::from_u32(pid);

    if let Some(process) = system.process(pid) {
        let health = serde_json::json!({
            "pid": pid.as_u32(),
            "status": "running",
            "cpu_usage": process.cpu_usage(),
            "memory_mb": process.memory() / 1024 / 1024,
            "disk_usage_bytes": process.disk_usage().total_written_bytes,
        });

        Ok(health.to_string())
    } else {
        Ok(serde_json::json!({
            "pid": pid.as_u32(),
            "status": "not_found",
        })
        .to_string())
    }
}

/// Kill process by PID (cross-platform)
#[pyfunction]
pub fn kill_process(pid: u32) -> PyResult<bool> {
    use sysinfo::{Pid, System};

    let mut system = System::new_all();
    system.refresh_all();

    let pid = Pid::from_u32(pid);

    if let Some(process) = system.process(pid) {
        Ok(process.kill())
    } else {
        Ok(false)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spawn_agents_parallel() {
        let commands = vec![
            vec!["echo".to_string(), "test1".to_string()],
            vec!["echo".to_string(), "test2".to_string()],
        ];

        let result = spawn_agents_parallel(commands);
        assert!(result.is_ok());
        let processes = result.unwrap();
        assert_eq!(processes.len(), 2);
    }
}
