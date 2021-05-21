from wikidata.client import Client
import requests
import json

# cli = Client()
# tag = cli.get('Q1073', load=True,)

# print(tag.label)
# print(tag.description)
# print(tag.data.keys())
# print(tag.data.get('claims').get('P279')[0])
# print(tag.data.get('claims').get('P31')[0].get('mainsnak').get('datavalue').get('value').get('id'))


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

