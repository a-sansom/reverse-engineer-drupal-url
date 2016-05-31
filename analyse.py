import sys
import os
import csv
import glob
from bs4 import BeautifulSoup
import re


class WgetPageReader:
    """Extract Drupal debug info from set of wget downloaded pages to CSV.

    Given a set of wget downloaded pages, that have had debug tags added
    to them, gather the debug information from them and write it to a file.

    Example tags added to downloaded file(s):

    ...
    <div class="" style="display: none;">
      <div class="debug-data-item" data-name="content_type" data-value="article"></div>
      <div class="debug-data-item" data-name="node_id" data-value="12345"></div>
      <div class="debug-data-item" data-name="node_url" data-value="http://example.org/a/b/c"></div>
      <div class="debug-data-item" data-name="uri" data-value="/a/b/c"></div>
      <div class="debug-data-item" data-name="absolute_uri" data-value="http://example.org/a/b/c"></div>
      <div class="debug-data-item" data-name="template" data-value="page.tpl.php"></div>
    </div>
    ...

    The resulting 'nodes.csv' file contains rows in the format:

    <node_id>,<node_url>,<content_type>,<template>,<uri>,<absolute_uri>

    Developed with Python 2.7.3 and BeautifulSoup 4.4.1
    """

    def __init__(self, datestamp, timestamp):
        """Class set up tasks."""
        self.base_path = './' + datestamp + '/' + timestamp
        self.debug_tag_names = ['node_id', 'node_url', 'content_type',
            'template', 'uri', 'absolute_uri',
        ]
        self.nodes = []
        self.reset_csv()

    def reset_csv(self):
        """Remove any existing file, if it exists from previous run."""
        path = self.csv_output_path()
        file = path + '/nodes.csv'

        if os.path.isfile(file):
            os.remove(file)

    def process_pages(self):
        """ Read the downloaded pages, hoover up info and write to CSV."""
        # For each file...
        for name in self.node_files():
            # Some kind of progress indicator
            print name
            # Make the soup
            soup = BeautifulSoup(open(name), 'lxml')
            # Get the debug tags
            tags = soup.find_all(self.debug_tag_filter)

            # Accrue node data we're interested in
            node = self.format_page_data(name, tags)

            # We should now have data for all pages that have had debug info
            # injected, but flag up any that haven't got what's expected
            if node['content_type'] == '':
                print 'Page "{0}" missing debug data'.format(name)
                print node
                node['content_type'] = 'NO_DEBUG_DATA'

            # Store node info, we'll summarise data later
            self.nodes.append(node)
            # Write/append the data to CSV
            self.serialise(node)

    def format_page_data(self, name, tags):
        """ Format the page debug info."""
        node = dict.fromkeys(self.debug_tag_names, '')
        node['file'] = name

        for tag in tags:
            if tag['data-name'] == 'node_id':
                node['node_id'] = tag['data-value']

            elif tag['data-name'] == 'node_url':
                node['node_url'] = tag['data-value']

            elif tag['data-name'] == 'content_type':
                node['content_type'] = tag['data-value']

            elif tag['data-name'] == 'template':
                node['template'] = tag['data-value']

            elif tag['data-name'] == 'uri':
                node['uri'] = tag['data-value']

            elif tag['data-name'] == 'absolute_uri':
                node['absolute_uri'] = tag['data-value']

        return node

    def debug_tag_filter(self, tag):
        """Identify if we're interested in a particular tag."""
        if tag.name == 'div':
            if tag.has_attr('class') and tag.has_attr('data-name') and tag.has_attr('data-value'):
                if 'debug-data-item' in tag['class'] and tag['data-name'] in self.debug_tag_names:
                    return True

        return False

    def node_files_path(self):
        """Return the path to where the wget downloaded pages are."""
        return self.base_path + '/pages'

    def csv_output_path(self):
        """Return the path to where the produced CSV will go."""
        return self.base_path

    def node_files(self):
        """List the wget downloaded files, one at a time."""
        path = self.node_files_path()

        if not os.path.exists(path):
            raise Exception(
                'Path to downloaded pages "{0}" does not exist'.format(path)
            )

        nodes = glob.iglob(path + '/*')

        for file in nodes:
            yield file

    def serialise(self, node):
        """Append node data to CSV file."""
        path = self.csv_output_path()

        if not os.path.exists(path):
            raise Exception(
                'Path to output CSV "{0}" does not exist'.format(path)
            )

        with open(path + '/nodes.csv', 'a') as csvfile:
            fields = self.debug_tag_names

            writer = csv.DictWriter(csvfile, fieldnames=fields, restval='',
                extrasaction='ignore', quoting=csv.QUOTE_MINIMAL,
                lineterminator='\n')
            writer.writerow(node)

    def summarise(self):
        """Summarise the node info."""
        summary = {}
        page_count = 0

        for node in self.nodes:
            if node['content_type'] not in summary:
                summary[node['content_type']] = 1
            else:
                summary[node['content_type']] += 1

            # If we're dealing with some kind of special case, highlight it
            # and we'll need to analyse for a bit more info.
            if node['content_type'] == 'UNKNOWN':
                print "'UNKNOWN' content type: {0} ({1})".format(
                    node['file'], node['absolute_uri']
                )

        # Sort the dictionary of content types and occurrences, and display.
        for content_type in sorted(summary.iterkeys()):
            count = summary[content_type]
            page_count += count

            print '{0:50}: {1}'.format(content_type, count)

        print '{0:50}: {1}'.format('Total pages', page_count)
        print 'See output CSV in {0}'.format(self.csv_output_path())

if __name__ == "__main__":
    """ Retrieve debug info from wget downloaded pages into a CSV file.

    CLI parameters are:

        date in YYYYMMDD format
        time in HHMMSS format

    Where the directory path to read downloaded files from is
    "./YYYYMMDD/HHMMSS/pages".

    Usage:

        python analyse.py 20160525 112610
    """

    datestamp = sys.argv[1]
    timestamp = sys.argv[2]

    page_reader = WgetPageReader(datestamp, timestamp)
    page_reader.process_pages()
    page_reader.summarise()
