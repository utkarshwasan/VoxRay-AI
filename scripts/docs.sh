#!/bin/bash

# Documentation helper scripts

case "$1" in
    build)
        echo "Building documentation..."
        # Requires mkdocs-material
        mkdocs build
        ;;
    serve)
        echo "Starting documentation server..."
        mkdocs serve
        ;;
    *)
        echo "Usage: $0 {build|serve}"
        exit 1
        ;;
esac
