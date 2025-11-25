import argparse
from scrapegoat_core import Shepherd, HeadlessSheepdog


def main():
    parser = argparse.ArgumentParser(description="Scrapegoat language executor")

    # Positional file or query arg
    parser.add_argument(
        "file_or_query",
        nargs="?",
        help="Path to a .goat file or a raw query as a string",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Prints the results of the query to the console",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        "--javascript",
        help="Uses a headless browser to support javascript rendered pages",
        action="store_true",
    )

    args = parser.parse_args()

    if args.javascript:
        shepherd = Shepherd(sheepdog=HeadlessSheepdog())
    else:
        shepherd = Shepherd()

    nodes = shepherd.herd(args.file_or_query)

    if args.verbose:
        for node in nodes:
            print(node)
