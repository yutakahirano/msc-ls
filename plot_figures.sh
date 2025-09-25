#!/bin/bash

mkdir -p fig/out

python3 fig/plot_error_detection.py --out=fig/out/error-detection.svg
python3 fig/plot_end_to_end.py --out=fig/out/end-to-end.svg
python3 fig/plot_lookup_table_coverage.py --out=fig/out/lookup-table-coverage.svg

for i in fig/out/*.svg; do
  out=`echo $i | sed s/svg/pdf/g`
  echo Converting $i to $out...
  inkscape $i -o $out
done
