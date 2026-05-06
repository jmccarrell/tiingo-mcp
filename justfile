set dotenv-load

# Shared worktree recipes (optional).
mod? wt '~/.config/just/worktree.just'

@_:
    just --list


# ── Run ───────────────────────────────────────────────────────────────────────

# Start the MCP server (stdio transport — for use by Claude Code)
[group('run')]
serve:
    uv run tiingo-mcp

# Register this server with Claude Code (user scope — available in all projects)
[group('run')]
install-mcp:
    claude mcp add --scope user tiingo-mcp -- uv run --project {{ justfile_directory() }} tiingo-mcp


# ── QA ───────────────────────────────────────────────────────────────────────

# Run tests
[group('qa')]
test *args:
    uv run -m pytest {{ args }}

# Run linters
[group('qa')]
lint:
    uvx ruff check
    uvx ruff format --check

# Check types
[group('qa')]
typing:
    uvx ty check --python .venv src


# ── Lifecycle ─────────────────────────────────────────────────────────────────

# Install Python deps
[group('lifecycle')]
install:
    uv sync

# Remove virtualenv and caches
[group('lifecycle')]
clean:
    rm -rf .venv .pytest_cache .ruff_cache
    find . -type d -name "__pycache__" -exec rm -r {} +
