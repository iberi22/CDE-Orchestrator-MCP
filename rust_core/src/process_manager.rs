// rust_core/src/process_manager.rs
//! Process management for parallel agent execution

use pyo3::prelude::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command as TokioCommand;

#[cfg(windows)]
use std::os::windows::process::CommandExt;

/// Represents a spawned agent process
#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentProcess {
    #[pyo3(get)]
    pub pid: u32,
    #[pyo3(get)]
    pub command: String,
    #[pyo3(get)]
    pub status: String,
}

/// Spawn multiple CLI agents in parallel using Rayon
#[pyfunction]
pub fn spawn_agents_parallel(commands: Vec<Vec<String>>) -> PyResult<String> {
    let results: Vec<AgentProcess> = commands
        .par_iter()
        .map(|cmd| {
            if cmd.is_empty() {
                return AgentProcess {
                    pid: 0,
                    command: String::new(),
                    status: "failed_empty".to_string(),
                };
            }

            match spawn_agent_sync(cmd) {
                Ok(process) => process,
                Err(e) => AgentProcess {
                    pid: 0,
                    command: cmd.join(" "),
                    status: format!("failed_{}", e),
                },
            }
        })
        .collect();

    serde_json::to_string(&results)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Serialization error: {}", e)))
}

fn spawn_agent_sync(cmd: &[String]) -> Result<AgentProcess, std::io::Error> {
    let mut command = Command::new(&cmd[0]);
    command
        .args(&cmd[1..])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    #[cfg(windows)]
    if cmd[0].to_lowercase() == "cmd" {
        command.creation_flags(0x08000000);
    }

    let child = command.spawn()?;
    let pid = child.id();

    Ok(AgentProcess {
        pid,
        command: cmd.join(" "),
        status: "running".to_string(),
    })
}

/// Spawn agent with async log streaming
#[pyfunction]
pub fn spawn_agent_async(command: Vec<String>) -> PyResult<String> {
    if command.is_empty() {
        return Ok(serde_json::json!({
            "pid": 0,
            "command": "",
            "status": "failed_empty",
        }).to_string());
    }

    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Runtime error: {}", e)))?;

    let result = rt.block_on(async {
        let mut cmd = TokioCommand::new(&command[0]);
        cmd.args(&command[1..])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        #[cfg(windows)]
        if command[0].to_lowercase() == "cmd" {
            cmd.creation_flags(0x08000000);
        }

        let mut child = cmd.spawn().map_err(|e| e.to_string())?;
        let pid = child.id().unwrap_or(0);

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

        Ok::<serde_json::Value, String>(serde_json::json!({
            "pid": pid,
            "command": command.join(" "),
            "status": "running",
        }))
    });

    match result {
        Ok(json) => Ok(json.to_string()),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e)),
    }
}

/// Monitor process health
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

/// Kill process by PID
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
