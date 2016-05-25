General outline of how to reverse engineer Drupal pages, to get information about node ID, content type etc, into a CSV.

* Insert code that generates debug markup tags when a page is visited

* Create a text file of all the (absolute) URLs you want to obtain debug information for, eg. `urls.csv`

* Use the `urls.csv` file as input to the `visit_pages.sh` bash script, to use wget to visit, generate and download each file with embedded debug info

* Run `analyse.py` to process the downloaded page debug information into a `nodes.csv` file for any further analysis/processing

