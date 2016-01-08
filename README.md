# pyoocs

![alt tag](https://madrisan.files.wordpress.com/2015/09/pyoocs-logo.png)

## Out of Compliance Scanner for Linux

### A customizable and modular security scanner for Linux

This project is at an early stage of development and only a few modules are currently available:

* *environment*: checks the root environment
* *filesystem*: checks for mandatory filesystems and mount options and for system files permissions
* *kernel*: check the kernel runtime configuration
* *packages*: make some checks on installed packages and rpm database
* *services*: check whether a list of services are running or not
* *sudo*: checks for root rights given to users and security issues

The checks are configurable via a JSON file.
You can found an example [here][1]

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
     "publicDir": "html/server/public/"
 },
```

---

> Project name | pyoocs
> :--- | :---
> Tags | Utilities/Security
> License | GPL v3+
> Operating System | Linux
> Implementation | Python 2.4+
> Current status | beta

[1]: https://github.com/madrisan/pyoocs/blob/master/oocs-cfg.json
