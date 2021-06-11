from tagpubDev.models import Article
from functools import reduce
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Sum, Q


class SearchResult:
    """
    Gets search terms as a list and return search results as a query set
    """

    def __init__(self, search_terms):
        self.search_terms = search_terms

    def getSearchResults(self):
        search_queries = [SearchQuery(term, search_type='phrase') for term in self.search_terms]
        article_search_query = reduce(lambda x, y: x & y, search_queries)
        # todo: Change tag search logic to search for each term and get intersection results
        tag_search_query = reduce(lambda x, y: x | y, search_queries)

        results_list = Article.objects.\
            filter(Q(SearchIndex=article_search_query) | Q(Tags__SearchIndex=tag_search_query)).\
            values('id', 'PMID', 'Title', 'PublicationDate').\
            annotate(a_rank=SearchRank(F('SearchIndex'), article_search_query)).\
            annotate(t_rank=SearchRank(F('Tags__SearchIndex'), tag_search_query)).\
            annotate(rank=(F('a_rank') + F('t_rank'))).values('id', 'Title', 'PublicationDate').\
            annotate(a_rank=Sum('a_rank'), t_rank=Sum('t_rank'), rank=Sum('rank')).\
            order_by(F('rank').desc(nulls_last=True), F('t_rank').desc(nulls_last=True), F('a_rank').desc(nulls_last=True))

        return results_list

