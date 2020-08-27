# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 2020 

@author: Stefan Mager and Christopher Henkel
"""

### Feel free to use the code for the automated download of journal article information.
# However, keep in mind that you might be blocked by the Springer website if you
# execute the code too often within a short amount of time. ###

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

timestamp = datetime.now().strftime("%H-%M-%S")
print(timestamp)

journals = [{
    "name": "bise",
    "id": "12599"}, {
    "name": "em",
    "id": "12525"}]


def find_max_num_pages(url):
    num_pages = 0
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features='html.parser')
    total_pages_soup = soup.find("input", {"name": "total-pages"})
    if total_pages_soup is not None:
        num_pages = int(total_pages_soup)["value"]
    return num_pages


def start_scraping():
    for journal in journals:
        max_pages = find_max_num_pages(url='https://link.springer.com/journal/' + journal['id'] + '/onlineFirst')
        print(max_pages)
        if max_pages > 0:
            for i in range(max_pages):
                page_number = i + 1
                page_url = 'https://link.springer.com/journal/' + journal['id'] + '/onlineFirst/page/' + str(
                    page_number)
                scrape_articles(url=page_url, outlet=journal['name'])
        else:
            page_url = 'https://link.springer.com/journal/' + journal['id'] + '/onlineFirst'
            scrape_articles(url=page_url, outlet=journal['name'])


# refactor: da ich den gleichen Code dreimal gebraucht hätte, ist es effizienter dies einmal als Funktion zu schreiben
def strip_html_element(element):
    return " ".join(element.text.split())


def scrape_articles(url, outlet, skip=False):
    print(url)
    r = requests.get(url)
    file_name = outlet + "_request_download.txt"
    file = open(file_name, "w", encoding="utf-8")
    file.write(r.text)
    file.close()

    file = open(file_name, "r", encoding="utf-8")
    html = file.read()
    file.close()

    soup = BeautifulSoup(html, features='html.parser')

    all_articles = []

    issue_items = soup.findAll(class_="c-list-group__item")
    print('number of toc-items found: ' + str(len(issue_items)))
    skip_first = skip
    for i in issue_items:
        if skip_first:
            skip_first = False
            continue

        current_article_authors = []

        h5_title = i.find(class_="c-card__title")
        title_strip = strip_html_element(h5_title)
        current_article_titles = title_strip
        print('Title: ' + current_article_titles)

        all_authors = i.findAll("span", itemprop="name")
        for single_author in all_authors:
            author_strip = strip_html_element(single_author)
            current_article_authors.append(author_strip)
        print('Authors: ' + str(current_article_authors))

        link = i.find(class_="c-card__title")
        h5_link = link.find("a", itemprop="url")
        # TODO: Potential Issue if you want to scrape other sites apart from informs
        current_article_links = h5_link.attrs["href"]

        current_article_abstracts = scrape_abstract(current_article_links)

        all_articles.append({
            "authors": current_article_authors,
            "title": current_article_titles,
            "links": current_article_links,
            "abstract": current_article_abstracts,
            "outlet": outlet
        })
    print(all_articles)
    if len(all_articles) > 0:
        keys = all_articles[0].keys()
        outlet_csv_file_name = outlet + timestamp + '.csv'
        with open(outlet_csv_file_name, 'a+', encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(all_articles)
    else:
        print('No articles found for ' + url)


def scrape_abstract(article_url):
    print(article_url)
    r = requests.get(article_url)

    soup = BeautifulSoup(r.text, features='html.parser')

    abstract = soup.find(class_="c-article-section__content")
    if abstract is not None:
        abstract_strip = strip_html_element(abstract)
        return abstract_strip
    else:
        return ""


if __name__ == '__main__':
    start_scraping()
