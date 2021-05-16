from Bio import Entrez
import xmltodict
from tagpubDev.articleManager import ArticleInfo
from tagpubDev.models import Journal, Author, Article, Keyword
from background_task import background


# @background(schedule=10)
def createArticles():
    Entrez.api_key = '2ed33cae73fa40c55df3b96dc4e7f6598209'
    Entrez.email = "semihsolmaz@hotmail.com"

    search_handle = Entrez.esearch(db="pubmed", term="flu", retmax=100)
    record = Entrez.read(search_handle)
    search_handle.close()
    id_list = record["IdList"]

    article_handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml", rettype="abstract")
    articles_xml = article_handle.read()
    articles = xmltodict.parse(articles_xml)
    articles_list = articles.get('PubmedArticleSet').get('PubmedArticle')
    article_handle.close()

    for item in articles_list:

        article_info = ArticleInfo(item)

        if article_info.getJournal():
            journal = Journal.objects.get_or_create(**article_info.getJournal())[0]
        else:
            journal = None

        keywords_list = []
        if article_info.getKeywords():
            for element in article_info.getKeywords():
                keyword = Keyword.objects.get_or_create(KeywordText=element)
                keywords_list.append(keyword[0])

        author_list = []
        for record in article_info.getAuthors():
            author = Author.objects.get_or_create(**record)
            author_list.append(author[0])

        article = Article(
            PMID=article_info.getPMID(),
            Title=article_info.getTitle(),
            Abstract=article_info.getAbstract(),
            PublicationDate=article_info.getPublicationDate(),
            Journal=journal,
            Tokens=article_info.getTokens()
        )

        article.save()

        article.createTSvector()

        if author_list:
            article.Authors.add(*author_list)

        article.Keywords.add(*keywords_list)

