#!/usr/bin/env bash
set -euo pipefail

SOURCE_URL="https://github.com/prashxant/agents-hooks/archive/refs/heads/main.tar.gz"
TEMP_DIR="$(mktemp -d)"
UPDATE_ONLY=false

if [ "${1:-}" = "--update" ]; then
  UPDATE_ONLY=true
elif [ -n "${1:-}" ]; then
  echo "Usage: $0 [--update]"
  exit 1
fi

cleanup() {
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

if [ ! -d ".git" ] && [ ! -f "package.json" ] && [ ! -f "README.md" ]; then
  echo "Run this installer from your project root."
  exit 1
fi

echo "Downloading agent hooks..."
curl -fsSL "$SOURCE_URL" | tar -xz -C "$TEMP_DIR"
SOURCE_DIR="$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"

backup() {
  if [ -e "$1" ]; then
    mv "$1" "$1.backup.$(date +%Y%m%d%H%M%S)"
  fi
}

if [ "$UPDATE_ONLY" = false ]; then
  backup ".codex/hooks.json"
  backup ".codex/hooks"
  backup ".agent-logger"
fi

mkdir -p ".codex"
cp "$SOURCE_DIR/.codex/config.toml" ".codex/config.toml"
cp "$SOURCE_DIR/.codex/hooks.json" ".codex/hooks.json"
if [ -d "$SOURCE_DIR/.codex/hooks" ]; then
  cp -R "$SOURCE_DIR/.codex/hooks" ".codex/"
fi
mkdir -p ".agent-logger"
cp -R "$SOURCE_DIR/.agent-logger/." ".agent-logger/"
if [ "$UPDATE_ONLY" = false ]; then
  rm -rf ".agent-logger/state"
fi
find ".agent-logger" -type d -name __pycache__ -prune -exec rm -rf {} +
touch log.md

if [ "$UPDATE_ONLY" = true ]; then
  echo "Agent hooks updated successfully. Logs: $(pwd)/log.md"
else
  echo "Agent hooks installed successfully. Logs: $(pwd)/log.md"
fi
