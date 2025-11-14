#!/bin/bash

mkdir -p fig/out

python3 fig/plot_error_detection.py --out=fig/out/error-detection.svg
python3 fig/plot_end_to_end.py --out=fig/out/end-to-end.svg
python3 fig/plot_lookup_table_coverage.py --out=fig/out/lookup-table-coverage.svg
python3 fig/plot_distillation_lifetime.py --out=fig/out/distillation-lifetime-{}.svg
python3 fig/plot_distillation_overhead.py --out=fig/out/distillation-overhead.svg
python3 fig/plot_msc_qubit_count.py --out=fig/out/msc-qubit-count.svg
python3 fig/plot_msc_survival_probability.py --out=fig/out/msc-survival-probability.svg

for i in fig/out/*.svg; do
  out=`echo $i | sed s/svg/pdf/g`
  echo Converting $i to $out...
  inkscape $i -o $out
done
