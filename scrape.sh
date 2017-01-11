#!/bin/bash -xe

OBL="$1"
CODE="$2"

mkdir -p "$OBL"
time python -u get_reformagkh_data-all.py \
  -of "$OBL" \
  --extractor none \
  --shuffle \
  --fast_check \
  "$CODE" "$OBL".data \
  | tee "$OBL"/download-$(date +'%FT%T').log
