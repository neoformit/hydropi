#!/usr/bin/env bash

rm -r build hydropi.egg-info
pip uninstall hydropi
pip install --no-cache-dir .
