#!/usr/bin/env python3.9

#####
# This script is to download papers from the arxiv.org
# for specific areads
#####

import os
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

g_to_folder = '/Users/fawuwu/Downloads'
g_arxiv_list_url = 'https://arxiv.org/list/'
g_arxiv_list_url_suffix = '/recent?skip=0&show=2000'
g_arxiv_paper_url_header = 'https://arxiv.org'
g_primary_domains = ['cs.CE', 'cs.DB', 'cs.DM', 'cs.DS', 'cs.DC', 'cs.PF', 'math.CO', 'q-fin.PM', 'q-fin.RM', 'stat.ML']
g_conditional_cs_domains = {'cs.AI': ['reason', 'causal', 'graph', 'tree', 'comb'],
                            'cs.LG': ['reason', 'causal', 'graph', 'tree', 'comb'],
                            'cs.CL': ['reason', 'causal', 'graph', 'tree', 'comb', 'memo'],
                            'cs.CV': ['reason', 'causal', 'graph', 'tree', 'comb'],
                            'math.ST': ['reason', 'causal', 'graph', 'tree', 'comb']}
g_links_to_download = {}

def get_title_and_link(domain, includes = []):
    url = g_arxiv_list_url + domain + g_arxiv_list_url_suffix
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    count = 0

    # Loop over all dt elements
    for dt in soup.find_all('dt'):
        title = None
        dd = dt.find_next_sibling('dd')
        if dd:
            # Extract Title
            title_div = dd.find('div', class_='list-title mathjax')
            if title_div:
                descriptor = title_div.find('span', class_='descriptor')
                if descriptor:
                    descriptor.decompose()
                    title = title_div.get_text(strip=True)
            else:
                print('None title')

        # Extract PDF link
        pdf_tag = dt.find('a', title='Download PDF')
        pdf_link = 'https://arxiv.org' + pdf_tag['href'] if pdf_tag else None

        if title and pdf_link:
            focus = True
            if len(includes) > 0:
                found = False
                for include in includes:
                    if include in title.lower():
                        found = True
                        break
                if not found:
                    focus = False
            if focus:
                g_links_to_download[title] = pdf_link
                count += 1

    print("Found {} papers".format(count))

def main():
    for domain in g_primary_domains:
        get_title_and_link(domain)

    for domain, includes in g_conditional_cs_domains.items():
        get_title_and_link(domain, includes)

    target_folder = g_to_folder + '/' + datetime.today().strftime('%Y%m%d')
    os.makedirs(target_folder, exist_ok=True)
    for title, link in g_links_to_download.items():
        title = title.strip().replace(':', '_').replace('/', '_')
        print('Download: file {}, url {}'.format(title, link))
        filename = os.path.join(target_folder, title + '.pdf')
        if os.path.exists(filename):
            print('Skipping ' + filename)
            continue
        response = requests.get(link)
        with open(filename, 'wb') as f:
            f.write(response.content)
        time.sleep(1)

if __name__ == '__main__':
    main()
