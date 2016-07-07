require 'nokogiri'
require 'csv'

# Class to extract Drupal debug information from a set of wget downloaded
# pages, to CSV.
#
# Given a set of wget downloaded pages, that have had debug tags added
# to them, gather the debug information from them and write it to a file.
#
# Example tags added to downloaded file(s):
#
#   ...
#   <div class="" style="display: none;">
#     <div class="debug-data-item" data-name="content_type" data-value="article"></div>
#     <div class="debug-data-item" data-name="node_id" data-value="12345"></div>
#     <div class="debug-data-item" data-name="node_url" data-value="http://example.org/a/b/c"></div>
#     <div class="debug-data-item" data-name="uri" data-value="/a/b/c"></div>
#     <div class="debug-data-item" data-name="absolute_uri" data-value="http://example.org/a/b/c"></div>
#     <div class="debug-data-item" data-name="template" data-value="page.tpl.php"></div>
#   </div>
#   ...
#
# The resulting 'nodes.csv' file contains rows in the format:
#
# <node_id>,<node_url>,<content_type>,<template>,<uri>,<absolute_uri>

class WgetPageReader

  # Set up instance variables.
  def initialize(datestamp, timestamp)
    @base_path = File.join(datestamp, timestamp)
    @datestamp = datestamp
    @timestamp = timestamp
    @nodes = []
    reset_csv
  end

  # Remove the output CSV if it already exists.
  def reset_csv()
    node_file = File.join(csv_output_path, 'nodes.csv')
    File.delete(node_file) if File.exist?(node_file)
  end

  # Process the downloaded pages, pulling out the debug information.
  def process_pages()
    unless Dir.exist?(node_files_path)
      raise "Path to downloaded pages '#{node_files_path}' does not exist"
    end

    Dir.glob(File.join(node_files_path, '*')) do |file_name|
      puts "Processing: #{file_name}"

      document = File.open(file_name) { |f| Nokogiri::HTML(f) }
      elements = document.xpath("//div[@class = 'debug-data-item']")
      node_data = Hash.new

      elements.each do |e|
        name = e['data-name']
        value = e['data-value']
        node_data[name] = value
      end

      @nodes << node_data
      serialise(node_data)
    end
  end

  # Return path to where to output the CSV file.
  def csv_output_path()
    return @base_path
  end

  # Return the path to where the wget downloaded files are to be read from.
  def node_files_path()
    return File.join(@base_path, 'pages')
  end

  # Write extracted debug data to CSV file.
  def serialise(node_data)
    unless Dir.exist?(csv_output_path)
      raise "Path to output CSV '#{csv_output_path}' does not exist"
    end

    CSV.open(File.join(csv_output_path, 'nodes.csv'), "a") do |csv_file|
      # Set empty strings to nil so that CSV empty field behaviour
      # matches Python version Ie non-quoted.
      node_data.map {|k, v|
        if v.to_s == ''
          node_data[k] = nil
        end
      }

      # Output the hash data to the CSV in a certain order (data.values is unordered).
      row = [node_data['node_id'], node_data['node_url'], node_data['content_type'], node_data['template'], node_data['uri'], node_data['absolute_uri']]
      csv_file << row
    end
  end

  # Print a summary of the processed files, listing node types and frequency.
  def summarise()
    summary = Hash.new
    page_count = 0

    @nodes.each {|node|
      if summary.include?(node['content_type'])
        summary[node['content_type']] += 1
      else
        summary[node['content_type']] = 1
      end
    }

    summary.keys.sort.each {|node_type|
      count = summary[node_type].to_i
      page_count += count
      puts "%-50s: %s" % [node_type, count]
    }

    puts "%-50s: %s" % ['Total pages:', page_count]
    puts "See output CSV in #{csv_output_path}"
  end
end

# Retrieve debug info from wget downloaded pages into a CSV file.
#
# CLI parameters are:
#
#   date in YYYYMMDD format
#   time in HHMMSS format
#
# Where the directory path to read downloaded files from is
# "./YYYYMMDD/HHMMSS/pages".
#
# Usage:
#
#   ruby analyse.rb 20160525 112610
#
page_reader = WgetPageReader.new(ARGV[0], ARGV[1])
page_reader.process_pages()
page_reader.summarise()
