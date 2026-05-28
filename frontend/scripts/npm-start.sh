#!/bin/sh

set -e

echo "Starting frontend service..."
npm run dev -- --host
