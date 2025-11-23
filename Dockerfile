# ═══════════════════════════════════════════════════════════
# Nexus AI - Multi-Stage Docker Build
# ═══════════════════════════════════════════════════════════
# Stage 1: Rust Builder - Compile high-performance modules
# Stage 2: Python Runtime - Final lightweight image
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# Stage 1: Rust Builder
# ═══════════════════════════════════════════════════════════
FROM rust:1.75-slim as rust-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy Rust project files
COPY rust_core/Cargo.toml rust_core/Cargo.lock ./
COPY rust_core/src ./src

# Configure cargo for faster builds and retries
ENV CARGO_NET_RETRY=10
ENV CARGO_HTTP_TIMEOUT=600

# Build Rust module in release mode
RUN cargo build --release

# Verify output exists
RUN ls -lh target/release/ && \
    test -f target/release/libcde_rust_core.so || \
    (echo "ERROR: Rust library not found!" && exit 1)

# ═══════════════════════════════════════════════════════════
# Stage 2: Python Runtime
# ═══════════════════════════════════════════════════════════
FROM python:3.14-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libssl3 \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash nexus && \
    mkdir -p /app /app/workspaces /app/.cde /app/logs && \
    chown -R nexus:nexus /app

# Set working directory
WORKDIR /app

# Copy Python requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install maturin for building wheel
RUN pip install --no-cache-dir maturin==1.7.4

# Copy Rust compiled library from builder
COPY --from=rust-builder /build/target/release/libcde_rust_core.so /usr/local/lib/
RUN ldconfig

# Copy Rust source for maturin (needed for wheel building)
COPY --from=rust-builder /build /app/rust_core
WORKDIR /app/rust_core

# Build and install Python wheel
RUN maturin build --release --interpreter python3.14 && \
    pip install --no-cache-dir target/wheels/*.whl && \
    python -c "import cde_rust_core; print('✅ Rust module loaded successfully')"

# Copy application code
WORKDIR /app
COPY src/ ./src/
COPY .cde/ ./.cde/
COPY specs/ ./specs/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/workspaces /app/logs /app/.cde/state

# Set ownership
RUN chown -R nexus:nexus /app

# Switch to non-root user
USER nexus

# Expose FastMCP server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import cde_rust_core; from src.cde_orchestrator.domain.agent_manager import AgentManager; print('OK')" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    WORKER_POOL_SIZE=3 \
    PYTHONPATH=/app

# Entrypoint
CMD ["python", "src/server.py"]
