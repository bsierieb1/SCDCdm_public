"""
This script is used to submit simulation jobs with the parameters used in the big benchmarking study
to the server they were conducted on.

The first part specifies the parameter sequences as nested lists.
The second part builds a bash script that submits a job to the slurm queue.
"""

import sys
import numpy as np
import os

from scdcdm.util import data_generation as gen

np.random.seed(1234)

# General parameters
cases = [1]
K = [5]
n_samples = [[i+1, i+1] for i in range(10)]
n_total = [5000]
num_results = [2e4]

# Get Parameter tuples: b: base composition; w: effect
b = []
for y1_0 in [200, 400, 600, 800, 1000]:
    b.append(np.round(gen.counts_from_first(y1_0, 5000, 5), 3))

b_w_dict = {}
i = 0
for b_i in b:
    b_t = np.round(np.log(b_i / 5000), 3)
    w_t = []
    for change in [b_i[0]/3, b_i[0]/2, b_i[0], b_i[0]*2, b_i[0]*3]:
        _, w = gen.b_w_from_abs_change(b_i, change, 5000)
        w_t.append(np.round(w, 3))
    b_w_dict[i] = (b_t, w_t)
    i += 1

#%%
# Create bash script to execute run_one_job.py
count = 0
for i in range(5):
    b = b_w_dict[i][0].tolist()
    for w in b_w_dict[i][1]:
        print(b)
        print(w)
        for n in range(20):
            with open("/home/icb/johannes.ostner/compositional_diff/compositionalDiff-johannes_tests_2/paper_simulation_scripts/comp_schedule_script_" + str(count) + ".sh", "w") as fh:
                fh.writelines("#!/bin/bash\n")
                fh.writelines("#SBATCH -o /home/icb/johannes.ostner/compositional_diff/compositionalDiff-johannes_tests_2/benchmark_results/out_" + str(count) + ".o\n")
                fh.writelines("#SBATCH -e /home/icb/johannes.ostner/compositional_diff/compositionalDiff-johannes_tests_2/benchmark_results/error_" + str(count) + ".e\n")
                fh.writelines("#SBATCH -p icb_cpu\n")
                fh.writelines("#SBATCH --exclude=ibis-ceph-[002-006,008-019],ibis216-010-[011-012,020-037,051,064],icb-rsrv[05-06,08],ibis216-224-[010-011]\n")
                fh.writelines("#SBATCH --constraint='opteron_6378'")
                fh.writelines("#SBATCH -c 1\n")
                fh.writelines("#SBATCH --mem=5000\n")
                fh.writelines("#SBATCH --nice=100\n")
                fh.writelines("#SBATCH -t 2-00:00:00\n")
                fh.writelines("/home/icb/johannes.ostner/anaconda3/bin/python /home/icb/johannes.ostner/compositional_diff/compositionalDiff-johannes_tests_2/paper_simulation_scripts/run_one_job_comp.py " +
                        str(cases).replace(" ", "") + " " +
                        str(K).replace(" ", "") + " " +
                        str(n_total).replace(" ", "") + " " +
                        str(n_samples).replace(" ", "") + " " +
                        str([b]).replace(" ", "") + " " +
                        str([[w.tolist()]]).replace(" ", "") + " " +
                        str(num_results).replace(" ", "") + " " +
                        str(n).replace(" ", ""))

            os.system("sbatch /home/icb/johannes.ostner/compositional_diff/compositionalDiff-johannes_tests_2/paper_simulation_scripts/comp_schedule_script_" + str(count) + ".sh")
            count += 1
