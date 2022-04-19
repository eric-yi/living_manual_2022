#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random

try:
    from agents import AGENTS
except Exception:
    from crawler.agents import AGENTS


class AgentMiddleware:
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent
