#!/usr/bin/env bash
set -euo pipefail

SOURCE_URL="https://github.com/prashxant/agents-hooks/archive/refs/heads/main.tar.gz"
TEMP_DIR="$(mktemp -d)"

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

backup ".codex/hooks.json"
backup ".codex/hooks"
backup ".agent-logger"

mkdir -p ".codex"
cp "$SOURCE_DIR/.codex/config.toml" ".codex/config.toml"
cp "$SOURCE_DIR/.codex/hooks.json" ".codex/hooks.json"
if [ -d "$SOURCE_DIR/.codex/hooks" ]; then
  cp -R "$SOURCE_DIR/.codex/hooks" ".codex/"
fi
mkdir -p ".agent-logger"
cp -R "$SOURCE_DIR/.agent-logger/." ".agent-logger/"
rm -rf ".agent-logger/state"
find ".agent-logger" -type d -name __pycache__ -prune -exec rm -rf {} +
touch log.md

echo "Agent hooks installed successfully. Logs: $(pwd)/log.md"
