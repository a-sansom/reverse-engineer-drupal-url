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
    <meta name="content_type" content="article" />
    <meta name="node_id" content="12345" />
    <meta name="node_url" content="http://example.org/a/b/c" />
    <meta name="uri" content="/a/b/c" />
    <meta name="absolute_uri" content="http://example.org/a/b/c" />
    <meta name="template" content="page.tpl.php" />
    ...

    The resulting 'nodes.csv' file contains rows in the format:

    <node_id>,<node_url>,<content_type>,<template>,<uri>,<absolute_uri>

    Prerequisites:

    sudo apt-get install python-bs4

    Developed with Python 2.7.3
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
            soup = BeautifulSoup(open(name))
            # Get the debug tags
            tags = soup.find_all(self.meta_tag_filter)
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
            if tag['name'] == 'node_id':
                node['node_id'] = tag['content']

            elif tag['name'] == 'node_url':
                node['node_url'] = tag['content']

            elif tag['name'] == 'content_type':
                node['content_type'] = tag['content']

            elif tag['name'] == 'template':
                node['template'] = tag['content']

            elif tag['name'] == 'uri':
                node['uri'] = tag['content']

            elif tag['name'] == 'absolute_uri':
                node['absolute_uri'] = tag['content']

        return node

    def meta_tag_filter(self, tag):
        """Identify if we're interested in a particular tag."""
        if tag.name == 'meta':
            if tag.has_attr('name') and tag.has_attr('content'):
                if tag['name'] in self.debug_tag_names:
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
                'Path to downloaded pages "{}" does not exist'.format(path)
            )

        nodes = glob.iglob(path + '/*')

        for file in nodes:
            yield file

    def serialise(self, node):
        """Append node data to CSV file."""
        path = self.csv_output_path()

        if not os.path.exists(path):
            raise Exception(
                'Path to output CSV "{}" does not exist'.format(path)
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
                print "'UNKNOWN' content type: {} ({})".format(
                    node['file'], node['absolute_uri']
                )

        # Sort the dictionary of content types and occurrences, and display.
        for content_type in sorted(summary.iterkeys()):
            count = summary[content_type]
            page_count += count

            print '{0:50}: {1}'.format(content_type, count)

        print 'Total pages: {0}'.format(page_count)

if __name__ == "__main__":
    """ Retrieve debug info from wget downloaded pages into a CSV file.

    CLI parameters are:

        date in YYYYMMDD format
        time in HHMMSS format

    Where the directory path to read downloaded files from is
    "./YYYYMMDD/HHMMSS/pages".

    Usage:

        python analyse.py 20160509 150745
    """

    datestamp = sys.argv[1]
    timestamp = sys.argv[2]

    page_reader = WgetPageReader(datestamp, timestamp)
    page_reader.process_pages()
    page_reader.summarise()
