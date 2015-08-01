+++
categories = ["hugo"]
date = "2015-07-30T15:39:23-06:00"
title = "Wordpress XML to Hugo MD"
type = "post"
slug = "wordpress-xml-to-hugo-md"
+++
I've had a personal family blog in one form of another since 2002. <!--more--> For the last 10 years, give or take, I used [WordPress](https://wordpress.com/).  It's a very fine and handy tool; especially for non-technical types.  That's the real issue... I'm a *technical type*.  I started looking for something simpler, easier to maintain, and more secure.  That led me to *static site generators*.

I won't go into the details, but there [are a few to choose from](http://lmgtfy.com/?q=static+site+generators).  I settled on [Hugo](http://gohugo.io/).  I was mainly interested in it because it seemed easy, was written in [Go](http://golang.org/), and yes, it had a pretty website.

The Conversion
==============

One of the many nice things about WordPress is the ability to export your site into XML (side note, I *loath* XML).  There are some examples and script that do the conversion for you, but what fun would that be?  In the process, I learned that:

1.  Most HTML is Markdown compliant (that is, Markdown "understands" it)
2.  It's hard to tell an HTML-to-MD converter exactly how you want the HTML parsed.

On to the script!  [You can view the script here.](https://gist.github.com/mtik00/75c8f555b49365395e32).  I won't go over it in gory detail, but here are the basics.

WP exports everything, but I was only concerned with the post `body`, the date it was published (`pubDate`), the `category`'s (I called them `tags` in the script), the `title`, and where it should go.  The last part took some predetermined knowledge of how I wanted my Hugo site to be set up (read [`[permalinks]`](http://gohugo.io/extras/permalinks/)).  If you look at the exported XML file, there are *lots* of metadata that I'm ignoring (YMMV).

{{< highlight python >}}
    tree = ET.parse(xml_path)
    channel = tree.find("channel")
    wp_version_check(channel)

    for post in channel.findall("item"):
        print "post title:", post.find("title").text
{{< /highlight >}}

WP puts all of the posts in a \<channel\> element.  Each post is located inside an \<item\> element.  So far, so good!  Now all we need to do is to loop through each item and grab the data we need.

{{< highlight python >}}
def wp_to_hugo_date(wp_date, tz_direction=-1):
    """Converts a UTC time string from the WordPress XML to a Hugo time string."""
    date = time.strptime(wp_date, "%a, %d %b %Y %H:%M:%S +0000")
    date = calendar.timegm(date)
    ltime = time.localtime(date)
    date = time.strftime("%Y-%m-%dT%H:%M:%S", ltime)

    date += "%+03i:00" % (((time.timezone / 3600) - (1 * ltime.tm_isdst)) * tz_direction)
    return ltime, date
{{< /highlight >}}

I'm using this function to convert the `pubDate` from WordPress to the format that Hugo uses.  Nothing real special here, although I'm sure there's a much better way to calculate the time zone.  The string-formatted `pubDate` will go into the posts front matter, and I parse `ltime` to figure out where the post should go.

That's the basics.  I ran this script on my entire WordPress XML dump (only 90+ pages, nothing too big).  It created all of the Markdown posts full of HTML.  It was up to me to then go in and adjust some of the HTML so it was rendered a little better by Hugo.  Most of my time spent was on downloading images, checking them into Git, and reworking the gallery posts to use my new template (which is awesome, because now I can use `{{ gallery path/to/gallery/folder }}` in my markdown).

The point is, however, I was able to have a fully functioning port of my WordPress blog to Hugo in a matter of hours (the script only took a second to run).  Woot!
