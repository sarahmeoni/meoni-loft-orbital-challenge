#!/usr/bin/env bash
#
# run-pip-compile.sh
#
# Compile pinned requirements*.txt from the requirements*.in source files
# using pip-tools. Run this whenever a dependency is added or changed.
#
set -euo pipefail

PIP_COMPILE_ARGS=(
    --allow-unsafe
    --strip-extras
    --no-emit-index-url
    --no-emit-trusted-host
    --upgrade
)

pip-compile "${PIP_COMPILE_ARGS[@]}" requirements.in
pip-compile "${PIP_COMPILE_ARGS[@]}" requirements-dev.in
