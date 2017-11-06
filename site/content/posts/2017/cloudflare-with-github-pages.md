+++
categories = ["web"]
date = "2017-11-06T10:10:08-07:00"
title = "Cloudflare with GitHub Pages"
type = "post"
slug = "cloudflare-with-github-pages"
+++

I recently changed my GitHub pages setup to incorporate the use of CloudFlare,
because, why not?

NOTE: If you don't have a domain, or don't care about CDN/Caching, the
instructions below are pointless!  Just point people to
`https://<username>.github.io`!

# Why

In my <a href="{{< relref "nginx-proxy-for-github-pages.md" >}}">
Nginx Proxy for GitHub Pages</a> post, I explained how
to set up your own web server using Nginx and Let's Encrypt to provide your
own SSL certificate and proxy requests to GitHub.  This is fine, but it still
adds a layer of complexity and requires your own VPS for set up.

I was recently poking around CloudFlare.  I found out that they have a *free*
tier that supports all kinds of neat things.  This includes a *shared* SSL
certificate (perfectly fine for GitHub Pages content), CDN, DNS, and of course
caching.  I'm always up for a *free* introduction to new-to-me technologies.

Personally, the biggest benefit is that I no longer have to deal with minimizing
anything!  CloudFlare offers the options to minimize things for you (and
bypass that when needed).  This means that my development workflow is quite a
bit easier.  This pretty much negates my
<a href="{{< relref "testing-pipelined-static-content.md" >}}">
Testing Pipelined Static Content</a> post!

# Steps

Full disclosure: Most of these steps are already online, so you could also
Google them too.

## CloudFlare

The first step was to sign up for a CloudFlare account.  That was easy.  During
the setup procress, CloudFlare figured out all of the DNS records I was using
(name servers, mail records, etc).  CloudFlare automatically sets them up as
one would expect.  For example, the `MX` records were left alone (which is
exactly what you want).  CloudFlare then tells you what to change on your 
registrar.  This makes it so all domain name lookups go through CloudFlare's
DNS.

## GitHub
The next step was to set up GitHub pages to know about our new domain.  This
is explained
<a href="https://help.github.com/articles/using-a-custom-domain-with-github-pages/">
in GitHub's online documentation</a>.  Just a quick settings change and a new
`CNAME` file.  One thing to note: you'll want to add a `.nojekyll` file to your
pages folder if you aren't using Jekyll.
<a href="https://github.com/blog/572-bypassing-jekyll-on-github-pages">(this is
the best link I found for that)</a>

## Wait

Now you wait!  `DNS` changes take a while to propogate through the system.  It
took my work network a full day to pick up the change; my home network only took
a few hours.  You'll know its been changed on your network when you run
`nslookup <domain>` and the result points to CloudFlare DNS.

## Back to CloudFlare

By now, you should be serving your content through CloudFlare connected to
GitHub.  There are some settings in CloudFlare that you may want to enable:

1.  `SSL Full`: On the **Crypto** page, you can set your `SSL` to `Full`.  This
    will encrypt the connection between CloudFlare and GitHub.  NOTE: You cannot
    use `Full (strict)` because your hostname is different from GitHub!  You'll
    get errors and your site won't work.
1.  `Browser Cache Expiration`: On the **Caching** page, you can now set the
    cache expiration.  If you use *cache busting* techniques, you can set this
    to something in the far future, like "6 months" or "1 year".
    `Always Online` is an interesting one too.
1.  `Auto Minify`: This is a handy feature on the **Speed** page.  I have
    CloudFlare automatically minify my JavaScript, CSS, and HTML.
1.  `Always Use HTTPS`: I like always redirecting to HTTPS.  AFter all, this is
    one of the reasons I'm using CloudFlare.  I've created a rule on the **Page Rules**
    page to always use https for `http://mtik00.com/*`.

NOTE: These changes take affect immediately(-ish).

# SSL

SSL/TLS is the biggest change.  I'm no longer encrypting `mtik00.com` with
Let's Encrypt.  This is because of 2 things:

1.  Visitors are presented with CloudFlare's SSL certificate
2.  CloudFlare communicates directly to GitHub using GitHub's SSL certificate

`mtik00.com` is no long providing any SSL.  That should make sense since `mtik00.com`
is really a *virtual* thing now.  All of the content is served by GitHub and
cached by CloudFlare.

# Posting Process

My process of creating a post is identical to before (thanks to scripting).
The only think I took out from my deployment script was the minification of
things.

# Caveats
Here are some things to consider when choosing this method.

*   Any DNS changes you need (e.g. `SPF`, `DKIM`, etc) will need to changed
    on CloudFlare's **DNS** settings page.
*   Your site will **NOT** use your certificate (unless you pay CloudFlare to
    manage one).  This is not the solution to use a domain-verified certificate.
*   This is mainly *fire and forget*.  Don't forget how things are set up!