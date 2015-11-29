# Burp pyTemplate Extension

## Description 

This Burp extension generates automatically a minimalist Python script replaying any request(s) seen in Burp:
  * In "Proxy"
  * In "Repeater"
  * In "Site map"

The generated Python script can then be used as a basis to write more advanced injection exploitation script (complex SQL injection, recursive local files download, site crawling ...)

## Features

  * Multiple requests support (cookies are stored and forwarded)
  * GET/POST support
  * HTTP headers are replayed as they were in the original request
  * SSL support
  * Returns: response code, response time, response body

## Requirements

  * Python 2.7
  * Burp Pro
  * Jython standalone WAR (https://portswigger.net/burp/help/extender.html#options_pythonenv)

## Initial setup

  1. Get both Python files template.py and generate_python.py
  2. Edit the file generate_python.py: put the absolute path of the file template.py on your system
  3. Load the plugin generate_python.py in Burp

## Usage

  1. Select one or several request(s) in Burp (Proxy, Repeater, Site Map)
  2. Right click -> "Generate Python Template"
  3. The generated Python script is displayed on the plugin's tab "PyTemplate"
  4. The script can be written to a file with the button "Export"
