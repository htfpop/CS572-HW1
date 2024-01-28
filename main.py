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
from selenium.webdriver.chrome.options import Options

USER_AGENT = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2810.1 Safari/537.36'}

BASE_URL = 'http://www.ask.com/web?q='


class SearchEngine:
	def __init__(self):
		self.query_set = None
		self.search_engine = 'Ask.com'
		self.queries = []
		self.google_json = {}
		self.urlSet = set()

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
	# sanity check to make sure we are on the same page as google json
	for query in e.queries:
		# Use Selenium to parse JS
		chrome_options = Options()
		chrome_options.add_argument("--headless")
		driver = webdriver.Chrome(chrome_options)

		# Make sure the query in list is actually inside the json file
		if len(e.google_json[query]) != 0:
			split_query = '+'.join(query.split())
			final_query = BASE_URL + split_query
			print(f'[Processing]: {query} - {final_query}\r')

			# fetch Ask.com
			driver.get(final_query)

			# using BS4 to process Ask.com
			soup = BeautifulSoup(driver.page_source, 'html.parser')

			print(f'Results from {final_query}\r')

			#urls = soup.find_all('div', class_="result-url-section")
			titles = soup.find_all('div', class_="result-title")

			for title in titles:
				t_title = title.find_next('a')
				link = t_title['href']
				header = t_title['title']
				print(f'{header} ||| {link}')
				driver.get(link)
				#driver.implicitly_wait(5)
				fetch = driver.current_url
				if link != fetch:
					print(f'[Link Redirect]: OLD: {link} ||| NEW: {fetch}')
				#e.urlSet.add(link)

			wait = random.randrange(5, 10)
			print(f'[SLEEP {wait}]')
			sleep(wait)

			driver.quit()



if __name__ == '__main__':
	# test()
	print("------------------------------------------")
	print(" CSCI-572 | Web Search Engine Comparison  ")
	print("------------------------------------------")

	engine = SearchEngine()
	engine.query_open('./Queries/100QueriesSet3.txt')
	# print(engine)
	# engine.get_queries()
	engine.google_query_open('./Queries/Google_Result3.json')
	# engine.get_google_json()
	parser(engine)
	# test2(engine)
	# test3()
