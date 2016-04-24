# pyoocs

![alt text][logo]

## Out of Compliance Scanner for Linux

### A customizable and modular security scanner for Linux

> Project name | pyoocs
> :--- | :---
> Tags | Utilities/Security
> License | GPL v3+
> Operating System | Linux
> Implementation | Python 2.4+, Python 3
> Current status | beta

#### Overview

This project is at an early stage of development and only a few modules are currently available:

* *environment*: checks the root environment
* *filesystem*: checks for mandatory filesystems and mount options and for system files permissions
* *kernel*: check the kernel runtime configuration
* *packages*: make some checks on installed packages and rpm database
* *services*: check whether a list of services are running or not
* *sudo*: checks for root rights given to users and security issues

The checks are configurable via a JSON file.
You can found an example [here][jsoncfg]

In particular three different output formats are supported:

* *console*: print the output to the console:
```json
 "oocs-output" : "console",
```
* *json*: print the output to the console, but in json format:
```json
 "oocs-output" : "json",
```
* *html*: run an http server for displaying the result of the scan:
```json
 "oocs-output" : "html",
 "oocs-html-opts": {
     "baseUrl": "http://localhost:8000/",
     "publicDir": "/srv/www-oocs/html/server/public/"
 },
```

The html mode is intended for debug and testing only.
Use the script `oocs-htmlviewer.py` instead, or the Node.JS viewer coupled with a MongoDB backend.

#### Screenshot of the Web Interface

PyOOCS also provides a (single page MVC) web application, based on the UI Boostrap and AngularJS technologies,
that let you browse the list of the available security reports and select which one to check.
The scanning data is stored in a MongoDB database ('oocs').

Here's a screenshot of a detailed server report.
Note that this server is tagged in red color because some critical deviations have been detected.
Each class of vulnerabilities (_critical_ or _warning_) can be inspected by selecting the appropriate tab,
which also show the number of occurrences that have been detected.
By default all the tests are displayed.


![alt text][screenshot_web]

[jsoncfg]: https://github.com/madrisan/pyoocs/blob/master/oocs-cfg.json
[logo]: https://madrisan.files.wordpress.com/2015/09/pyoocs-logo.png
[screenshot_web]: https://madrisan.files.wordpress.com/2015/10/screencapture-pyoocs-web-interface.png
