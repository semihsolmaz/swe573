# from wikidata.client import Client
import requests
# import json

# cli = Client()
# tag = cli.get('Q1073', load=True,)
# tag = requests.get('https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q155&languages=en&format=json')
# tag_dict = tag.json()


class WikiEntry:
    """
    WikiEntry class to generate Tag model data from wikidata JSON reponse
    Uses wiki id with Q prefix to fetch entry data
    """
    def __init__(self, wikiID):
        tag = requests.get('https://www.wikidata.org/w/api.php?action=wbgetentities&ids=' + wikiID + '&languages=en&format=json')
        tag_dict = tag.json().get('entities').get(wikiID)
        self.entry_data = tag_dict

    def getID(self):
        return self.entry_data.get('id')

    def getLabel(self):
        return self.entry_data.get('labels').get('en').get('value')

    def getDescription(self):
        if self.entry_data.get('descriptions'):
            return self.entry_data.get('descriptions').get('en').get('value')
        else:
            return None

    def getTokens(self):
        token_list = []
        if self.entry_data.get('aliases'):
            for alias in self.entry_data.get('aliases').get('en'):
                token_list.append(alias.get('value'))

        if self.entry_data.get('claims'):
            # fetching subclass data
            if self.entry_data.get('claims').get('P279'):
                for subclass in self.entry_data.get('claims').get('P279'):
                    subclass_id = subclass.get('mainsnak').get('datavalue').get('value').get('id')
                    entry = WikiEntry(subclass_id)
                    token_list.append(entry.getLabel())
            # fetching instance of data
            if self.entry_data.get('claims').get('P31'):
                for instance in self.entry_data.get('claims').get('P31'):
                    instance_id = instance.get('mainsnak').get('datavalue').get('value').get('id')
                    entry = WikiEntry(instance_id)
                    token_list.append(entry.getLabel())
            # fetching studied by data
            if self.entry_data.get('claims').get('P2579'):
                for studied_by in self.entry_data.get('claims').get('P2579'):
                    studied_by_id = studied_by.get('mainsnak').get('datavalue').get('value').get('id')
                    entry = WikiEntry(studied_by_id)
                    token_list.append(entry.getLabel())

            if self.entry_data.get('claims').get('P361'):
                for part_of in self.entry_data.get('claims').get('P361'):
                    part_of_id = part_of.get('mainsnak').get('datavalue').get('value').get('id')
                    entry = WikiEntry(part_of_id)
                    token_list.append(entry.getLabel())

        return ', '.join(token_list)


def getLabelSuggestion(term):
    wiki_set = requests.get('https://www.wikidata.org/w/api.php?action=wbsearchentities&search='
                            + term
                            + '&format=json&language=en&type=item&continue=0')

    suggestions = []
    if wiki_set.json().get('search'):
        for wikipage in wiki_set.json().get('search'):
            page = [wikipage.get('id'),
                    wikipage.get('id') + ': ' + wikipage.get('label') + ' - ' + wikipage.get('description')
                    ]
            suggestions.append(page)

    return suggestions

# entry = WikiEntry('Q1073')
# print(entry.getID())
# print(entry.getLabel())
# print(entry.getDescription())
# print(entry.getTokens())
