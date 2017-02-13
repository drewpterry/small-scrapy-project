# -*- coding: utf-8 -*-
from manageset.models import Kanji, Sentence, Words, SentenceOwner
import json
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TatoebaSentencePipeline(object):

    def __init__(self):
        self.file = open('items.jl', 'wb')

    def process_item(self, item, spider):
        self.store_json(item, spider)
        the_sentence = item['japanese_sentence']
        the_english_sentence = item['english_sentence']
        source_id = item['source_id']
        sentence_owner = item['sentence_owner']
        the_word = item['words']
        the_word_id = item['word_id']
        source_url = item['source_url']
        comment_exists = item['comment_exists']
        audio_url = item['audio']
 
        word_object = Words.objects.get(id = the_word_id)
        if sentence_owner == None:
	          sentence_owner = ' '

        if the_english_sentence == None:
            the_english_sentence = ' '
            word_object = Words.objects.get(id = the_word_id)
        try:
            owner_object = SentenceOwner.objects.get(name = sentence_owner)
        except ObjectDoesNotExist:   	
            owner_object = SentenceOwner.objects.create(name = sentence_owner).save()
        try:
            sentence_object = Sentence.objects.get(source_id = source_id)
            print "Sentence Exists"
            if Sentence.objects.filter(source_id = source_id, words__id = the_word_id).exists():
                print "THIS RELATIONSHIP ALREADY EXISTS"
            else:    
                word_object = word_object.sentence_set.add(sentence_object)
                print "THIS IS A NEW RELATIONSHIP"
        except ObjectDoesNotExist:
            word_object.sentence_set.create(japanese_sentence = the_sentence, english_sentence = the_english_sentence, source_id = source_id, sentence_owner = owner_object,  source_url = source_url, comment_exists = comment_exists, audio = audio_url)
            sentence_object = Sentence.objects.get(source_id = source_id)
        print sentence_object.japanese_sentence, sentence_object.english_sentence, sentence_object.source_id, sentence_object.sentence_owner, sentence_object.source_url, sentence_object.comment_exists, sentence_object.audio 
	
    def store_json(self, item, spider):
        print item['japanese_sentence'], " wrote JSON"
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
