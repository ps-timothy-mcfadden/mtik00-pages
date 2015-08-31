+++
categories = ["hugo", "web", "python"]
date = "2015-08-30T21:55:57-06:00"
title = "Django and Cripsy Form Login with Icons"
type = "post"
slug = "django-and-cripsy-form-login-with-icons"
+++

I recently created a website using the very nice [Edge](http://django-edge.readthedocs.org/en/latest/) template for a new Django site.  The log in form was nice, but I wanted a form with icons and no labels.  Here's how I did it...<!--more-->

The greatest thing is that this was a *super easy* change.  I think it looks a lot nicer, to boot.

Here's what the old login page looked like:
{{< figure src="/media/login-before.png" alt="Default edge login template" >}}


I used the incredible [`PrependedText`](http://django-crispy-forms.readthedocs.org/en/d-0/layouts.html?highlight=prependedtext) FormHelper item to add a [Font Awesome](http://fortawesome.github.io/Font-Awesome/) icon before the field.  I had to set the field labels to empty-strings, as I:

  1.    Couldn't figure out the `Field` item to set inside `PrependedText`
  1.    Couldn't use `self.helper.form_show_labels = False` because I needed it for the `remember_me` field.

Here's the python code:
{{< highlight python >}}
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["username"].label = ""
        self.fields["password"].label = ""
        self.helper.layout = Layout(
            PrependedText('username', '<i class="fa fa-envelope-o"></i>', placeholder="Enter Email Address"),
            PrependedText('password', '<i class="fa fa-key"></i>', placeholder="Enter Password"),
            HTML('<a href="{}">Forgot Password?</a>'.format(
                reverse("accounts:password-reset"))),
            Field('remember_me'),
            Submit('sign_in', 'Log in',
                   css_class="btn btn-lg btn-primary btn-block"),
        )
{{< /highlight >}}

Here's the new login form:
{{< figure src="/media/login-after.png" alt="New log in template" >}}

The is subtle, but effective!  (I think so, anyways)
