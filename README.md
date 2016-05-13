General outline of how to reverse engineer Drupal pages, to get information about node ID, content type etc, into a CSV.

* Adjust site theme to insert &lt;meta /> tags on each page, likely via a preprocess function, adding variables and then printing them in the various page.tpl.php files.

* Create a text file of all the (absolute) URLs you want to obtain debug information for

* Use the URL text file as input to the visit_pages.sh bash script, to use wget to visit, generate and download each file with embedded debug info

* Run analyse.py to process the downloaded page debug information into a CSV

