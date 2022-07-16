#!/usr/bin/env bash


# test_2
python project.py 1 19 0.01 4096 4 0.5 64 debug > output.txt
diff output.txt ./output-files/output02-full.txt
diff simout.txt ./output-files/simout02.txt

# test _3
python project.py 2 19 0.01 4096 4 0.5 64

# test _4
python project.py 8 19 0.01 4096 4 0.75 32

# test _5
python project.py 8 101 0.001 16384 4 0.5 128
