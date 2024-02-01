""" **************************************************************
* Programmer : Christopher K. Leung (2965-7518-69)               *
* Course ID  : CSCI572 - Information Retrieval and               *
*                         Web Search Engines                     *
* Due Date   : January 31, 2024                                  *
* Project    : Web Search Engine Comparison                      *
* Purpose    : This Python script will query search engines and  *
*               will compute the Spearman rank correlation       *
*               coefficient against the Ask.com search engine    *
*****************************************************************"""
import json
import random
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from datetime import datetime

USER_AGENT = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2810.1 Safari/537.36'}

BASE_URL = 'http://www.ask.com/web?q='

LOGFILE = './logs/log'

MAX_RETRIES = 10
TIMEOUT = 30

CURRENT_TIME = ""

summary = {}


class SearchEngine:
	def __init__(self):
		self.query_set = None
		self.search_engine = 'Ask.com'
		self.queries = []
		self.google_json = {}
		self.urlSet = set()
		self.file = None
		self.json = None

	def query_open(self, path):
		with open(file=path, mode='r') as f:
			lines = f.readlines()
			for line in lines:
				if line == "\n":
					continue
				self.queries.append(line.strip())

		self.query_set = path

		# check to make sure there are 100 queries
		if len(self.queries) != 100:
			print(f'[ERROR]: Could not find 100 Queries in {path}\r\nExiting now..\r\n')
			exit(-1)

	def log_open(self, i=1):
		global CURRENT_TIME
		now = datetime.now()
		current_time = now.strftime("%m%d%Y_%H%M%S")
		CURRENT_TIME = current_time
		print("Current Time =", CURRENT_TIME)
		self.file = open(LOGFILE + CURRENT_TIME + f'_i{i}' + '.txt', 'w', encoding='utf-8', buffering=1)

	def json_open(self, i=1):
		global CURRENT_TIME
		self.json = open(LOGFILE + CURRENT_TIME + f'_i{i}' + '.json', 'w')

	def log_write(self, s):
		print(s)
		self.file.write(s)

	def log_close(self):
		self.file.close()

	def json_write(self, s: dict):
		json.dump(s, self.json, indent=3)

	def json_close(self):
		self.json.close()

	def google_query_open(self, path):
		with open(file=path, mode='r') as f:
			self.google_json = json.load(f)

		# check to make sure there are 100 queries
		if len(self.google_json) != 100:
			print(f'[ERROR]: Could not find 100 json entries in {path}\r\nExiting now..\r\n')
			exit(-1)

	def get_queries(self):
		print("---Printing 100 Queries:---")
		for x, query in enumerate(self.queries, start=1):
			print(f'[Query {x}]: {query}')

	def get_google_json(self):
		print("---Printing Google Json Queries:---")
		print(json.dumps(self.google_json, indent=3))

	@staticmethod
	def search(query, sleep=True):
		# if sleep:  # Prevents loading too many pages too soon
		# time.sleep(randint(10, 100))
		temp_url = '+'.join(query.split())  # for adding + between words for the query
		# url = 'http://www.ask.com/web?q=' + temp_url

		render = 'http://www.ask.com/web?q=' + temp_url
		html = requests.get(render, headers=USER_AGENT).text
		soup = BeautifulSoup(html, 'html.parser')

		# soup = BeautifulSoup(requests.get(url, headers=USER_AGENT).text, "html.parser")
		print(soup.prettify())
		new_results = SearchEngine.scrape_search_result(soup)
		return new_results

	@staticmethod
	def scrape_search_result(soup):
		raw_results = soup.find_all('["div", attrs = {"class" : "PartialSearchResults-item-title"}]')
		results = []
		# implement a check to get only 10 results and also check that URLs must not be duplicated
		for result in raw_results:
			link = result.get('href')
			results.append(link)
		return results

	def __str__(self):
		s = '[Search Engine]: {}\n' \
		    '[Query Set]: {}\n' \
			.format(self.search_engine, self.query_set)
		return s


# URL = 'https://www.ask.com/web?ueid=CF726D1B-EE50-4271-9B93-A607D8890554&an=organic&ad=dirN&locale=en_US&qo=serpSearchTopBox&q=raytheon'
URL = 'https://www.ask.com/web?ueid=CF726D1B-EE50-4271-9B93-A607D8890554&an=organic&ad=dirN&locale=en_US&qo=serpSearchTopBox&q=billgates'


def test():
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	driver = webdriver.Chrome(chrome_options)

	driver.get(URL)
	driver.implicitly_wait(5)

	# print(driver.page_source)

	# title = driver.find_element(By.TAG_NAME, 'title').text
	# print("Page Title:", title)
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	# print(soup.prettify())

	print("getting results")
	# results = soup.find_all('div', class_='result')
	# for result in results:
	# Obtain nested divs (3):  result-url-section, result-title, result-abstract
	# url_div = results.find_all_next('div', class_="result-url-section")
	# title_div = results.find_all_next('div', class_="result-title")
	# result_div = result.find_all_next('div', class_="result-abstract")
	urls = soup.find_all('div', class_="result-url-section")
	titles = soup.find_all('div', class_="result-title")

	for title in titles:
		t_title = title.find_next('a')
		link = t_title['href']
		header = t_title['title']
		print(f'{header} ||| {link}')

	# href = result.getText('href')
	# title = result.getText('title')
	# print(f'{title} : {href}')

	"""
	req = requests.get(URL, headers=USER_AGENT)
	print(req.text)
	soup = BeautifulSoup(req.text, 'html.parser')
	#print(soup.text)
	"""


def test2(e: SearchEngine):
	"""
	testing json accesses
	:param e: search engine object
	:return: none
	"""
	print(f'Len of e json: {len(e.google_json)}')

	for key in e.google_json:
		for val in range(len(e.google_json[key])):
			print(f'KEY: {key} ||| VAL: {e.google_json[key][val]}')


def test3():
	"""
	Testing to see if I can get a redirect link
	:return: none
	"""
	driver = webdriver.Chrome()
	link = 'http://www.has-sante.fr/portail/jcms/c_676945/fr/prialt-ct-5245'

	driver.get(link)
	print(driver.current_url)


def parser(e: SearchEngine):
	global summary
	# sanity check to make sure we are on the same page as google json
	out_dict = {}
	curr_query = 1
	for query in e.queries:
		query_hits = 0
		total_url = len(e.google_json[query])
		g_query_list = []
		curr_query_str = f'Query {curr_query}'
		result_list = []

		# Use Selenium to parse JS
		chrome_options = Options()
		chrome_options.add_argument("--headless")
		# chrome_options.add_argument("--disable-notifications")
		driver = webdriver.Chrome(chrome_options)
		driver.set_page_load_timeout(TIMEOUT)

		# Make sure the query in list is actually inside the json file
		if len(e.google_json[query]) != 0:

			# Append sanitized google query
			for url in range(total_url):
				g_query_list.append(url_filter(e.google_json[query][url]))

			# DEBUG print out google query
			for url in range(len(g_query_list)):
				print(g_query_list[url])

			split_query = '+'.join(query.split())
			final_query = BASE_URL + split_query

			# printout
			e.log_write(f'[Processing]: {query} - {final_query}\r\n')

			count1 = 0
			# fetch Ask.com
			while count1 < MAX_RETRIES:
				try:
					driver.get(final_query)
					break
				except TimeoutException:
					print(f'[ERROR]: Ask.com request timeout\r')
					count1 += 1

			if count1 == MAX_RETRIES:
				print(f'Cannot scrape, Exiting...\r\n')
				exit(-100)

			# using BS4 to process Ask.com
			soup = BeautifulSoup(driver.page_source, 'html.parser')

			# printout
			e.log_write(f'Results from {final_query}\r')

			# urls = soup.find_all('div', class_="result-url-section")
			titles = soup.find_all('div', class_="result-title")

			# for calculating spearman's
			webpage_index = 1
			google_index = 0
			cumulative_sum = 0
			rho = 0
			google_rank = []
			ask_rank = []
			for title in titles:
				if len(result_list) == 10:
					e.log_write(f'---Found 10 entries for this query---')
					break

				t_title = title.find_next('a')
				link = t_title['href']
				header = t_title['title']

				# sanitize entire url
				sanitized_url = url_filter(link)

				# sanitize only ending to keep http / https
				no_uid = no_uid_url(link)

				count2 = 0
				# fetch actual website
				while count2 < MAX_RETRIES:
					try:
						sleep_val = random.randrange(1, 3)
						sleep(sleep_val)

						driver.get(link)

						# printout
						e.log_write(f'[{sleep_val} sec]: {header} ||| {sanitized_url}\r')

						result_list.append(no_uid)

						break
					except TimeoutException:
						print(f'PAGE REQUEST TIMEOUT RETRYING: {header} ||| {link}\r')

						# Quit Selenium
						driver.quit()

						# Re-initialize Selenium
						driver = webdriver.Chrome(chrome_options)

						# Invoke sleep to prevent IP Ban
						sleep(10)

						count2 += 1

				if count2 == MAX_RETRIES:
					print(f'Cannot fetch websites, Exiting...\r\n')
					exit(-200)

				fetch = driver.current_url
				if link != fetch:
					# printout
					e.log_write(f'[Link Redirect]: OLD: {link} ||| NEW: {fetch}\r')

				hit = False
				# Check if we have a match
				for url in range(len(g_query_list)):
					if g_query_list[url] == sanitized_url:
						e.log_write(
							f'[MATCHED]: google index {url + 1} ||| ask index {webpage_index} ||| {g_query_list[url]} ||| {sanitized_url}\r')
						query_hits += 1
						google_index = url + 1
						google_rank.append(google_index)
						ask_rank.append(webpage_index)
						hit = True
					elif g_query_list[url] == url_filter(fetch) and not result_list.__contains__(fetch):
						e.log_write(
							f'[MATCHED]: google index {url + 1} ||| ask index {webpage_index} ||| {g_query_list[url]} ||| {fetch}\r')
						query_hits += 1
						google_index = url + 1
						google_rank.append(google_index)
						ask_rank.append(webpage_index)
						hit = True

				if hit:
					# calculate cumulative sum
					cumulative_sum += (google_index - webpage_index) ** 2

				# increment webpage index to keep track of next webpage
				webpage_index += 1

			# spearman's calculation
			if query_hits == 0:
				rho = 0
			elif query_hits == 1:
				# Capture the following:
				# if Rank in your result = Rank in Google result → rho=1
				# if Rank in your result ≠ Rank in Google result → rho=0
				if google_rank[0] == ask_rank[0]:
					rho = 1
				else:
					rho = 0
			else:
				rho = 1 - ((6 * cumulative_sum) / ((query_hits ** 3) - query_hits))

			# Complete parse through all titles, quit Selenium for refresh
			driver.quit()

			append = {curr_query_str: result_list}
			out_dict.update(append)

			e.log_write(f'Query {curr_query} Hits: {query_hits} ||| Overlap: {query_hits / 10} ||| rho: {rho}\r')
			summary.update({'Query ' + str(curr_query): {'q_hits': query_hits, 'overlap': query_hits / 10, 'rho': rho}})

		wait = 3
		# printout
		e.log_write(f'[SLEEP {wait}]\r\n')
		sleep(wait)

		curr_query += 1

	e.json_write(out_dict)


def url_filter(url: str):
	temp_url = url.replace('https://www.', '').replace('http://www.', '').replace('https://', '').replace('http://',
	                                                                                                      '').rstrip(
		'/')
	index = temp_url.find('?utm_content=')
	if index > 0:
		return temp_url[:index]

	return temp_url


def no_uid_url(url: str):
	ret_url = url
	index = ret_url.find('?utm_content=')
	if index > 0:
		return ret_url[:index]
	return url


def test4():
	data = {
		'query1': ['value1', 'value2', 'value3']
	}

	temp = {'query2': ['value11', 'value12', 'value31']}

	data.update(temp)

	with open('test.json', 'w') as json_file:
		json.dump(data, json_file, indent=3)


def print_summary(e: SearchEngine):
	global summary
	avg_hits = 0
	avg_overlap = 0
	avg_rho = 0
	for query, data in summary.items():
		hits = data['q_hits']
		avg_hits += hits
		overlap = data['overlap']
		avg_overlap += overlap
		rho = data['rho']
		avg_rho += rho
		e.log_write(f'Query {query}: Hits: {hits} ||| Overlap: {overlap} ||| Rho: {rho}\r')

	e.log_write(f'Avg hit: {avg_hits/100} ||| Avg Overlap {avg_overlap/100} ||| Avg Rho: {avg_rho/100}\r')



if __name__ == '__main__':
	# test()
	print("------------------------------------------")
	print(" CSCI-572 | Web Search Engine Comparison  ")
	print("------------------------------------------")

	for x in range(5):
		print(f'ITERATION {x}\r\n')

		engine = SearchEngine()
		engine.log_open(x)
		engine.json_open(x)
		engine.query_open('./Queries/100QueriesSet3.txt')
		# print(engine)
		# engine.get_queries()
		engine.google_query_open('./Queries/Google_Result3.json')
		# engine.get_google_json()
		parser(engine)

		print_summary(engine)
		# test4()
		engine.log_close()
		engine.json_close()
		# test2(engine)
		# test3()

		engine = None
