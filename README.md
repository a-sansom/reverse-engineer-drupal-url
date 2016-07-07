Outline of how to reverse engineer Drupal pages, to get information about node ID, content type etc, into a CSV.

* Insert code that generates debug markup tags when a page is visited by downloading and enabling the relevant Drupal module in the `drupal` subdirectory

* Create a text file of all the (absolute) URLs you want to obtain debug information for, eg. `urls.csv`

* Use the `urls.csv` file as input to the `visit_pages.sh` bash script, to use wget to visit, generate and download each file with embedded debug info

* Run `analyse.py YYYYMMDD HHMMSS` (or `analyse.rb YYYYMMDD HHMMSS`) to process the downloaded page debug information into a `nodes.csv` file for any further analysis/processing

`analyse.py`/`analyse.rb` example output (along with `nodes.csv` in the directory noted below):

```
article                                           : 56
page                                              : 9
webform                                           : 123
Total pages                                       : 188
See output CSV in ./20160525/112610
```

If you need to use a logged in Drupal user for various pages:

* Open Firefox, and install the [Export Cookies](https://addons.mozilla.org/en-US/firefox/addon/export-cookies/) add-on
* Clear existing cookies
* Log in to the Drupal site
* Export your cookies using the add-on
* Overwrite the default (empty) `cookies.txt` file in this directory
* Run the `visit_pages.sh` script as usual
