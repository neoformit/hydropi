#!/usr/bin/env bash

source ~/programs/anaconda/etc/profile.d/conda.sh
conda activate hydroweb

rm -r build hydropi.egg-info
pip uninstall hydropi
pip install --no-cache-dir .
