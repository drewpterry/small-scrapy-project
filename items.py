# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy_djangoitem import DjangoItem
from manageset.models import Kanji, Sentence

import scrapy


class SentenceItem(DjangoItem):
    django_model = Sentence
    # define the fields for your item here like:
    words = scrapy.Field()
    word_id = scrapy.Field()
    pass
