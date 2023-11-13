import argparse
import sys
import os
from PyPaperBot.Paper import Paper
from PyPaperBot.PapersFilters import filterJurnals, filter_min_date, similarStrings
from PyPaperBot.Downloader import downloadPapers
from PyPaperBot.Scholar import ScholarPapersInfo
from PyPaperBot.Crossref import getPapersInfoFromDOIs
from PyPaperBot.proxy_n import proxy
from halo import Halo

def start(query, scholar_results, scholar_pages, dwn_dir, proxy = proxy, min_date=None, num_limit=None, num_limit_type=None, filter_jurnal_file=None, restrict=None, DOIs=None, SciHub_URL=None):
    spinner = Halo(text='Downloading papers ...', spinner='dots')
    to_download = []
    if DOIs is None:
        print("Query: {}".format(query))
        to_download = ScholarPapersInfo(query, scholar_pages, restrict, min_date, scholar_results, spinner)
    else:
        print("Downloading papers from DOIs\n")
        num = 1
        i = 0
        while i < len(DOIs):
            DOI = DOIs[i]
            print("Searching paper {} of {} with DOI {}".format(num, len(DOIs), DOI))
            papersInfo = getPapersInfoFromDOIs(DOI, restrict)
            to_download.append(papersInfo)

            num += 1
            i += 1

    if restrict != 0 and to_download:
        if filter_jurnal_file is not None:
            to_download = filterJurnals(to_download, filter_jurnal_file)

        if min_date is not None:
            to_download = filter_min_date(to_download, min_date)

        if num_limit_type is not None and num_limit_type == 0:
            to_download.sort(key=lambda x: int(x.year) if x.year is not None else 0, reverse=True)

        if num_limit_type is not None and num_limit_type == 1:
            to_download.sort(key=lambda x: int(x.cites_num) if x.cites_num is not None else 0, reverse=True)

        downloadPapers(to_download, dwn_dir, num_limit, SciHub_URL, spinner)

    Paper.generateReport(to_download, dwn_dir + "result.csv")
    Paper.generateBibtex(to_download, dwn_dir + "bibtex.bib")

def download(query, results_per_page = 10, min_date = 2018, scholar_pages = '1-2'):
    pchain = []
    proxy(pchain)
    
    dwn_dir = 'papers'
    
    dwn_dir = dwn_dir.replace('\\', '/')
    if dwn_dir[-1] != '/':
        dwn_dir += "/"
    
    try:
        split = scholar_pages.split('-')
        if len(split) == 1:
            scholar_pages = range(1, int(split[0]) + 1)
        elif len(split) == 2:
            start_page, end_page = [int(x) for x in split]
            scholar_pages = range(start_page, end_page + 1)
        else:
            raise ValueError
    except Exception:
        print(
            r"Error: Invalid format for --scholar-pages option. Expected: %d or %d-%d, got: " + scholar_pages)
        sys.exit()

    start(query, scholar_pages=scholar_pages, restrict=1, proxy=proxy, scholar_results=results_per_page, min_date=min_date, dwn_dir=dwn_dir)
    
if __name__ == "__main__":
        
    query = ' "subword tokenizers" OR "subword tokenization" OR "subword segmentation" OR "subword-based tokenization" OR "morphological segmentation of words" OR "subword level tokenization"'
    query = '"access control" AND "machine learning"'
    download(query, results_per_page = 1, min_date = 2023, scholar_pages = '1-2')