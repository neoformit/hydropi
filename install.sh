#!/usr/bin/env bash

if [ "$USER" = 'pi' ]; then
    source /home/pi/hydro/venv/bin/activate
else
    source ~/programs/anaconda/etc/profile.d/conda.sh
    conda activate hydroweb
fi

rm -r build hydropi.egg-info
pip uninstall --no-input hydropi
pip install --no-cache-dir .
