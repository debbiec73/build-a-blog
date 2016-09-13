#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_main(self):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("main.html", posts=posts)

    def get(self):
        self.render_main()

class NewPost(Handler):
    def render_newpost(self, title="", body="", error=""):
        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Blog(title = title, body = body)
            a.put()

            blog_post_id = a.key().id()
            blog_post = Blog.get_by_id(int (blog_post_id) )
            response = ("<h1>" + blog_post.title + "</h1>" + "<p>" + blog_post.body + "</p>")

            self.response.write(response)
        else:
            error = "we need both a title and a body!"
            self.render_newpost(title, body, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        #blog_post_id = self.request.get("id")
        blog_post = Blog.get_by_id(int (id) )

        if blog_post:
             response = ("<h1>" + blog_post.title + "</h1>" + "<p>" + blog_post.body + "</p>")
             self.response.write(response)
        else:
            self.renderError(400)
            return

        #response = self.request.get("id")
        #blog_post = Blog.get_by_id()
        #self.response.write(2)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
],  debug=True)
