#!/usr/bin/env bash

set -e

echo "Installing Cosmic Mixer..."

if ! command -v pipx >/dev/null; then
    echo "pipx not found. Please install pipx first."
    exit 1
fi

pipx install . --force

echo
echo "Cosmic Mixer installed successfully."
echo
echo "Run with:"
echo
echo "cosmic-mixer"