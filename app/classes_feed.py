# -*- coding: utf-8 -*-

import feedparser
import threading
import tweepy
import time
from datetime import datetime

from flask import current_app, flash

from . import db
from . import infos_tweet
from .models import Feed, Article


class RssFlux():
    """
    Play arg "radio" in local HTML player.
    functions :
    > refresh (default rate = 1800 sec.)
    > activate() / deactivate()
    > get_articles
    """

    def __init__(self, idflux):
        """Connection init."""
        self.app = current_app._get_current_object()
        self.idflux = idflux
        flux_info = Feed.query.filter_by(id=self.idflux).first()

        self.name = flux_info.name
        self.url = flux_info.url
        self.collect_actif = flux_info.collect_actif
        self.Tweet_actif = flux_info.Tweet_actif
        self.user_id = flux_info.user_id
        # resfresh rate for geting articles (28800.0 = 8h)
        self.refresh = 28800.0
        self.frequency = (24/flux_info.frequency) * 3600

        if flux_info.hashtag:
            self.hashtag = flux_info.hashtag
        else:
            self.hashtag = ''
        # thread name
        # self.name_Thread = '{0} {1}'.format('thread', idflux)
        # print self.name_Thread

    def get_articles(self):
        """Get every self.refresh all new article of the feed and insert bdd"""
        # repeat in a thread every self.refresh the get_articles function
        # self.name_Thread = threading.Timer(self.refresh, self.get_articles).start()
        threading.Timer(self.refresh, self.get_articles).start()
        rss = self.url
        feeds = feedparser.parse(rss)

        with self.app.app_context():
            # titles list of all articles in bdd
            title_articles = Article.query.with_entities(Article.title).all()
            # list title/link from last 10 items of Rss feed not in bdd
            # feedss = [(feeds.entries[i]['title'], feeds.entries[i]['link'])
            #           for i in range(1, 10)
            #           if feeds.entries[i]['title'] not in title_articles]

            feedss = []
            for i in range(1, 10):
                if feeds.entries[i]['title'] not in title_articles:
                    add_news = [feeds.entries[i]['title'], feeds.entries[i]['link']]
                    feedss.append(add_news)
            # Add new items from list feedss to bdd
            for elem in feedss:
                article = Article(title=elem[0],
                                  url=elem[1])
                db.session.add(article)
            db.session.commit()
            print '=========='
            print feedss
            print '=========='
            print title_articles

    def activate_collect(self):
        """Activate Flux to get Articles."""
        if self.actif == 0:
            self.actif = 1
            self.get_articles()
        else:
            print 'Rss already enable'

    def desactivate_collect(self):
        """Desactivate Flux to get Articles."""
        if self.actif == 1:
            self.actif = 0
            # self.name_Thread.cancel()
        else:
            print 'Rss already disable'

    def tweet_articles(self):
        """Format and tweet articles from bdd."""
        # loop every self.frequency time over function with threading
        threading.Timer(self.frequency, self.tweet_articles).start()
        print self.frequency

        if self.Tweet_actif:
            articles_to_tweet = Article.query.\
                filter(Article.feed_id == self.idflux).\
                filter(Article.tweeted == 0).first()
            # checkingarticles to tweet
            if articles_to_tweet:
                auth = tweepy.OAuthHandler(infos_tweet.Key_consumer, infos_tweet.Consumer_secret)
                auth.set_access_token(infos_tweet.Access_token, infos_tweet.Access_token_secret)
                api = tweepy.API(auth)

                try:
                    # Title to the tweet Format
                    title = articles_to_tweet.title[:120]
                    # update twitted
                    articles_to_tweet.tweeted = 1
                    articles_to_tweet.date_tweeted = datetime.utcnow()
                    db.session.commit()
                    # send it
                    api.update_status(title)
                # check rate limit
                except tweepy.RateLimitError:
                    time.sleep(16 * 60)

        else:
            # inactive tweet function
            message = flash('Activate Tweet function for this feed !')
            print message

    def print_info(self):
        self.attrs = vars(self)
        print ', '.join("%s: %s" % item for item in self.attrs.items())
