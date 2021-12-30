#!/usr/bin/env bash

if [[ ! 'hydroweb' in $PS1 ]]; then
    echo "Forget to activate conda environment?"
    exit 0;
fi

rm -r build hydropi.egg-info
pip uninstall hydropi
pip install --no-cache-dir .
