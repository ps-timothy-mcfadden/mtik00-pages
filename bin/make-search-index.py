#!/usr/bin/env python2.7
"""
This script is used to generate a JSON index file of all of the Markdown content
used by Hugo for use with Lunr.js.  This should be run prior to building the
static files.

NOTE: Only TOML is supported, and "draft" content is not considered.
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
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
CONTENT_DIR = os.path.join(THIS_DIR, "..", "site", "content")
OUTFILE = os.path.join(THIS_DIR, "..", "site", "static", "js", "lunr-index.json")

# This list was taken directly from the lunr.js stopWords array.  Lunr is ignoring
# these, so we might as well remove them from our index.
IGNORED_WORDS = ["a", "able", "about", "across", "after", "all", "almost", "also", "am", "among", "an", "and", "any", "are", "as", "at", "be", "because", "been", "but", "by", "can", "cannot", "could", "dear", "did", "do", "does", "either", "else", "ever", "every", "for", "from", "get", "got", "had", "has", "have", "he", "her", "hers", "him", "his", "how", "however", "i", "if", "in", "into", "is", "it", "its", "just", "least", "let", "like", "likely", "may", "me", "might", "most", "must", "my", "neither", "no", "nor", "not", "of", "off", "often", "on", "only", "or", "other", "our", "own", "rather", "said", "say", "says", "she", "should", "since", "so", "some", "than", "that", "the", "their", "them", "then", "there", "these", "they", "this", "tis", "to", "too", "twas", "us", "wants", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would", "yet", "you", "your"]

# These words will be included regardless of length or inclusion in IGNORED_WORDS
INCLUDE_WORDS = ["tim"]

# The minimum length of a word to be considered a keyword (not used for words
# beginning with a capital letter)
MIN_WORD_LENGTH = 5

# We'll try to infer the "href" for the index based on this setting.
PERMALINKS = "/:year/:month/:slug/"

# Hack for my static files.  Only posts dated newer this parameter will be
# considered for the PERMALINKS setting.  Posts older than this parameter will
# assumed to be "static", located at document root.
MIN_PERMALINK_YEAR = 2000

# When --stats is enabled, the top X words will be displayed
TOP_X_WORDS = 10

# Only set this parameter to True if you publish draft content and want it
# included in the search
INCLUDE_DRAFTS = False

# By default, Hugo makes folders for your content (http://gohugo.io/extras/urls/)
# The HREFs stored in the index *should* always end with a slash (e.g.
# /posts/content1/).  If you run into trouble with this, you can turn this off.
# NOTE: Depending on how you are serving your pages, turning this off can cause
# 301 redirects to unwanted locations (e.g. a custom domain could redirect to
# <username>.github.io).
FORCE_TRAILING_SLASH = True


def get_args():
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', help="Path to your generated 'lunr-index.json' file", type=str, default=OUTFILE)
    parser.add_argument("--prettyprint", help="Make you JSON output file easier to read by humans", action="store_true")
    parser.add_argument('--contentdir', help="Path to search for your Markdown files", type=str, default=CONTENT_DIR)
    parser.add_argument('--min-permalink-year', help="Minimum post year to consider for permalink reformat", type=int, default=MIN_PERMALINK_YEAR)
    parser.add_argument("--stats", help="Print some very basic keyword statistics", action="store_true")
    parser.add_argument("--drafts", help="Include drafts in the index (Only use this if you publish your draft content!)", action="store_true")
    return parser.parse_args()


def get_keywords(text, min_word_length=MIN_WORD_LENGTH, ignored_words=IGNORED_WORDS):
    """This function returns a set of *keywords* found in the text.  An attempt
    is made to ignore all HTML tags, Markdown link targets, non-words, words
    less than a minimum length, and words included in the IGNORED_WORDS list.

    :param str text: The text you wish to parse
    :param int min_word_length: The minimum length of words you want returned
    :param list ignored_words: Words found in this list will not be returned
    """
    # Remove any HTML tags
    text = re.sub("(</?.*?>)", "", text)

    # Remove Markdown links (but keep the link text)
    text = re.sub("\[(.+)\]\(.+?\)", r"\1", text)

    # Replace all non-word characters and underscore with a space
    text = re.sub("[\W_]", " ", text)

    # Return the sorted set, since set()'s order is non-deterministic and we
    # don't want to needlessly consider a change in order a reason to check in
    # the result again.
    words = text.split()
    keywords = sorted(
        set([
            x.lower() for x in words if
            re.match("^[A-Z][a-z]{3}", x)  # Capitalized words w/ 3 or more characters are always considered
            or (x in INCLUDE_WORDS)
            or ((len(x) > min_word_length) and (x not in ignored_words))
        ]),
        cmp=lambda x, y: cmp(x.lower(), y.lower())
    )

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
    sorted_stats = sorted(STATS.items(), key=operator.itemgetter(1), reverse=True)[:TOP_X_WORDS]

    print "===== Statistics ===================================="
    print "    Total number of keywords across all content:", len(STATS)
    print "    Top %i keywords:" % TOP_X_WORDS
    for keyword, count in sorted_stats:
        print "    %20s: %i" % (keyword, count)


def get_href(date, path, slug, permalinks=PERMALINKS, min_permalink_year=MIN_PERMALINK_YEAR):
    """This function attempts to figure out the URL that the file will be
    generated at.  This is far from perfect, and only a couple permalink variables
    are even considered.
    """
    base, fname = os.path.split(path)
    slug = slug or fname[:-3]

    if (not permalinks) or (date.tm_year < min_permalink_year):
        href = "/" + slug

        if FORCE_TRAILING_SLASH and (not href.endswith("/")):
            href += "/"

        return href

    href = permalinks
    href = href.replace(":year", "%04i" % date.tm_year)
    href = href.replace(":month", "%02i" % date.tm_mon)
    href = href.replace(":slug", slug)

    # We need to add the trailing slash so we don't get 301 redirects.
    if FORCE_TRAILING_SLASH and (not href.endswith("/")):
        href = href[:-1]

    if re.search(":[a-z]", href):
        raise Exception("Could not fully convert permalinks: %s" % href)

    return href


def parse(path, drafts=False):
    """Parses a single Markdown file.

    NOTE: Only TOML format is supported!

    Returns a dictionary with keys: ["title", "tags", "content", "href"]
    """
    with open(path, "rb") as fh:
        text = fh.read().strip()

    if not re.match("^\+\+\+", text):
        raise Exception("[%s] doesn't appear to be TOML")

    match = re.search("^\+\+\+(?P<header>.*)^\+\+\+(?P<content>.*)", text, re.DOTALL | re.MULTILINE)
    if match:
        header = match.group("header")
        if re.search("^\s*draft\s+=\s+true", header, re.MULTILINE) and (not drafts):
            return None

        title = re.search("^title\s+=\s+(?P<quote>['\"])(?P<title>.+?)(?P=quote)", header, re.MULTILINE).group("title")
        date = re.search("^date\s+=\s+(?P<quote>['\"])(?P<title>.+?)(?P=quote)", header, re.MULTILINE).group("title")
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


def get_index(basedir, drafts=False):
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
            data = parse(path, drafts=drafts)

            # Only add stuff to the index that has content
            if data and data["content"]:
                index.append(parse(path))

    return index


if __name__ == '__main__':
    tstart = time.time()

    args = get_args()
    ENABLE_STATS = args.stats
    STATS = {}
    index = get_index(args.contentdir, drafts=args.drafts)
    write_json_file(index, args.outfile, args.prettyprint)

    print "Parsed [%i] files in [%s]" % (len(index), format_timespan(time.time() - tstart))
    print "Created index file at", os.path.abspath(args.outfile)
    print "...size is %.02fkb" % (os.stat(args.outfile).st_size / 1024.0)

    if ENABLE_STATS:
        print_stats()
