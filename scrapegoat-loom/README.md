# Scrapegoat Loom

Welcome to the Scrapegoat Loom!
This is where all the code for the Loom extension of Scrapegoat lives.

Read on to discover how Scrapegoat can revolutionize your webscraping experience.

## Quick Links

Is this page not what you are looking for?
Below are all of Scrapegoat's links in one place for your convenience:

- [GitHub Repository](https://github.com/armanchinai/scrapegoat)
- [Documentation Home](https://armanchinai.github.io/scrapegoat/)
- [Scrapegoat Core PyPI Package](https://pypi.org/project/scrapegoat-core/)
- [Scrapegoat Loom PyPI Package](https://pypi.org/project/scrapegoat-loom/)
- [License](https://github.com/armanchinai/scrapegoat/blob/main/LICENSE)

## The Problem with Webscraping Today
The webscraping experience is awful; it has been for a long time.
Scrapers are brittle, repetitive, and full of boilerplate.
Even simple tasks require dozens of lines of glue code just to fetch a page, parse it, and walk the DOM.

Imagine if, everytime you wanted to pull data from a database, you had to write code to connect to the database, write code to traverse the table and find your data, and then parse the results into a usable format.
Nobody would put up with that, yet that's exactly what we do when scraping the web.

This code fetches a recipe page and extracts the list of ingredients into a CSV file ignoring, the "Deselect All" option contained in the list.

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

ingredient_spans = soup.select("span.o-Ingredients__a-Ingredient--CheckboxLabel")

ingredients = []
for span in ingredient_spans:
    body = span.get_text(strip=True)
    if body.lower() != "deselect all":
        ingredients.append(body)

with open("ingredients.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["body"])
    for ingredient in ingredients:
    writer.writerow([ingredient])
````

As you can see, even for a simple task like extracting ingredients from a recipe page, we have to write a lot of boilerplate code to handle HTTP requests, parse HTML, navigate the DOM, and write to a CSV file. With more complex tasks, the code only gets longer and more unwieldy. Stacking this up over multiple pages or sites quickly becomes a nightmare.

## The Scrapegoat Solution
Scrapegoat started with a question: *Why can't we query web pages like we query a database?*

### Query-Centric Design
Scrapegoat is designed with the query at the center.
You shouldn't have to write boilerplate, string libraries together, or even think about the underlying plumbing.
With Scrapegoat, you write queries that express *what* data you want to extract, and Scrapegoat takes care of *how* to get it.

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

You can even run our package through the CLI!

````bash
scrapegoat path/to/file.goat
````

### Goatspeak: The Querying Language for Scrapegoat
At the heart of Scrapegoat is Goatspeak, a domain-specific language (DSL) designed specifically for webscraping.
Goatspeak allows you to express complex scraping tasks in a concise and readable way.

We pride ourselves on ensuring Goatspeak is easy to learn, even for those new to webscraping. 
With only 5 commands, Goatspeak allows you to fetch pages, navigate the DOM, extract data, and structure the results exactly how you want them.

Below is that same example from earlier.
However, this time with a query, the Scrapegoat way:

````goat
VISIT "https://www.foodnetwork.com/recipes/food-network-kitchen/baked-feta-pasta-9867689";
SCRAPE span IF @class="o-Ingredients__a-Ingredient--CheckboxLabel" IF body != "Deselect All";
EXTRACT body;
OUTPUT csv --filename "ingredients";
````

### Loom: A Graphical Interface for Building Goatspeak Queries

However, if building queries isn't your style, Scrapegoat also provides an entirely code-free experience through our Loom extension, which offers a graphical interface for building and running Goatspeak queries.

Furthermore, Goatspeak queries are designed to be portable and reusable.
Simply save a query into a `.goat` file, and it can be shared and run anywhere Scrapegoat is installed.

### Enhanced Development Experience with Linter and LSP
To further improve your development experience with Scrapegoat, we offer a linter and Language Server Protocol (LSP) extension.
The linter helps you catch syntax errors and potential issues in your Goatspeak scripts before you run them, while the LSP extension provides features like autocompletion, go-to-definition, and inline documentation within your code editor.

### Extendability
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

## Author

### Quinn Thompson

Responsible for developing the Loom extension, creating the graphical interface for building Goatspeak queries, and enhancing user experience.

<p align="center">
    <!-- LinkedIn -->
    <a href="https://www.linkedin.com/in/quinn-thompson-5362a2237/" target="_blank">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
    </a>
    <!-- GitHub -->
    <a href="https://github.com/qthompson2">
        <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
    </a>
    <!-- Email -->
    <a href="mailto:q.thompson088@gmail.com">
        <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email">
    </a>
</p>

## Acknowledgements

Scrapegoat was developed as a semester-long project at British Columbia Institute of Technology (BCIT) for the course [COMP 7082 - Software Engineering](https://www.bcit.ca/courses/software-engineering-comp-7082/). The team will always express its deepest appreciation to [BCIT](https://www.bcit.ca/), the [Bachelor of Science in Applied Computer Science](https://www.bcit.ca/programs/bachelor-of-science-in-applied-computer-science/?gclsrc=aw.ds&gad_source=1&gad_campaignid=6619783868&gbraid=0AAAAADA1Hd1fv6rgLxfuBhvK5Rm2qP96C&gclid=Cj0KCQiAubrJBhCbARIsAHIdxD-4qTkpFYvcyLX83bOhPxmdYRYj3ENnir7DR4H5ghMb5fbfcztWkoMaApW-EALw_wcB) program, and [Fatemeh Riahi](https://www.linkedin.com/in/fatemeh-riahi-99b3775a/) for her continuous support and guidance throughout the project.

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.