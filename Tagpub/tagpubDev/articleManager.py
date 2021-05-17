from datetime import datetime
from collections.abc import Mapping
from Bio import Entrez
import xmltodict


class ArticleInfo:

    def __init__(self, article_dict):
        self.article_dict = article_dict

    def getJournal(self):
        journal_info = self.article_dict.get('MedlineCitation').get('Article').get('Journal')
        if journal_info.get('ISSN'):
            journal_dict = {
                'ISSN': journal_info.get('ISSN').get('#text'),
                'Title': journal_info.get('Title'),
                'ISOAbbreviation': journal_info.get('ISOAbbreviation')
                }
            return journal_dict
        else:
            return None

    def getPublicationDate(self):
        journal_info = self.article_dict.get('MedlineCitation').get('Article').get('Journal')
        if journal_info.get('JournalIssue').get('PubDate').get('Day') and journal_info.get('JournalIssue').get('PubDate').get('Month') and journal_info.get('JournalIssue').get('PubDate').get('Year'):
            date_str = journal_info.get('JournalIssue').get('PubDate').get('Year') + '-' + \
                       journal_info.get('JournalIssue').get('PubDate').get('Month') + '-' + \
                       journal_info.get('JournalIssue').get('PubDate').get('Day')
            for fmt in ('%Y-%b-%d', '%Y-%m-%d'):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')

        elif journal_info.get('JournalIssue').get('PubDate').get('Year') and journal_info.get('JournalIssue').get('PubDate').get('Month'):
            date_str = journal_info.get('JournalIssue').get('PubDate').get('Year') + '-' + \
                       journal_info.get('JournalIssue').get('PubDate').get('Month')
            for fmt in ('%Y-%b', '%Y-%m'):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')
        elif journal_info.get('JournalIssue').get('PubDate').get('Year'):
            pub_date = journal_info.get('JournalIssue').get('PubDate').get('Year')
            return datetime.strptime(pub_date, '%Y')
        else:
            return None

    def getAbstract(self):
        abstract_dict = self.article_dict.get('MedlineCitation').get('Article').get('Abstract')
        if abstract_dict:
            abstract_info = abstract_dict.get('AbstractText')
            if type(abstract_info) is str:
                return abstract_info
            elif type(abstract_info) is list:
                abstract_text = ''
                for item in abstract_info:
                    if type(item) is str:
                        abstract_text += item + '\n'
                    else:
                        abstract_text += item.get('@Label') + '\n' + item.get('#text') + '\n'
                return abstract_text
            else:
                return abstract_info['#text']
        else:
            return None

    def getTitle(self):
        title = self.article_dict.get('MedlineCitation').get('Article').get('ArticleTitle')
        return title

    def getAuthors(self):
        authors_list = self.article_dict.get('MedlineCitation').get('Article').get('AuthorList')
        authors_dict_list = []
        if authors_list:
            for author in authors_list.get('Author'):
                try:
                    if author.get('LastName') and author.get('Initials'):
                        author_dict = {
                            'LastName': author.get('LastName'),
                            'ForeName': author.get('ForeName'),
                            'Initials': author.get('Initials')
                        }
                        authors_dict_list.append(author_dict)
                except AttributeError:
                    print('No author info')
                    pass
        return authors_dict_list

    def getKeywords(self):
        keywords_data = self.article_dict.get('MedlineCitation').get('KeywordList')
        keywords = []
        if keywords_data:
            for keyword in keywords_data.get('Keyword'):
                keywords.append(keyword.get('#text'))
        else:
            keywords = None
        return keywords

    def getPMID(self):
        pmid = self.article_dict.get('MedlineCitation').get('PMID').get('#text')
        return pmid

    def getTokens(self):
        clean_dict = self.article_dict.get('MedlineCitation')
        clean_dict.pop('PMID', None)
        clean_dict.pop('KeywordList', None)
        clean_dict.get('Article').pop('ArticleTitle', None)
        clean_dict.get('Article').pop('Abstract', None)
        # clean_dict.get('Article').pop('Journal', None)
        tokens = []

        def iterateArticleData(value):
            if isinstance(value, Mapping):
                for element in value.values():
                    iterateArticleData(element)
            elif type(value) is list:
                for element in value:
                    iterateArticleData(element)
            elif type(value) is str:
                tokens.append(value)

        iterateArticleData(clean_dict)
        return ' '.join(tokens)

    # todo: Get references of the article
    # def getReferences(self):
    # https: // eutils.ncbi.nlm.nih.gov / entrez / eutils / elink.fcgi?dbfrom = pmc & linkname = pmc_refs_pubmed & id = 4423606

    # todo: Get how many times article is cited etc.
    # def getArticleMetrics:
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id=21876726&id=21876761

# Entrez.api_key = '2ed33cae73fa40c55df3b96dc4e7f6598209'
# Entrez.email = "semihsolmaz@hotmail.com"
#
# search_handle = Entrez.esearch(db="pubmed", term="flu", retmax=15)
# record = Entrez.read(search_handle)
# search_handle.close()
# id_list = record["IdList"]
#
# article_handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml", rettype="abstract")
# articles_xml = article_handle.read()
# articles = xmltodict.parse(articles_xml)
# articles_list = articles.get('PubmedArticleSet').get('PubmedArticle')
# article_handle.close()
#
# art = ArticleInfo(articles_list[0])
# print(art.getKeywords())



