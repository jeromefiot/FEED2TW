# -*- coding: utf-8 -*-

import feedparser
import tweepy
import time
from datetime import datetime
import random
from threading import Timer

from flask import current_app, flash
from flask.ext.login import current_user

from . import db
from . import infos_tweet
from .models import Feed, Article


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# THREADING TEST
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

class RepeatedTimer(object):
    """
    Run function (arg or not) every interval seconds
    http://stackoverflow.com/questions/3393612/
    run-certain-code-every-n-seconds
    """

    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class RssFlux():
    """
    Activate get_articles (and func to deactivate : desactivate_collect).
    Activate tweet_articles (and func to deactivate : desactivate_tweet).
    functions :
    > refresh (default rate = 1800 sec.)
    > activate() / deactivate()
    > get_articles
    > Tweet articles from (self) Feed
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
        # resfresh rate for geting articles (28800.0 = 8h)
        self.refresh = 610.0  # every 10mn
        # self.frequency = (24/flux_info.frequency) * 3600
        self.frequency = 600.0  # every 10mn

        if flux_info.hashtag:
            self.hashtag = flux_info.hashtag
        else:
            self.hashtag = ''
        # thread name
        # self.name_Thread = '{0} {1}'.format('thread', idflux)
        # print self.name_Thread

    def get_articles(self):
        """Get every self.refresh all new artle of feed and insert bdd."""
        # repeat in a thread every self.refresh the get_articles function
        # self.name_Thread = threading.Timer(self.refresh, self.get_articles).start()
        # Timer(self.refresh, self.get_articles).start()
        rss = self.url
        feeds = feedparser.parse(rss)

        with self.app.app_context():
            db.session.expunge_all()
            # titles list of all articles in bdd
            title_articles = [element.title for element in
                              Article.query.filter(Article.feed_id == self.idflux)]
            # list title/link from last 10 items of Rss feed not in bdd
            feedss = [(feeds.entries[i]['title'], feeds.entries[i]['link'])
                      for i in range(1, 10)
                      if feeds.entries[i]['title'] not in title_articles]

            # Add new items from list feedss to bdd
            for elem in feedss:
                article = Article(title=elem[0],
                                  url=elem[1],
                                  feed_id=self.idflux)
                db.session.add(article)
            db.session.commit()
            print "SCRAPP ARTICLE EFFECTUE"

    def tweet_articles(self):
        """Format and tweet articles from bdd for self.flux."""
        with self.app.app_context():
            articles_to_tweet = Article.query.\
                filter(Article.feed_id == self.idflux).\
                filter(Article.tweeted == 0).all()

            # checkingarticles to tweet
            if articles_to_tweet:
                auth = tweepy.OAuthHandler(infos_tweet.Key_consumer, infos_tweet.Consumer_secret)
                auth.set_access_token(infos_tweet.Access_token, infos_tweet.Access_token_secret)
                api = tweepy.API(auth)

                try:
                    for tweets in articles_to_tweet:
                        # TITLE // LINK -> tweet_content
                        title = tweets.title[:100]
                        link_article = tweets.url
                        # FEED name for VIA -> tweet_content
                        name_feed = Feed.query.\
                                    filter(Feed.id == Article.feed_id).first()
                        via_article = name_feed.name.split()[0]

                        tweet_content = "%s // %s - via %s" %\
                                        (title, link_article, via_article)
                        # update twitted
                        tweets.tweeted = 1
                        tweets.date_tweeted = datetime.utcnow()
                        db.session.commit()
                        # send it
                        api.update_status(tweet_content)
                        # wait randomly
                        time.sleep(600 + random.randint(30, 60))
                        print "Tweet ID : "+str(tweets.id)+" : ENVOYE"
                # check rate limit
                except tweepy.RateLimitError:
                    time.sleep(16 * 60)
            else:
                # no tweet to send
                message = flash('No tweets to send')
                print message

    def activate_get(self):
        """Activate Flux to get Articles."""
        print self.collect_actif
        if not self.collect_actif:
            print "enter activate_get"
            self.rt2 = RepeatedTimer(self.refresh, self.get_articles)
            # update Feed
            flux_info = Feed.query.filter_by(id=self.idflux).first()
            flux_info.collect_actif = True
            db.session.commit()
            print self.rt2
        else:
            print 'Collect already enable'

    def desactivate_get(self):
        """Desactivate Flux to get Articles."""
        if self.rt2.is_running:
            self.rt2.stop()
            # update Feed
            flux_info = Feed.query.filter_by(id=self.idflux).first()
            flux_info.collect_actif = False
            db.session.commit()
        else:
            print 'Collect already disable'

    def activate_tweet(self):
        """Activate Flux to get Articles."""
        print "State TWEET (Tweet_actif) : "
        print self.Tweet_actif
        if not self.Tweet_actif:
            print "enter activate_tweet"
            self.rt = RepeatedTimer(self.frequency, self.tweet_articles)
            # update Feed
            flux_info = Feed.query.filter_by(id=self.idflux).first()
            flux_info.Tweet_actif = True
            db.session.commit()
            print self.rt
        else:
            print 'Tweet already enable'

    def desactivate_tweet(self):
        """Desactivate Flux to get Articles."""
        if self.rt.is_running:
            self.rt.stop()
            # update Feed
            flux_info = Feed.query.filter_by(id=self.idflux).first()
            flux_info.Tweet_actif = False
            db.session.commit()
        else:
            print 'Tweet already disable'

    def state(self):
        """Print effective actions (tweet_articles / get_articles)."""
        if self.rt.is_running is True:
            if self.rt2.is_running is True:
                return self.name+" : Collecting and Tweeting actif."
            return self.name+" : Tweeting is actif."
        elif self.rt2.is_running is True:
            return self.name+" : Collecting is actif."
        else:
            print 'No actions'

    def print_info(self):
        self.attrs = vars(self)
        print ', '.join("%s: %s" % item for item in self.attrs.items())

if __name__ == '__main__':
    pass
