# Scrapegoat Core Documentation

## Introduction
This section of the documentation covers the documentation for the core Scrapegoat package.
The core package provides the fundamental features and functionalities of Scrapegoat.

For added scraping joy, this package has been goat themed. After all, goats are known for their agility and ability to navigate difficult terrain, much like how Scrapegoat helps you navigate the complexities of webscraping.

## Scrapegoat Architecture Overview

Scrapegoat is built around a modular OOP architecture that separates concerns into different components.

### Submanagers

Most users will primarily interact with the [Shepherd](./classes/shepherd.md) class, which serves as the main entry point for executing Goatspeak queries. 
However, under the hood, Scrapegoat is composed of several submanagers, each responsible for handling specific commands in Goatspeak.

- [Goat](./classes/goat.md): The submanager responsible for handling scrape and select operations.
- [Sheepdog](./classes/sheepdog.md): The submanager responsible for handling visit operations.
- [Milkmaid](./classes/milkmaid.md): The submanager responsible for handling extract operations.
- [Milkman](./classes/milkman.md): The submanager responsible for handling file I/O operations.
- [Gardener](./classes/gardener.md): The submanager responsible for handling the conversion of HTML strings into HTMLNode objects.

### Language Utility Classes

Supporting these submanagers are several language utility classes that represent the core constructs of the Goatspeak language.

- [Query](./classes/block.md): The class representing an individual query.
- [GoatspeakBlock](./classes/block.md): A group of queries to be executed as a block.
- [Command](./classes/commands.md): The base class for all Goatspeak commands.
    - [FetchCommand](./classes/commands.md): The class representing the VISIT command.
    - [GrazeCommand](./classes/commands.md): The class representing the SELECT and SCRAPE commands.
    - [ChurnCommand](./classes/commands.md): The class representing the EXTRACT command.
    - [DeliverCommand](./classes/commands.md): The class representing the OUTPUT command.
- [Condition](./classes/conditions.md): The base class for all conditional statements in Goatspeak.
    - [IfCondition](./classes/conditions.md): The class representing an IF conditional statement.
    - [InCondition](./classes/conditions.md): The class representing an IN conditional statement
- [HTMLNode](./classes/node.md): The class representing an HTML element in the DOM.

### Interpreter Utility Classes

Finally, several utility classes assist in interpreting and executing Goatspeak queries.

- [Interpreter](./classes/interpreter.md): The class responsible for interpreting and executing Goatspeak queries.
- [Parser](./classes/interpreter.md): The base class responsible for parsing Goatspeak queries into command objects.
    - [FlagParser](./classes/interpreter.md): The class responsible for parsing flags in Goatspeak commands.
    - [ConditionParser](./classes/interpreter.md): The class responsible for parsing conditional statements in Goatspeak commands.
    - [ScrapeSelectParser](./classes/interpreter.md): The class responsible for parsing SCRAPE and SELECT commands in Goatspeak.
    - [ExtractParser](./classes/interpreter.md): The class responsible for parsing EXTRACT commands in Goatspeak.
    - [OutputParser](./classes/interpreter.md): The class responsible for parsing OUTPUT commands in Goatspeak.
    - [VisitParser](./classes/interpreter.md): The class responsible for parsing VISIT commands in Goatspeak.
- [Tokenizer](./classes/interpreter.md): The class responsible for tokenizing Goatspeak queries into individual tokens.
- [Token](./classes/interpreter.md): The class representing an individual token in a Goatspeak query.
- [TokenType](./classes/interpreter.md): An enumeration of all possible token types in Goatspeak.

## Further Reading
To learn more about each of these components, please refer to their respective documentation pages linked above.