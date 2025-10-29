#!/bin/bash
### GARBAGE CLEANER BASH SCRIPT ###
# This script removes all CSV files in the current directory except for sample.csv

# Remove all csv files except sample.csv
find . -type f -name "*.csv" ! -name "sample.csv" -exec rm -f {} \;