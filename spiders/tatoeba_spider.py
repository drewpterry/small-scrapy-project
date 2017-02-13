# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from tatoeba_sentence.items import SentenceItem
import json
from manageset.models import Kanji, Sentence, Words, SentenceOwner
import logging
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
import pdb

class TatoebaSentenceSpider(scrapy.Spider):
    name = "sentences"
    rotate_user_agent = True
    allowed_domains = ["tatoeba.org", "jisho.org"]
    
    def __init__(self):
        self.file = open('failed_urls.jl', 'wb')
        self.url = ''

    def start_requests(self):
        count = 0
        all_words = Words.objects.filter(sentence_scrape=False).order_by('-combined_frequency') 
        # all_words = Words.objects.filter(real_word = '彼処') 
        for word in all_words:
            word.sentence_scrape = True 
            word.save()
            count += 1
            if word.real_word == "none":
                vocab_word = word.hiragana
            else:
                vocab_word = word.real_word
            url = 'http://jisho.org/search/' + vocab_word + '%23sentence'
            self.url = url
            the_request = scrapy.Request(url, self.parse, errback=self.on_error, meta={'word': vocab_word, 'word_id': word.id})
            yield the_request

    def parse(self, response):
        print response.meta['word']
        for sentence in response.css('.inline_copyright'):
            tatoeba_url = sentence.css('a::attr(href)').extract()
            jisho_url = response.url
            response_word = response.meta['word']
            url_id = tatoeba_url[0].rsplit('/',1)[1]
            word_id = response.meta['word_id']
            relation_exists = Sentence.objects.filter(source_id=url_id, words__id = word_id).exists()
            if relation_exists:
                print 'RELATION ALREADY EXISTS: SKIPPING'
                pass
            else:
                request = Request(tatoeba_url[0], callback=self.parse_tatoeba)
                request.meta['word'] = response.meta['word']
                request.meta['word_id'] = response.meta['word_id']
                yield request

        next_page = response.css(".more::attr('href')")
        if next_page:
            url = response.urljoin(next_page[0].extract())
            request = Request(url, self.parse)
            request.meta['word'] = response.meta['word']
            request.meta['word_id'] = response.meta['word_id']
            yield request

    def parse_tatoeba(self, response):
        for sentence_set in response.css('.sentences_set'):

            item = SentenceItem()

            japanese_sentence = sentence_set.css('.mainSentence .text::text').extract()[0]
            english_sentence = sentence_set.css('.correctnessZero:lang(en)::text').extract()
            sentence_owner = response.css('.adopt-item::text').extract()
            no_comment = response.css('.module em')
            audio_url = sentence_set.css('.audio a::attr(href)').extract()
            try:
                item['sentence_owner'] = sentence_owner[0]
                print "sentence owner is: ", sentence_owner[0]
            except:
                item['sentence_owner'] = ' '		    
            if english_sentence: 
                item['english_sentence'] = english_sentence[0]
            else:
                item['english_sentence'] = ' '
            if no_comment:
                item['comment_exists'] = False
            else:
                item['comment_exists'] = True
            if audio_url:
                item['audio'] = audio_url[0]
            else:
                item['audio'] = ''
            item['japanese_sentence'] = japanese_sentence
            item['source_url'] = response.url
            item['source_id'] = response.url.rsplit('/',1)[1]
            item['words'] = response.meta['word']
            item['word_id'] = response.meta['word_id']
            yield item

    def error_call(self, failure):
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))

        #if isinstance(failure.value, HttpError):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)



    def on_error(self, failure):
        # if isinstance(failure.value, HttpError):
        # response = failure.value.response
        print "There was an error"
        failed_url = failure.request.url
        failure_message = failure.value.message
        word_id = failure.request.meta['word_id']
        failed_word = Words.objects.get(id=word_id)
        failed_word.scrape_failed = True
        failed_word.save()
        failure_info = [failed_word.id, failed_word.real_word, failed_url, failure_message]
        # print failure_info
        line = json.dumps(failure_info) + "\n"
        print line
        self.file.write(line)
        return True
