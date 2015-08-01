+++
categories = ["hugo", "web", "python"]
date = "2015-07-31T17:40:02-06:00"
title = "Git and SSH Keys"
type = "post"
slug = "git-and-ssh-keys"
draft = true
+++

-   windows
-   %HOME%\.ssh\config
-   putty KeyGen (public/private)
    -   no password protection: protect this key!
-   Add to AWS instance / GitHub account
-   (alternatively use the password plugin windows app)

```
Host example.com ec2-111-111-111-111.us-west-2.compute.amazonaws.com
    User ubuntu
    IdentityFile <path to>aws-ubuntu-private.openssh
```
