import argparse
from scrapegoat_loom import Loom


def main():
    parser = argparse.ArgumentParser(description="Scrapegoat language executor")
    
    args = parser.parse_args()

    Loom().weave()