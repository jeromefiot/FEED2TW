from flask import render_template, redirect, url_for, abort, flash,\
                  request, current_app
from flask.ext.login import login_required, current_user
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin

import feedparser
import time

from . import main
from ..classes_feed import RssFlux

from .forms import EditProfileForm, EditProfileAdminForm, AddFeed
from .. import db, admin
from ..models import Role, User, Feed, Article
from ..decorators import admin_required


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES PUBLIQUES
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/contact')
def contact():
    return render_template('contact.html')


@main.route('/credits')
def credits():
    return render_template('credits.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES INSCRITS
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.telephone = form.telephone.data
        current_user.location = form.location.data
        current_user.codepostal = form.codepostal.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.telephone.data = current_user.telephone
    form.location.data = current_user.location
    form.codepostal.data = current_user.codepostal
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES @ADMIN_REQUIRED
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------


@main.route('/add_feed', methods=['GET', 'POST'])
@login_required
@admin_required
def add_feed():
    form = AddFeed()
    user_feeds = Feed.query.filter_by(user_id=current_user.id).all()
    if form.validate_on_submit():
        feed = Feed(name=form.name.data,
                    url=form.url.data,
                    actif=form.actif.data)
        db.session.add(feed)
        flash('The Feed has been added.')
        return redirect(url_for('.add_feed'))
    return render_template('main/add_form.html', form=form, feeds=user_feeds)


@main.route('/articles/<int:id_feed>', methods=['GET', 'POST'])
@login_required
@admin_required
def articles(id_feed):
    user_feeds = Feed.query.filter_by(id=id_feed).first()

    rss = user_feeds.url
    syndication_number = 10
    feeds = feedparser.parse(rss)

    feedss = [(i, feeds.entries[i]['title'], feeds.entries[i]['link'])
              for i in range(1, syndication_number)]
    # condition rajoutable sur les titres a sortir =
    # if 'commercial' in feeds.entries[i]['title']]

    return render_template('main/feed_articles.html', articles=feedss)


@main.route('/all_articles', methods=['GET', 'POST'])
@login_required
@admin_required
def all_articles():
    user_feeds = Article.query.all()

    return render_template('main/all_articles.html', articles=user_feeds)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.telephone = form.telephone.data
        user.location = form.location.data
        user.codepostal = form.codepostal.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.telephone.data = user.telephone
    form.location.data = user.location
    form.codepostal.data = user.codepostal
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/list_users/', methods=['GET', 'POST'])
@login_required
@admin_required
def list_users():
    user = User.query.all()
    if request.method == 'POST':
        flash("Suppression de id")

    return render_template('list_users.html', user=user)


@main.route('/zob', methods=['GET', 'POST'])
@login_required
@admin_required
def zob():
    test = RssFlux(1)
    test.tweet_articles()

    return render_template('index.html')

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES ADMIN
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

class MyModelView(ModelView):
    # remove "password_hash"
    # http://flask-admin.readthedocs.org/en/latest/api/mod_model/#flask.ext.admin.model.BaseModelView)
    column_exclude_list = ('password_hash')

    # Accessible only by admin
    @admin_required
    def is_accessible(self):
        return current_user.is_administrator()


class MyModelView2(ModelView):
    pass


class MyModelView3(ModelView):
    pass

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView2(Feed, db.session))
admin.add_view(MyModelView3(Article, db.session))

# pour la vue avec tous les arg, sinon Myview3
# admin.add_view(ModelView(User, db.session))
