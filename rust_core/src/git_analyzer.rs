// rust_core/src/git_analyzer.rs
//! Professional Git History Analyzer with parallel processing
//!
//! Provides comprehensive Git repository analysis:
//! - Commit history with parallel processing
//! - Branch analysis (active, stale, merged)
//! - Contributor insights (commits, impact, activity)
//! - Code churn analysis (files changed most)
//! - Development patterns (commit frequency, peak times)
//! - Architectural decisions (refactoring, migrations)
//! - Release patterns (tags, versions)

use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use std::process::Command;
use chrono::Timelike; // Added for .hour()

#[derive(Debug, Serialize, Deserialize)]
pub struct GitAnalysis {
    pub repository_info: RepositoryInfo,
    pub commit_history: CommitHistory,
    pub branch_analysis: BranchAnalysis,
    pub contributor_insights: Vec<ContributorInsight>,
    pub code_churn: CodeChurn,
    pub development_patterns: DevelopmentPatterns,
    pub architectural_decisions: Vec<ArchitecturalDecision>,
    pub release_patterns: ReleasePatterns,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RepositoryInfo {
    pub path: String,
    pub remote_url: Option<String>,
    pub default_branch: String,
    pub total_commits: usize,
    pub first_commit_date: String,
    pub last_commit_date: String,
    pub repository_age_days: i64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CommitHistory {
    pub recent_commits: Vec<CommitInfo>,
    pub commits_by_month: HashMap<String, usize>,
    pub commits_by_day_of_week: HashMap<String, usize>,
    pub average_commits_per_week: f64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CommitInfo {
    pub hash: String,
    pub author: String,
    pub email: String,
    pub date: String,
    pub message: String,
    pub files_changed: usize,
    pub insertions: usize,
    pub deletions: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BranchAnalysis {
    pub total_branches: usize,
    pub active_branches: Vec<BranchInfo>,
    pub stale_branches: Vec<BranchInfo>,
    pub merged_branches_count: usize,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct BranchInfo {
    pub name: String,
    pub last_commit_date: String,
    pub commits_ahead: usize,
    pub commits_behind: usize,
    pub is_merged: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ContributorInsight {
    pub name: String,
    pub email: String,
    pub total_commits: usize,
    pub first_commit_date: String,
    pub last_commit_date: String,
    pub lines_added: usize,
    pub lines_deleted: usize,
    pub files_modified: usize,
    pub impact_score: f64, // Weighted score based on commits + churn
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CodeChurn {
    pub most_changed_files: Vec<FileChurn>,
    pub total_files_ever_changed: usize,
    pub hotspots: Vec<String>, // Files changed frequently
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FileChurn {
    pub path: String,
    pub times_changed: usize,
    pub total_insertions: usize,
    pub total_deletions: usize,
    pub last_modified: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DevelopmentPatterns {
    pub commit_frequency: String, // "Very active", "Active", "Moderate", "Low"
    pub peak_development_hours: Vec<u8>,
    pub peak_development_days: Vec<String>,
    pub average_commit_size: f64, // Lines changed per commit
    pub median_commit_size: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ArchitecturalDecision {
    pub commit_hash: String,
    pub date: String,
    pub author: String,
    pub message: String,
    pub decision_type: String, // "refactor", "migration", "architecture", "deprecation"
    pub impact: String,        // "high", "medium", "low"
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ReleasePatterns {
    pub total_tags: usize,
    pub recent_tags: Vec<TagInfo>,
    pub average_days_between_releases: f64,
    pub release_frequency: String, // "Weekly", "Monthly", "Quarterly", "Irregular"
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TagInfo {
    pub name: String,
    pub date: String,
    pub commit_hash: String,
    pub message: String,
}

/// Analyze Git repository with parallel processing
pub fn analyze_git_repository(repo_path: &str, days: i64) -> Result<GitAnalysis, String> {
    let path = Path::new(repo_path);

    if !path.exists() {
        return Err(format!("Path does not exist: {}", repo_path));
    }

    if !path.join(".git").exists() {
        return Err(format!("Not a Git repository: {}", repo_path));
    }

    // Gather all data in parallel (nested rayon::join for 4 operations)
    let (
        (repo_info, commit_history),
        (branch_analysis, contributors)
    ) = rayon::join(
        || {
            rayon::join(
                || get_repository_info(repo_path),
                || get_commit_history(repo_path, days),
            )
        },
        || {
            rayon::join(
                || get_branch_analysis(repo_path),
                || get_contributor_insights(repo_path, days),
            )
        },
    );

    // Unwrap and clone commit_history for analysis
    let commit_hist = commit_history?;
    let code_churn = get_code_churn(repo_path, days)?;
    let dev_patterns = analyze_development_patterns(&commit_hist)?;
    let arch_decisions = find_architectural_decisions(repo_path, days)?;
    let release_patterns = analyze_release_patterns(repo_path)?;

    Ok(GitAnalysis {
        repository_info: repo_info?,
        commit_history: commit_hist,
        branch_analysis: branch_analysis?,
        contributor_insights: contributors?,
        code_churn,
        development_patterns: dev_patterns,
        architectural_decisions: arch_decisions,
        release_patterns,
    })
}

fn get_repository_info(repo_path: &str) -> Result<RepositoryInfo, String> {
    let default_branch = execute_git_command(repo_path, &["rev-parse", "--abbrev-ref", "HEAD"])?;
    let remote_url = execute_git_command(repo_path, &["config", "--get", "remote.origin.url"]).ok();

    let total_commits = execute_git_command(repo_path, &["rev-list", "--count", "HEAD"])?
        .trim()
        .parse::<usize>()
        .map_err(|e| format!("Failed to parse commit count: {}", e))?;

    let first_commit = execute_git_command(
        repo_path,
        &["log", "--reverse", "--format=%ai", "--max-count=1"],
    )?;

    let last_commit = execute_git_command(repo_path, &["log", "-1", "--format=%ai"])?;

    println!("First commit date: '{}'", first_commit.trim()); // DEBUG
    println!("Last commit date: '{}'", last_commit.trim()); // DEBUG

    // Calculate age
    let first_date = chrono::NaiveDateTime::parse_from_str(
        first_commit.trim().split_whitespace().take(2).collect::<Vec<_>>().join(" ").as_str(),
        "%Y-%m-%d %H:%M:%S"
    ).map_err(|e| format!("Failed to parse first commit date: {}", e))?;

    let last_date = chrono::NaiveDateTime::parse_from_str(
        last_commit.trim().split_whitespace().take(2).collect::<Vec<_>>().join(" ").as_str(),
        "%Y-%m-%d %H:%M:%S"
    ).map_err(|e| format!("Failed to parse last commit date: {}", e))?;

    let age_days = (last_date - first_date).num_days();

    Ok(RepositoryInfo {
        path: repo_path.to_string(),
        remote_url,
        default_branch: default_branch.trim().to_string(),
        total_commits,
        first_commit_date: first_commit.trim().to_string(),
        last_commit_date: last_commit.trim().to_string(),
        repository_age_days: age_days,
    })
}

fn get_commit_history(repo_path: &str, days: i64) -> Result<CommitHistory, String> {
    let now = chrono::Local::now();
    let since = now - chrono::Duration::days(days);
    let since_date = since.format("%Y-%m-%d").to_string();

    let log_output = execute_git_command(
        repo_path,
        &[
            "log",
            &format!("--since={}", since_date),
            "--format=%H|%an|%ae|%ai|%s",
            "--numstat",
        ],
    )?;

    let commits = parse_git_log_with_stats(&log_output);

    let mut commits_by_month: HashMap<String, usize> = HashMap::new();
    let mut commits_by_day: HashMap<String, usize> = HashMap::new();

    for commit in &commits {
        if let Some(month) = commit.date.split('-').take(2).collect::<Vec<_>>().get(0..2) {
            let month_key = month.join("-");
            *commits_by_month.entry(month_key).or_insert(0) += 1;
        }

        // Parse day of week (this is simplified; real implementation would use chrono)
        // For now, just count by date
        if let Some(date) = commit.date.split_whitespace().next() {
            *commits_by_day.entry(date.to_string()).or_insert(0) += 1;
        }
    }

    let weeks = (days as f64 / 7.0).max(1.0);
    let avg_commits_per_week = commits.len() as f64 / weeks;

    Ok(CommitHistory {
        recent_commits: commits.into_iter().take(50).collect(),
        commits_by_month,
        commits_by_day_of_week: commits_by_day,
        average_commits_per_week: avg_commits_per_week,
    })
}

fn get_branch_analysis(repo_path: &str) -> Result<BranchAnalysis, String> {
    let branches_output = execute_git_command(repo_path, &["branch", "-a", "--format=%(refname:short)|%(committerdate:iso)|%(ahead-behind:HEAD)"])?;

    let branches: Vec<BranchInfo> = branches_output
        .lines()
        .filter_map(|line| parse_branch_info(line))
        .collect();

    let active_branches: Vec<BranchInfo> = branches
        .iter()
        .filter(|b| is_branch_active(&b.last_commit_date, 30))
        .cloned()
        .collect();

    let stale_branches: Vec<BranchInfo> = branches
        .iter()
        .filter(|b| !is_branch_active(&b.last_commit_date, 30))
        .cloned()
        .collect();

    let merged_count = branches.iter().filter(|b| b.is_merged).count();

    Ok(BranchAnalysis {
        total_branches: branches.len(),
        active_branches,
        stale_branches,
        merged_branches_count: merged_count,
    })
}

fn get_contributor_insights(repo_path: &str, days: i64) -> Result<Vec<ContributorInsight>, String> {
    let now = chrono::Local::now();
    let since = now - chrono::Duration::days(days);
    let since_date = since.format("%Y-%m-%d").to_string();

    // Use git log instead of shortlog to avoid empty stdout issues
    let log_output = execute_git_command(
        repo_path,
        &[
            "log",
            &format!("--since={}", since_date),
            "--format=%aN|%aE",
        ],
    )?;

    let mut contributor_counts: HashMap<String, usize> = HashMap::new();
    let mut contributor_names: HashMap<String, String> = HashMap::new();

    for line in log_output.lines() {
        let parts: Vec<&str> = line.split('|').collect();
        if parts.len() >= 2 {
            let name = parts[0].trim();
            let email = parts[1].trim();
            let key = email.to_string();
            *contributor_counts.entry(key.clone()).or_insert(0) += 1;
            contributor_names.entry(key).or_insert(name.to_string());
        }
    }

    let contributors: Vec<ContributorInsight> = contributor_counts
        .par_iter()
        .filter_map(|(email, count)| {
            let name = contributor_names.get(email)?;
            analyze_contributor(repo_path, name, email, *count, days)
        })
        .collect();

    Ok(contributors)
}

fn get_code_churn(repo_path: &str, days: i64) -> Result<CodeChurn, String> {
    let now = chrono::Local::now();
    let since = now - chrono::Duration::days(days);
    let since_date = since.format("%Y-%m-%d").to_string();

    let log_output = execute_git_command(
        repo_path,
        &["log", &format!("--since={}", since_date), "--numstat", "--format="],
    )?;

    let mut file_changes: HashMap<String, (usize, usize, usize)> = HashMap::new(); // (times, insertions, deletions)

    for line in log_output.lines() {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 3 {
            if let (Ok(ins), Ok(del)) = (parts[0].parse::<usize>(), parts[1].parse::<usize>()) {
                let path = parts[2].to_string();
                let entry = file_changes.entry(path).or_insert((0, 0, 0));
                entry.0 += 1;
                entry.1 += ins;
                entry.2 += del;
            }
        }
    }

    let mut most_changed: Vec<(String, (usize, usize, usize))> = file_changes.into_iter().collect();
    most_changed.sort_by(|a, b| b.1.0.cmp(&a.1.0));

    let most_changed_files: Vec<FileChurn> = most_changed
        .iter()
        .take(20)
        .map(|(path, (times, ins, del))| FileChurn {
            path: path.clone(),
            times_changed: *times,
            total_insertions: *ins,
            total_deletions: *del,
            last_modified: String::new(), // Would require extra query, skipping for performance
        })
        .collect();

    let hotspots: Vec<String> = most_changed_files
        .iter()
        .filter(|f| f.times_changed > 5)
        .map(|f| f.path.clone())
        .collect();

    Ok(CodeChurn {
        most_changed_files,
        total_files_ever_changed: most_changed.len(),
        hotspots,
    })
}

fn analyze_development_patterns(commit_history: &CommitHistory) -> Result<DevelopmentPatterns, String> {
    let commit_frequency = if commit_history.average_commits_per_week > 20.0 {
        "Very active"
    } else if commit_history.average_commits_per_week > 10.0 {
        "Active"
    } else if commit_history.average_commits_per_week > 5.0 {
        "Moderate"
    } else {
        "Low"
    };

    // Calculate peak hours and days from recent commits
    let mut hour_counts: HashMap<u32, usize> = HashMap::new();
    let mut day_counts: HashMap<String, usize> = HashMap::new();
    let mut total_size = 0;
    let mut commit_sizes = Vec::new();

    for commit in &commit_history.recent_commits {
        // Parse date: 2023-10-27 10:00:00 +0000
        if let Ok(dt) = chrono::NaiveDateTime::parse_from_str(
            commit.date.split_whitespace().take(2).collect::<Vec<_>>().join(" ").as_str(),
            "%Y-%m-%d %H:%M:%S"
        ) {
            *hour_counts.entry(dt.time().hour()).or_insert(0) += 1;
            *day_counts.entry(dt.format("%A").to_string()).or_insert(0) += 1;
        }

        let size = commit.insertions + commit.deletions;
        total_size += size;
        commit_sizes.push(size);
    }

    let mut peak_hours: Vec<u8> = hour_counts.keys().map(|&h| h as u8).collect();
    peak_hours.sort_by_key(|h| std::cmp::Reverse(hour_counts.get(&(*h as u32)).unwrap_or(&0)));

    let mut peak_days: Vec<String> = day_counts.keys().cloned().collect();
    peak_days.sort_by_key(|d| std::cmp::Reverse(day_counts.get(d).unwrap_or(&0)));

    commit_sizes.sort();
    let median_size = if !commit_sizes.is_empty() {
        commit_sizes[commit_sizes.len() / 2]
    } else {
        0
    };

    let avg_size = if !commit_history.recent_commits.is_empty() {
        total_size as f64 / commit_history.recent_commits.len() as f64
    } else {
        0.0
    };

    Ok(DevelopmentPatterns {
        commit_frequency: commit_frequency.to_string(),
        peak_development_hours: peak_hours.into_iter().take(5).collect(),
        peak_development_days: peak_days.into_iter().take(3).collect(),
        average_commit_size: avg_size,
        median_commit_size: median_size,
    })
}

fn find_architectural_decisions(repo_path: &str, days: i64) -> Result<Vec<ArchitecturalDecision>, String> {
    let now = chrono::Local::now();
    let since = now - chrono::Duration::days(days);
    let since_date = since.format("%Y-%m-%d").to_string();

    let keywords = vec!["refactor", "migrate", "architecture", "deprecate", "breaking", "redesign"];

    let mut decisions = Vec::new();

    for keyword in keywords {
        let log_output = execute_git_command(
            repo_path,
            &[
                "log",
                &format!("--since={}", since_date),
                &format!("--grep={}", keyword),
                "-i",
                "--format=%H|%ai|%an|%s",
            ],
        )?;

        for line in log_output.lines() {
            if let Some(decision) = parse_architectural_decision(line, keyword) {
                decisions.push(decision);
            }
        }
    }

    Ok(decisions)
}

fn analyze_release_patterns(repo_path: &str) -> Result<ReleasePatterns, String> {
    let tags_output = execute_git_command(repo_path, &["tag", "-l", "--sort=-creatordate"])?;

    let tag_names: Vec<&str> = tags_output.lines().collect();
    let total_tags = tag_names.len();

    let recent_tags: Vec<TagInfo> = tag_names
        .iter()
        .take(10)
        .filter_map(|tag| get_tag_info(repo_path, tag))
        .collect();

    let frequency = if total_tags > 50 {
        "Weekly"
    } else if total_tags > 20 {
        "Monthly"
    } else if total_tags > 5 {
        "Quarterly"
    } else {
        "Irregular"
    };

    // Calculate average days between releases
    let mut total_days = 0;
    let mut count = 0;

    for i in 0..recent_tags.len().saturating_sub(1) {
        if let (Ok(d1), Ok(d2)) = (
            chrono::NaiveDateTime::parse_from_str(
                recent_tags[i].date.split_whitespace().take(2).collect::<Vec<_>>().join(" ").as_str(),
                "%Y-%m-%d %H:%M:%S"
            ),
            chrono::NaiveDateTime::parse_from_str(
                recent_tags[i+1].date.split_whitespace().take(2).collect::<Vec<_>>().join(" ").as_str(),
                "%Y-%m-%d %H:%M:%S"
            )
        ) {
            total_days += (d1 - d2).num_days().abs();
            count += 1;
        }
    }

    let avg_days = if count > 0 {
        total_days as f64 / count as f64
    } else {
        0.0
    };

    Ok(ReleasePatterns {
        total_tags,
        recent_tags,
        average_days_between_releases: avg_days,
        release_frequency: frequency.to_string(),
    })
}

// Helper functions

fn execute_git_command(repo_path: &str, args: &[&str]) -> Result<String, String> {
    let mut cmd_args = vec!["-C", repo_path];
    cmd_args.extend_from_slice(args);

    let output = Command::new("git")
        .args(&cmd_args)
        .output()
        .map_err(|e| format!("Failed to execute git command: {}", e))?;

    if !output.stderr.is_empty() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        // println!("Stderr: {}", stderr); // DEBUG
    }

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        if stdout.trim().is_empty() {
            println!("WARNING: Stdout is empty for command: git {}", args.join(" "));
        } else {
            // println!("Stdout: {}", stdout); // Keep commented to avoid spam, but warn on empty
        }
        Ok(stdout)
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

fn parse_git_log_with_stats(log_output: &str) -> Vec<CommitInfo> {
    let mut commits = Vec::new();
    let mut current_commit: Option<CommitInfo> = None;

    for line in log_output.lines() {
        if line.contains('|') && !line.starts_with(|c: char| c.is_numeric()) {
            // New commit line: hash|author|email|date|subject
            if let Some(commit) = current_commit.take() {
                commits.push(commit);
            }

            let parts: Vec<&str> = line.split('|').collect();
            if parts.len() >= 5 {
                current_commit = Some(CommitInfo {
                    hash: parts[0].to_string(),
                    author: parts[1].to_string(),
                    email: parts[2].to_string(),
                    date: parts[3].to_string(),
                    message: parts[4..].join("|"),
                    files_changed: 0,
                    insertions: 0,
                    deletions: 0,
                });
            }
        } else if let Some(ref mut commit) = current_commit {
            // Numstat line: insertions deletions filename
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 3 {
                if let (Ok(ins), Ok(del)) = (parts[0].parse::<usize>(), parts[1].parse::<usize>()) {
                    commit.insertions += ins;
                    commit.deletions += del;
                    commit.files_changed += 1;
                }
            }
        }
    }

    if let Some(commit) = current_commit {
        commits.push(commit);
    }

    commits
}

fn parse_branch_info(line: &str) -> Option<BranchInfo> {
    let parts: Vec<&str> = line.split('|').collect();
    if parts.len() < 3 {
        return None;
    }

    let name = parts[0].trim().to_string();
    let date = parts[1].trim().to_string();
    let ahead_behind = parts[2].trim();

    let (ahead, behind) = if let Some((a, b)) = ahead_behind.split_once(|c: char| c.is_whitespace() || c == '\t') {
        (a.parse().unwrap_or(0), b.parse().unwrap_or(0))
    } else {
        (0, 0)
    };

    Some(BranchInfo {
        name,
        last_commit_date: date,
        commits_ahead: ahead,
        commits_behind: behind,
        is_merged: false, // Simplified
    })
}

fn is_branch_active(last_commit_date: &str, days: i64) -> bool {
    if let Ok(date) = chrono::NaiveDateTime::parse_from_str(
        last_commit_date.split_whitespace().take(2).collect::<Vec<_>>().join(" ").as_str(),
        "%Y-%m-%d %H:%M:%S"
    ) {
        let now = chrono::Local::now().naive_local();
        let diff = now - date;
        diff.num_days() <= days
    } else {
        false
    }
}

fn analyze_contributor(repo_path: &str, name: &str, email: &str, commits_count: usize, days: i64) -> Option<ContributorInsight> {
    let now = chrono::Local::now();
    let since = now - chrono::Duration::days(days);
    let since_date = since.format("%Y-%m-%d").to_string();

    let stats_output = execute_git_command(
        repo_path,
        &[
            "log",
            &format!("--author={}", email),
            &format!("--since={}", since_date),
            "--numstat",
            "--format=%ai"
        ]
    );

    if let Err(e) = &stats_output {
        println!("Failed to get stats for {}: {}", email, e);
        return None;
    }
    let stats_output = stats_output.ok()?;

    let mut lines_added = 0;
    let mut lines_deleted = 0;
    let mut files_modified = 0;
    let mut first_date = String::new();
    let mut last_date = String::new();

    for stat_line in stats_output.lines() {
        if stat_line.contains('-') && stat_line.contains(':') {
            if last_date.is_empty() {
                last_date = stat_line.to_string();
            }
            first_date = stat_line.to_string();
        } else {
            let stat_parts: Vec<&str> = stat_line.split_whitespace().collect();
            if stat_parts.len() >= 2 {
                if let (Ok(ins), Ok(del)) = (stat_parts[0].parse::<usize>(), stat_parts[1].parse::<usize>()) {
                    lines_added += ins;
                    lines_deleted += del;
                    files_modified += 1;
                }
            }
        }
    }

    let impact_score = (commits_count as f64 * 10.0) + (lines_added as f64 * 0.1) + (files_modified as f64 * 0.5);

    Some(ContributorInsight {
        name: name.to_string(),
        email: email.to_string(),
        total_commits: commits_count,
        first_commit_date: first_date,
        last_commit_date: last_date,
        lines_added,
        lines_deleted,
        files_modified,
        impact_score,
    })
}

fn parse_architectural_decision(line: &str, keyword: &str) -> Option<ArchitecturalDecision> {
    let parts: Vec<&str> = line.split('|').collect();
    if parts.len() < 4 {
        return None;
    }

    let message = parts[3].to_string();

    let impact = if message.to_lowercase().contains("breaking") || message.to_lowercase().contains("major") {
        "high"
    } else if message.to_lowercase().contains("minor") || message.to_lowercase().contains("fix") {
        "low"
    } else {
        "medium"
    };

    Some(ArchitecturalDecision {
        commit_hash: parts[0].to_string(),
        date: parts[1].to_string(),
        author: parts[2].to_string(),
        message,
        decision_type: keyword.to_string(),
        impact: impact.to_string(),
    })
}

fn get_tag_info(repo_path: &str, tag: &str) -> Option<TagInfo> {
    let output = execute_git_command(
        repo_path,
        &["show", tag, "--format=%H|%ai|%s", "--no-patch"]
    ).ok()?;

    let line = output.lines().next()?;
    let parts: Vec<&str> = line.split('|').collect();
    if parts.len() < 3 {
        return None;
    }

    Some(TagInfo {
        name: tag.to_string(),
        commit_hash: parts[0].to_string(),
        date: parts[1].to_string(),
        message: parts[2].to_string(),
    })
}
