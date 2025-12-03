# Installation

Welcome to the installation guide!
This page will walk you through how to install all of the features from the Scrapegoat ecosystem.
Follow the steps below to set up the software on your system.

## Prerequisites
Before you begin, ensure that you have the following prerequisites installed on your system:

* [Python](https://www.python.org/downloads/) (version 3.7 or higher)
* [pip](https://pip.pypa.io/en/stable/installation/)
* [Playwright](https://playwright.dev/python/docs/intro) (Optional by default, required for JavaScript rendering support)

!!! tip "Check Python Version"

    You can check your Python version by running.

    ````bash
    python --version
    ````

## Core Installation

### Install the Core Package
To install the core package, run the following command in your terminal:
````bash
pip install scrapegoat-core
````

### Optional: Install with Playwright Support
If you want to use Playwright for browser automation, you can install the package with Playwright support by running:
````bash
pip install scrapegoat-core[js]
````

### Verify Installation
To verify that the installation was successful, you can run the following command:
````bash
scrapegoat -h
````
This should display the help message for the Scrapegoat command-line interface.
If you see the help message, congratulations! You have successfully installed Scrapegoat.

!!! success "Scrapegoat Installation Successful"
    If you see the help message, congratulations! You have successfully installed Scrapegoat.

    ````plaintext
    usage: scrapegoat [-h] [-v] [-j] [file_or_query]

    Scrapegoat language executor

    positional arguments:
        file_or_query     Path to a .goat file or a raw query as a string

    options:
        -h, --help        show this help message and exit
        -v, --verbose     Prints the results of the query to the console
        -j, --javascript  Uses a headless browser to support javascript rendered pages
    ````

## Loom Installation (Optional)
Loom is an optional extension that provides additional features for Scrapegoat.

### Install Loom
To install Loom, run the following command:
````bash
pip install scrapegoat-loom
````

### Installing Scrapegoat with Loom Support
Alternatively, you can install Scrapegoat with Loom support by running:
````bash
pip install scrapegoat-core[loom]
````

### Verify Loom Installation
To verify that Loom was installed successfully, you can run the following command:
````bash
loom -h
````
This should display the help message for the Loom command-line interface.

!!! success "Loom Installation Successful"

    If you see the help message, congratulations! You have successfully installed Loom.

    ````plaintext
    usage: loom [-h]

    Scrapegoat language executor

    options:
    -h, --help  show this help message and exit
    ````

## Linter and LSP Installation (Optional)
Scrapegoat also offers a linter and Language Server Protocol (LSP) extension for enhanced development experience. 

### Installation via GitHub
Currently our LSP and linter extensions are not available on the VSCode marketplace.
To install the Goatspeak linter and LSP extension, follow these steps:

1. Clone the Scrapegoat repository using the command below.
````bash
git clone "https://github.com/ChinaiArman/scrapegoat.git"
````
1. Open VSCode and go to the Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or by pressing `Ctrl+Shift+X`.
2. Click on the three-dot menu in the top-right corner of the Extensions view and select "Install from VSIX...".
3. Navigate to the cloned `scrapegoat` repository and find the `goatspeak-language-support` folder.
4. Select the `goatspeak-language-support` folder and click "Open" to install the extension.

### Verify Linter and LSP Installation

To verify that the linter and LSP extension is working, open a `.goat` file in VSCode. 

!!! success "Goatspeak Linter and LSP Installation Successful"
    You should see syntax highlighting and linting suggestions as you type.

## Conclusion
You have now successfully installed Scrapegoat and its optional extensions.
You can start using Scrapegoat for your web scraping needs.
For more information on how to use Scrapegoat, take a peak at our [tutorials](tutorials/core-tutorial.md) to begin using Scrapegoat.