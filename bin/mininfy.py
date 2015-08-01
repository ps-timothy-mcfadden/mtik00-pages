import os
import htmlmin


def slurp(path):
    with open(path, "rb") as fh:
        text = fh.read()

    return unicode(text)


def get_minimized_text(path):
    text = slurp(path)
    html = htmlmin.minify(text, remove_comments=True, remove_empty_space=True)
    return html


if __name__ == '__main__':
    for root, dirs, files in os.walk('mtik00.github.io'):
        for fname in [x for x in files if x.endswith(".html")]:
            html_file = os.path.join(root, fname)
            print "minimizing: ", html_file
            minimized_html = get_minimized_text(html_file)
            with open(html_file, "wb") as fh:
                fh.write(minimized_html)
