# Introduction

Welcome to the Scrapegoat documentation!
This documentation will guide you through all there is to know about Scrapegoat, from installation to advanced usage.

Read on to discover how Scrapegoat can revolutionize your webscraping experience.

## The Problem with Webscraping Today
The webscraping experience is awful; it has been for a long time.
Scrapers are brittle, repetitive, and full of boilerplate.
Even simple tasks require dozens of lines of glue code just to fetch a page, parse it, and walk the DOM.

Imagine if, everytime you wanted to pull data from a database, you had to write code to connect to the database, write code to traverse the table and find your data, and then parse the results into a usable format.
Nobody would put up with that, yet that's exactly what we do when scraping the web.

!!! failure "Webscraping with BeautifulSoup"

    This code fetches a recipe page and extracts the list of ingredients into a CSV file ignoring the "Deselect All" option contained in the list.

    ````python
    import requests
    import csv
    from bs4 import BeautifulSoup


    url = "https://www.foodnetwork.com/recipes/food-network-kitchen/baked-feta-pasta-9867689"
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Scrapegoat)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
    })
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    ingredients_section = soup.find("section", class_="o-Ingredients")
    ingredients_body = ingredients_section.find("div", class_="o-Ingredients__m-Body")

    ingredients = []

    for p in ingredients_body.find_all("p"):
        label = p.find("label")
        if not label:
        continue

        spans = label.find_all("span")
        if len(spans) >= 2:
        ingredient_text = spans[1].get_text(strip=True)
        if ingredient_text.lower() == "deselect all":
            continue
        ingredients.append(ingredient_text)

    with open("ingredients.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["body"])
        for ingredient in ingredients:
        writer.writerow([ingredient])
    ````

    As you can see, even for a simple task like extracting ingredients from a recipe page, we have to write a lot of boilerplate code to handle HTTP requests, parse HTML, navigate the DOM, and write to a CSV file.

## The Scrapegoat Solution
Scrapegoat started with a question: *Why can't we query web pages like we query a database?*

Scrapegoat is designed with the query at the center.
You shouldn't have to write boilerplate, string libraries together, or even think about the underlying plumbing.
With Scrapegoat, you write queries that express *what* data you want to extract, and Scrapegoat takes care of *how* to get it.

!!! success "Webscraping with Scrapegoat"

    ````python
    from scrapegoat import Shepherd

    query = """
        VISIT "https://example.com";
        SCRAPE a IN table;
        EXTRACT href;
        OUTPUT json --filename 'links';
        """
    results = Shepherd().herd(query)
    ````

!!! tip "Running Scrapegoat from the Command Line"

    You can even run our package through the CLI!

    ````bash
    scrapegoat path/to/file.goat
    ````

## Goatspeak: The Querying Language for Scrapegoat
At the heart of Scrapegoat is Goatspeak, a domain-specific language (DSL) designed specifically for webscraping.
Goatspeak allows you to express complex scraping tasks in a concise and readable way.

We pride ourselves on ensuring Goatspeak is easy to learn, even for those new to webscraping. 
With only 5 commands, Goatspeak allows you to fetch pages, navigate the DOM, extract data, and structure the results exactly how you want them.

Below is that same example from earlier.
However, this time with a query, the Scrapegoat way:
!!! success "Goatspeak Query Example"

    ````goat
    VISIT "https://www.foodnetwork.com/recipes/food-network-kitchen/baked-feta-pasta-9867689";
    SCRAPE span IF @class="o-Ingredients__a-Ingredient--CheckboxLabel" IF body != "Deselect All";
    EXTRACT body;
    OUTPUT csv --filename "ingredients";
    ````

However, if building queries isn't your style, Scrapegoat also provides an entirely code-free experience through our Loom extension, which offers a graphical interface for building and running Goatspeak queries.

Furthermore, Goatspeak queries are designed to be portable and reusable.
Simply save a query into a `.goat` file, and it can be shared and run anywhere Scrapegoat is installed.

## Enhanced Development Experience with Linter and LSP
To further improve your development experience with Scrapegoat, we offer a linter and Language Server Protocol (LSP) extension.
The linter helps you catch syntax errors and potential issues in your Goatspeak scripts before you run them, while the LSP extension provides features like autocompletion, go-to-definition, and inline documentation within your code editor.

## Extendability
Scrapegoat is designed to be extendable. 
Each command in Goatspeak is run through a submanager, all of which are open to extension to add new functionality.
Our documentation goes over extensively how and where to add new features to Scrapegoat, to ensure you receive the richest webscraping experience possible.

## Feature Summary
- **Concise Queries**: Extract data with just a few lines of Goatspeak code.
- **Easy to Learn**: Simple syntax with only 5 core commands.
- **Code-Free Option**: Use the Loom extension for a graphical interface.
- **Portable Scripts**: Save and share `.goat` files easily.
- **Enhanced Development**: Linter and LSP support for a better coding experience.
- **Extendable**: Easily add new features and commands to Scrapegoat.
- **JavaScript Site Support**: Built-in support for scraping JavaScript-rendered pages using a headless browser.
- **Multiple Output Formats**: Export scraped data in various formats like JSON or CSV.
- **Command-Line Interface**: Run Goatspeak queries directly from the terminal.

Building webscrapers with Scrapegoat becomes a joy, not a chore.
To get started, check out our [installation guide](installation.md) and start writing your first Goatspeak query today!

## Useful Links

Below are all of Scrapegoat's links in one place for your convenience:

- [GitHub Repository](https://github.com/ChinaiArman/scrapegoat)
- [Documentation Home](https://chinaiarman.github.io/scrapegoat/)
- [Scrapegoat Core PyPI Package](https://pypi.org/project/scrapegoat-core/)
- [Scrapegoat Loom PyPI Package](https://pypi.org/project/scrapegoat-loom/)
- [License](https://github.com/ChinaiArman/scrapegoat/blob/main/LICENSE)