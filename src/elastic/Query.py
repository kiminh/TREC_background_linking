#!/usr/bin/env python3

import os
import jieba
import re
import numpy as np
from elasticsearch import Elasticsearch
import xmlhandler as xh

INDEX_NAME = "news_alpha"
result_file = "bresults_trial.test"

# get file path conf
path_mp = {}
with open(os.getcwd()+'/../path.cfg', 'r', encoding='utf-8') as f:
	for line in f:
		li = line[:-1].split('=')
		path_mp[li[0]] = li[1]

es = Elasticsearch(port=7200)

topics = xh.get_topics(path_mp['DataPath'] + path_mp['topics'])
# get stop words list
stwlist = [line.strip() for line in open('stopwords.txt', encoding='utf-8').readlines()]
# doc length 595037
D = 595037


def test_backgound_linking():
	with open(result_file, 'w', encoding='utf-8') as f1:
		num = 1
		for mp in topics:
			# print(mp['num'].split(':')[1].strip())
			print("query docid", mp['docid'])
			num += 1
			# search by docid to get the query
			dsl = {
				'query': {
					'match': {
						'id': mp['docid']
					}
				}
			}
			res = es.search(index=INDEX_NAME, body=dsl)
			# print(res)
			doc = res['hits']['hits'][0]['_source']
			dt = doc['published_date']
			docid = doc['id']
			print("found docid: ", docid)
			# print(doc)
			# remove stop words
			text = re.sub('[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+', '', doc['title_body'])
			words = "#".join(jieba.cut(text)).split('#')
			q = {}
			tf = {}
			for w in words:
				if w != "" and w != ' ' and w not in stwlist:
					if w in tf:
						tf[w] += 1.0
					else:
						tf[w] = 1.0
					# calc idf
					dsl = {
						"size": 0,
						'query': {
							'match_phrase': {
								'title_body': w
							},
						},
						"aggs": {
							"idf": {
								"terms": {
									"field": "source.keyword"
								}
							}
						}

					}
					res = es.search(index=INDEX_NAME, body=dsl)
					res = res['aggregations']['idf']['buckets']
					idf = 0.0
					for dc in res:
						idf += dc['doc_count']
					if idf > 0.0:
						q[w] = np.log(D / idf)
					else:
						q[w] = 0.0
			for w in q.keys():
				q[w] *= tf[w]
				# q now contains the tf * idf for each word
			q = sorted(q.items(), key=lambda x: x[1], reverse=True)
			query = ""
			sz = min(20, len(q))
			cnt = 0
			for w in q:
				if cnt >= sz:
					break
				query += ' ' + w[0]
				cnt += 1
			# query the doc
			dsl = {
				"query": {
					'bool': {
						'must': {
							'match': {'title_body': query}
						},
						"must_not": {"match": {"id": docid}},
						'filter': {
							"range": {"published_date": {"lt": dt}}
						}
					},
				}
			}
			res = es.search(index=INDEX_NAME, body=dsl)
			res = res['hits']['hits']
			# output result.test file
			print('Number of hits:', len(res))
			print('Writing to file: ', result_file)
			cnt = 1
			for ri in res:
				out = []
				out.append(mp['num'].split(':')[1].strip())
				out.append('Q0')
				out.append(ri['_source']['id'])
				out.append(str(cnt))
				out.append(str(ri['_score']))
				out.append('NEWAPPROACH')
				ans = "\t".join(out) + "\n"
				f1.write(ans)
				cnt += 1
	return


test_backgound_linking()
