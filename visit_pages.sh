#!/bin/bash

# Date in YYYYMMDD format
today=$(date +"%Y%m%d")
# Time we're starting harvesting data
start_time=$(date +"%H%M%S")
# Output directory
output_dir=./$today/$start_time
# Where to put the visited pages
page_output_dir=./$output_dir/pages
# Log file
log_file=./$output_dir/visit_pages.log
# File containing the URLs is first an only script parameter
input_file=$1

echo "Input file is: $input_file"
echo "Output dir is: $output_dir"
echo "Started at $today $start_time"

# If input file doesn't exist, exit with error message
if [ ! -f $input_file ]; then
    echo "Error: Provided input file does not exist"
    exit 1
fi

# If output dir doesn't yet exist, create it
if [ ! -d "$page_output_dir" ]; then
  `mkdir -p $page_output_dir`
fi

# Now we've got input file with URLs for each page, and the output dir exists...
# Use wget to:
# Request for each line in the input file
# Log each request to a log file
# Retry requests up to 5 times
# Delay for 1 second between each request
# Store the each request response in the $page_output_dir directory
# The --no-proxy ignores any environment proxies set up.
wget --no-proxy -a $log_file -i $input_file -t 5 -w 1 -P $page_output_dir

# Show we're done
echo "Finished at $(date +"%Y%m%d %H%M%S")"
