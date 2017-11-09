+++
categories = ["web", "python"]
date = "2017-11-09T14:52:30-07:00"
title = "Jinja2 Cache Busting URLs in Python"
type = "post"
slug = "jinja2-cache-busting-urls"
+++

Cache busting is a technique the gives web developers a compromise between
asset load speeds and new features.  In this article,
we'll discuss a *pure Python* way of implementing this feature in your Jinja2
templates.<!--more-->

# What is "caching"
NOTE: This article will not cover HTML cache headers, proxy settings, etc.

Everything you see on a web page is *loaded* from somewhere.  That "somewhere"
could be a VPS in the cloud, a [CDN](https://en.wikipedia.org/wiki/Content_delivery_network)
service like [CloudFlare](https://www.cloudflare.com/), your machine, and so
on.  We'll call these things "assets".  Assets are images and text files used
to tell your browser how the page you are looking at should look.  These are
mostly things that don't really change too often.

Since assets don't change often, you can *really* speed up page loading by using
something called "cache".  Serving files from the webserver can be really slow,
especially if it's a very popular website, or your internet connection is slow.
The good news is that if you have visited that page recently, some or all of
the assets will already be on your computer.

This all happens without much input from you, the user.  Your browser will
cache by default (unless using something like Tor Browser).  Even if you have
your browser cache disabled, the assets may be cached by a service like
[CloudFlare](https://www.cloudflare.com/).  That's out of your control.

Quick loading is great, but what happens when the version of
`cute-puppy.jpg` you have in your cache is different from what's on the server?
You'll continue to see the same old boring puppy image.
[FOMO](https://en.wikipedia.org/wiki/Fear_of_missing_out) anyone?

There's also evidence that search engines prioritize websites that use very
long cache times (e.g. Google's own Page Insights tool).  A nice article on
how caching works can be found here: https://jakearchibald.com/2016/caching-best-practices/

# Busting the cache
Web developers use a technique called "cache busting" to ensure that any
change to `cute-puppy.jpg` is immediately seen by users.  They get around any
"cache" mechanism by generally taking 1 of these approaches:

*   Change the filename: Instead of `cute-puppy.jpg`, they'll use something
    like `cute-puppy-v1.jpg`.  If the change the content, they'll change
    the name to `cute-puppy-v2.jpg`.
*   Change the URL: Instead of using `/static/images/cute-puppy.jpg` in
    HTML, they'll use something like `/static/images/cute-puppy.jpg?v1`.

The idea is the same.  Any change a developer makes to the *"asset"* will cause
viewers to download the updated file.

I prefer the second method.  I think this is cleaner, and causes less overall
churn in my source code control.

# Pre-calculate vs JIT
The way I see it, you have two options here: 1) Use a build step to version your
assets; 2) perform a "just in time" calculation when the resource is requested.
This really depends on your process, but I don't see a downside to pre-calculating a version.
This method should also perform much better under load.  Admittedly, I'm too lazy to measure
it, so [YMMV](https://en.wiktionary.org/wiki/YMMV).

I decided to create a script that calculated the [CRC32](https://en.wikipedia.org/wiki/Cyclic_redundancy_check)
for each of my static images and store the result in a JSON file.  I load that
file at the start of my script.  This works great!  It does, however, cause a
lookup to occur each time the Jinja2 template is *rendered*.  Jinja2 is pretty
good a caching rendered templates (moar cache!), so I think that's fine.

NOTE: You could also dynamically create this table at application start.  I
chose not to just to keep the start process simple and clean.

Here's my Python function to calculate the
[CRC32](https://en.wikipedia.org/wiki/Cyclic_redundancy_check) for each of my
images:
{{< highlight python >}}
import zlib
def build():
    """
    Builds the release files
    """
    # Calculates and stores the CRC32 for all images in 'static/images'
    outfile = os.path.join(THIS_DIR, 'app', 'cachbuster.json')
    image_dir = os.path.join(THIS_DIR, 'html', 'static', 'images')
    result = {}
    for root, dirs, files in os.walk(image_dir):
        for fname in files:
            fpath = root + '/' + fname
            relpath = fpath[len(image_dir) + 1:].replace('\\', '/')
            prev = 0
            for line in open(fpath, 'rb'):
                prev = zlib.crc32(line, prev)
            result[relpath] = '%x' % (prev & 0xFFFFFFFF)

    with open(outfile, 'wb') as fh:
        fh.write(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))
{{< /highlight >}}

The fancy `relpath` thing is so the output is more manageable (more on that
later).  The file output looks a little like this:
<a name="jsonfile"></a>
{{< highlight json >}}
{
    "about-us.jpg": "8212d43f",
    "favicon.ico": "be79d92e",
    "slider/title-img-01.jpg": "5849f6f0",
    "slider/title-img-02.jpg": "a66c8271",
    "slider/title-img-03.jpg": "2e2cbe84"
}
{{< /highlight >}}

# Jinja2
[Jinja2](http://jinja.pocoo.org/) is a templating tool used by many Python-based
web development frameworks (like [Flask](http://flask.pocoo.org/) and
[bottle.py](https://bottlepy.org)).  It's really quite handy when it comes to
creating a single HTML file using nice
[OO](https://en.wikipedia.org/wiki/Object-oriented_programming)
concepts like inheritance.

## Filter
The first thing we want to do is to add a custom Jinja2 *filter*.  This is the
thing that will compare some input to our [JSON data](#jsonfile) and return a URL.

{{< highlight python >}}
CACHEBUSTER = json.loads(open(THIS_DIR + '/cachbuster.json', 'rb').read())
{{< /highlight >}}

`CACHEBUSTER` is just the data that was calculated during our build step.

{{< highlight python >}}
def imageloader(partial_path):
    '''
    Returns the path with a cachbuster tag if found, or the path otherwise.
    '''
    if partial_path in CACHEBUSTER:
        return '/static/images/' + partial_path + '?' + CACHEBUSTER[partial_path]

    return '/static/images/' + partial_path
{{< /highlight >}}

The function `imageloader` is the thing that we'll usee in our Jinja2 templates.
This function accepts a single input, `partial_path`.  We check for the
existence of that path in our data.  If we find it, we return a URL with the
calculation appended as a "query".  If not, we'll assume that the path is
relative to `/static/images/`.

Using [our data](#jsonfile) file from above:
{{< highlight python >}}
>>> print imageloader('slider/title-img-01.jpg')
'/static/images/slider/title-img-01.jpg?5849f6f0'
>>> print imageloader('someimage.jpg')
'/static/images/someimage.jpg'
{{< /highlight >}}

All good!  Any time we make a change to `slider/title-img-01.jpg`, the
calculation will change, and we'll get a new URL.  Any item that's not
pre-calculated will be returned like normal.

The last part is to tell Jinja2 about this new filter in `app.py`.
{{< highlight python >}}
jinja2_loader = jinja2.FileSystemLoader(TEMPLATE_DIR)
jinja2_env = jinja2.Environment(autoescape=True, loader=jinja2_loader)
jinja2_env.filters['imageloader'] = imageloader
{{< /highlight >}}

The magic is the `jinja2_env.filters['imageloader'] = imageloader` line.  That
tells Jinja2 to call our `imageloader()` function any time it sees a filter
named `imageloader`.

## Template Use

Here's how I use the new filter inside a template:
{{< highlight html >}}
<img src="{{'slider/title-img-01.jpg' | imageloader}}" alt="Title slider image 1">
{{< /highlight >}}

`'slider/title-img-01.jpg'` gets passed to our function, which returns
`'/static/images/slider/title-img-01.jpg?5849f6f0'`.  That whole string then
goes into the template, resulting in this:
{{< highlight html >}}
<img src="/static/images/slider/title-img-01.jpg?5849f6f0" alt="Title slider image 1">
{{< /highlight >}}

Perfect!  As long as we keep generating our JSON file during our build process,
the templates will always point to the latest asset without regard to our
cache settings.

# Where to go from here
I showed you how I cache-bust the images from one of my websites.  This is done
in pure Python, without other tools like `Grunt`.  If you are already using
compile tools, you may as well find out how they do cache-busting.  But what
fun is that?

This can be extended to your other assets.  For example, why not to your
`.css` and `.js` too?  That excersize is left up to the reader ;)
