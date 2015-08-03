+++
categories = ["github", "nginx"]
date = "2015-08-02T22:15:32-06:00"
title = "Nginx Proxy for GitHub Pages"
type = "post"
slug = "nginx-proxy-for-github-pages"
+++
[Nginx](https://www.nginx.com/) is my favorite web server.  I find it *much* easier to configure and use than Apache.  If you believe the hype, it's also faster and consumes fewer resources.  That's really not the point of this article, however.<!--more-->

This point of this article is to show you how you configure Nginx on your server to serve static content that is actually served by GitHub pages.

TL;DR
=====

1.  Create a `pages` repo
1.  Clone it to your local computer
1.  Check in you static files
1.  Set up your Nginx configuration file
1.  `git commit -am"..." && git push
1.  Profit!

GitHub Pages
============

[GitHub](https://github.com) alows users to store static web content (HTML, CSS, and JS) in specific repositories.  The only real caveat is that you must have `index.html` in your repository root.  Of course, your files will also be public if you are using the free service.  This service is called [GitHub Pages](https://pages.github.com/).  [Here is this blogs repository](https://github.com/mtik00/mtik00.github.io).


Content
=======

There are lots of ways to create your site.  I use [Hugo](http://gohugo.io) to generate the blog out of easy-to-generate Markdown files.  Nice and *relatively* simple.  However you do it, you'll need to be able to generate static content.

Nginx
=====

GitHub will serve up your pages to the web world just fine.  For this blog, you can go to https://mtik00.github.io to browse it.  It looks the same as https://mtik00.com, with the exception of the SSL key.  If you want users to go to your custom URL, and you want to manage your own SSL keys, you'll need to set up an Nginx *proxy*.

NOTE: If you don't care about SSL and only want a custom domain, read this instead: https://help.github.com/articles/setting-up-a-custom-domain-with-github-pages/

Since your content is hosted on GitHub, you only need an Nginx configuration file that redirects.  Here's the configuration that I use (without the SSL setup):

{{< highlight nginx >}}
server {
    server_name mtik00.com;
    listen 443 ssl spdy;

    # The site is actually hosted on github pages.  Using this proxy location
    # allows us to secure the connection with our own SSL keys, instead of the
    # generic github.io SSL keys.

    location / {
        proxy_pass https://mtik00.github.io;
        proxy_intercept_errors on;

        # allow GitHub to pass caching headers instead of using our own
        expires off;
    }
{{< /highlight >}}

The *magic* happens when a user navigates to https://mtik00.com/.  When the happens, the `location /` block matches, and all of the content is silently served from http://mtik00.github.io.  How cool is that?

Users will never know (nor will they care).

Why
===

This might all seem a bit silly.  Really, if already have a web server running Nginx, why set up the proxy in the first place?  Why not just store your content on the server?  Well, the way I see it, this method has the following benefits:

1.  `git commit -am"..." && git push` is all that's needed to update your site
1.  Your content won't take up any space on your web server
1.  You get to control your content entirely

Only you can decide if it's work it.  It is for me.  I can decide at any time to move the content off of GitHub, I can create new SSL keys as needed, and all I need to do to update is to `push` the new pages back up to GitHub.

Folder Structure
================

As I've mentioned before, I use Hugo to generate the static HTML files that are served by GitHub.  That, in itself, is a separate repository.  I started off with everything in the same repo.  It was a little odd, but it *wasn't quite right*.  My development files were in a folder called `dev`, and the generated HTML files were in the repo root.  I decided to make things a little more complex to make the static html file repo cleaner.

I currently have two projects:  1) My development files; 2) My GitHub pages static HTML files.  The trick here is that my GitHub pages repo is a *subtree* located inside my other repo.  It looks like this:

    mtik00-pages/
    mtik00-pages/mtik00.github.com

The base folder contains my development enviroment (batch files, python scripts, hugo binaries, etc).  The only thing `mtik00-pages/mtik00.github.com` contains are HTML/CSS/JS files.  My normal process goes like this:

1.  hugo new content/post
1.  edit the post in [SublimeText2](http://www.sublimetext.com/)
1.  commit the new content: `git add . && git commit -am"adding new post"`
1.  build the static pages:  `hugo -d"mtik00.github.com`
1.  deploy the static pages: `cd mtik00.github.com && git add -A . && git commit -am"new pages" && git push`
