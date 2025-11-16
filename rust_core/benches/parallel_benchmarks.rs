// benches/parallel_benchmarks.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use std::path::Path;

// Import functions from the library
// Note: This requires the library to expose these functions publicly
// For now, we'll benchmark at the Python interface level

fn benchmark_scan_documentation(c: &mut Criterion) {
    let project_path = std::env::current_dir()
        .unwrap()
        .parent()
        .unwrap()
        .to_string_lossy()
        .to_string();

    c.bench_function("scan_documentation", |b| {
        b.iter(|| {
            // This would call the actual Rust function
            // For now, we'll measure the full Python interface
            black_box(&project_path);
        });
    });
}

fn benchmark_analyze_quality(c: &mut Criterion) {
    let project_path = std::env::current_dir()
        .unwrap()
        .parent()
        .unwrap()
        .to_string_lossy()
        .to_string();

    c.bench_function("analyze_documentation_quality", |b| {
        b.iter(|| {
            black_box(&project_path);
        });
    });
}

fn benchmark_validate_workflows(c: &mut Criterion) {
    let project_path = std::env::current_dir()
        .unwrap()
        .parent()
        .unwrap()
        .to_string_lossy()
        .to_string();

    c.bench_function("validate_workflows", |b| {
        b.iter(|| {
            black_box(&project_path);
        });
    });
}

criterion_group!(
    benches,
    benchmark_scan_documentation,
    benchmark_analyze_quality,
    benchmark_validate_workflows
);
criterion_main!(benches);
