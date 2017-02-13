from random import choice
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy import log
from scrapy.conf import settings
import random


# class RotateUserAgentMiddleware(object):
#     """Rotate user-agent for each request."""
#     def __init__(self, user_agents):
#         self.enabled = False
#         self.user_agents = user_agents
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         user_agents = crawler.settings.get('USER_AGENT_CHOICES', [])
#         if not user_agents:
#             raise NotConfigured("USER_AGENT_CHOICES not set or empty")
#
#         o = cls(user_agents)
#         crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
#
#         return o
#
#     def spider_opened(self, spider):
#         self.enabled = getattr(spider, 'rotate_user_agent', self.enabled)
#
#     def process_request(self, request, spider):
#         if not self.enabled or not self.user_agents:
#             return
#         request.headers['user-agent'] = choice(self.user_agents)
#         spider.log(
#                        u'User-Agent: {} {}'.format(request.headers.get('User-Agent'), request),
#                        level=log.DEBUG
#                    )
#
# class ProxyMiddleware(object):
#     def process_request(self, request, spider):
#         request.meta['proxy'] = settings.get('HTTP_PROXY')

class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua  = random.choice(settings.get('USER_AGENT_CHOICES'))
        if ua:
            request.headers.setdefault('User-Agent', ua)
            spider.log(
                u'User-Agent: {} {}'.format(request.headers.get('User-Agent'), request),
                level=log.DEBUG
            )

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('HTTP_PROXY')