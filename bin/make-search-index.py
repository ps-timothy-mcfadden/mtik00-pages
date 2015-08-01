#!/usr/bin/env python2.7
"""
This script is used to generate a JSON index file of all of the Markdown content
used by Hugo.  This should be run prior to building the static files.
"""

# Imports ######################################################################
import os
import re
import json
import time
import argparse
import operator


# Metadata #####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "07/29/2015"
__license__ = "MIT"


# Globals ######################################################################
DEBUG = False
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
CONTENT_DIR = os.path.join(THIS_DIR, "..", "site", "content")
OUTFILE = os.path.join(THIS_DIR, "..", "site", "static", "js", "lunr.index.json")

# This list was taken directly from the lunr.js stopWords array.  Lunr is ignoring
# these, so we might as well remove them from our index.
IGNORED_WORDS = ["a", "able", "about", "across", "after", "all", "almost", "also", "am", "among", "an", "and", "any", "are", "as", "at", "be", "because", "been", "but", "by", "can", "cannot", "could", "dear", "did", "do", "does", "either", "else", "ever", "every", "for", "from", "get", "got", "had", "has", "have", "he", "her", "hers", "him", "his", "how", "however", "i", "if", "in", "into", "is", "it", "its", "just", "least", "let", "like", "likely", "may", "me", "might", "most", "must", "my", "neither", "no", "nor", "not", "of", "off", "often", "on", "only", "or", "other", "our", "own", "rather", "said", "say", "says", "she", "should", "since", "so", "some", "than", "that", "the", "their", "them", "then", "there", "these", "they", "this", "tis", "to", "too", "twas", "us", "wants", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would", "yet", "you", "your"]
INCLUDE_WORDS = ["tim"]
MIN_WORD_LENGTH = 5  # (Unless it starts with a capital letter)
PERMALINKS = "/:year/:month/:slug/"
MIN_PERMALINK_YEAR = 2000  # Hack for my static files.  This way I don't have to parse "type="

ENABLE_STATS = False
STATS = {}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', help="Path to your generated 'lunr.index.json' file", type=str, default=OUTFILE)
    parser.add_argument("--prettyprint", help="Make you JSON output file easier to read by humans", action="store_true")
    parser.add_argument('--contentdir', help="Path to search for your Markdown files", type=str, default=CONTENT_DIR)
    parser.add_argument('--min-permalink-year', help="Mininum post year to consider for permalink reformat", type=int, default=MIN_PERMALINK_YEAR)
    parser.add_argument("--stats", help="Print some very basic keyword statistics", action="store_true")
    return parser.parse_args()


def get_keywords(text, min_word_length=MIN_WORD_LENGTH, ignored_words=IGNORED_WORDS):
    """This function returns a set of *keywords* found in the text.

    :param str text: The text you wish to parse
    :param int min_word_length: The minumum length of words you want returned
    :param list ignored_words: Words found in this list will not be returned
    """
    # Remove any HTML elements
    text = re.sub("(<.*?>)", "", text)

    # Replace all non-word characters with a space (also get rid of _)
    text = re.sub("[\W_]", " ", text)

    # The search is case insensitive, so make things easier by always using LC
    text = text.lower()

    # Return the sorted set, since set()'s order is non-deterministic and we
    # don't want to needlessly consider a change in order a reason to check in
    # the result again.
    keywords = sorted(
        set([x for x in text.split() if re.match("^[A-Z]", x) or (x in INCLUDE_WORDS) or ((len(x) > min_word_length) and (x not in ignored_words))]),
        cmp=lambda x, y: cmp(x.lower(), y.lower()))

    if ENABLE_STATS:
        parse_stats(keywords)

    return keywords


def parse_stats(keywords):
    """This function keeps track of the number of times each keyword is used."""
    global STATS

    for keyword in keywords:
        if keyword not in STATS:
            STATS[keyword] = 1
        else:
            STATS[keyword] += 1


def print_stats():
    """Display the collected stats."""
    # http://stackoverflow.com/a/613218
    sorted_stats = sorted(STATS.items(), key=operator.itemgetter(1), reverse=True)

    print "===== Statistics ===================================="
    print "    Total number of keywords across all content:", len(STATS)
    print "    Top 10 keywords:"
    for keyword, count in sorted_stats[:10]:
        print "        %s: %i" % (keyword, count)


def get_href(date, path, slug, permalinks=PERMALINKS, min_permalink_year=MIN_PERMALINK_YEAR):
    """This function attempts to figure out the URL that the file will be
    generated at.  This is far from perfect, and only a couple permalink variables
    are even considered.
    """
    base, fname = os.path.split(path)
    slug = slug or fname[:-3]

    if (not permalinks) or (date.tm_year < min_permalink_year):
        return "/" + slug

    href = permalinks
    href = href.replace(":year", "%04i" % date.tm_year)
    href = href.replace(":month", "%02i" % date.tm_mon)
    href = href.replace(":slug", slug)

    if href.endswith("/"):
        href = href[:-1]

    if re.search(":[a-z]", href):
        raise Exception("Could not fully convert permalinks: %s" % href)

    return href


def parse(path):
    """Parses a single Markdown file.

    NOTE: Only TOML format is supported!

    Returns a dictionary with keys: ["title", "tags", "content", "href"]
    """
    with open(path, "rb") as fh:
        text = fh.read()

    match = re.search("^\+\+\+(?P<header>.*)^\+\+\+(?P<content>.*)", text, re.DOTALL | re.MULTILINE)
    if match:
        header = match.group("header")
        if "draft = true" in header:
            return None

        title = re.search("^title = (?P<quote>['\"])(?P<title>.+?)(?P=quote)", header, re.MULTILINE).group("title")
        date = re.search("^date = (?P<quote>['\"])(?P<title>.+?)(?P=quote)", header, re.MULTILINE).group("title")
        date = time.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")

        tags_match = re.search("^(categories|tags) = \[(.*?)\]", header, re.MULTILINE)
        if tags_match:
            tags = tags_match.group(2).replace("'", "").replace('"', "").replace(",", " ").split()
        else:
            tags = []

        slug_match = re.search("^slug = (?P<quote>['\"])(?P<slug>.+?)(?P=quote)", header, re.MULTILINE)
        if slug_match:
            slug = slug_match.group("slug")
        else:
            slug = None

        return {
            "title": title,
            "tags": tags,
            "content": " ".join(get_keywords(match.group("content"))),
            "href": get_href(date, path, slug)
        }


def format_timespan(seconds, format="%i:%02i:%0.4f"):
    """A convenience function to return a certain number of seconds in a readable format."""
    hours = int(seconds / 3600)
    minutes = int((seconds - hours * 3600) / 60)
    seconds = seconds - hours * 3600 - minutes * 60
    return format % (hours, minutes, seconds)


def write_json_file(data, path, prettyprint=False):
    """Outputs data to a JSON formatted text file.

    :param var data: The data you want to write
    :param str path: The path of the file you want to write the data to
    :param bool prettyprint: Whether or not you want a human-readable file
    """
    with open(path, "wb") as fh:
        if prettyprint:
            fh.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), ))
        else:
            fh.write(json.dumps(data))


def get_index(basedir):
    """Walk `basedir`, searching for any Markdown files.  These files will be
    parsed and returned as a list of dictionaries.

    :param str basedir: The root directory you want to walk
    """
    index = []

    for root, _, files in os.walk(basedir):
        for fname in files:
            if not fname.endswith(".md"):
                continue

            path = os.path.join(root, fname)
            data = parse(path)

            # Only add stuff to the index that has content
            if data and data["content"]:
                index.append(parse(path))

    return index


if __name__ == '__main__':
    tstart = time.time()

    args = get_args()
    ENABLE_STATS = args.stats
    index = get_index(args.contentdir)
    write_json_file(index, args.outfile, args.prettyprint)

    print "Parsed [%i] files in [%s]" % (len(index), format_timespan(time.time() - tstart))
    print "Created index file at", os.path.abspath(args.outfile)
    print "...size is %.02fkb" % (os.stat(args.outfile).st_size / 1024.0)

    if ENABLE_STATS:
        print_stats()
