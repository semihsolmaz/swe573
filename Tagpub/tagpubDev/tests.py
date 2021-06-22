from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.postgres.search import SearchQuery
from django.urls import reverse
from tagpubDev.models import Article, Author, Journal, RegistrationApplication, Tag, Keyword


client = Client()
client.login(username="admin@tagpub.com", password="123456")


# models tests
class Test(TestCase):

    def create_author(self, LastName="Testsurname", ForeName="Testname", Initials="tt"):
        return Author.objects.create(LastName=LastName, ForeName=ForeName, Initials=Initials)

    def test_author_creation(self):
        author = self.create_author()
        self.assertTrue(isinstance(author, Author))
        control_author = Author.objects.filter(LastName="Testsurname").values()
        self.assertEqual(control_author[0].get('LastName'), author.LastName)

    def create_journal(self, ISSN="0304-4939", Title="Aegean medical journal",
                       ISOAbbreviation="Aegean medical journal"):
        return Journal.objects.create(ISSN=ISSN, Title=Title, ISOAbbreviation=ISOAbbreviation)

    def test_journal_creation(self):
        journal = self.create_journal()
        self.assertTrue(isinstance(journal, Journal))
        control_journal = Journal.objects.filter(ISSN="0304-4939").values()
        self.assertEqual(control_journal[0].get('Title'), journal.Title)

    def create_keyword(self, KeywordText="endocardium"):
        return Keyword.objects.create(KeywordText=KeywordText)

    def test_keyword_creation(self):
        keyword = self.create_keyword()
        self.assertTrue(isinstance(keyword, Keyword))
        control_keyword = Keyword.objects.filter(KeywordText="endocardium").values()
        self.assertEqual(control_keyword[0].get('KeywordText'), keyword.KeywordText)

    def create_registration(self,
                            name="test_applicant",
                            surname="test_applicant_surname",
                            email="test@ss.com",
                            applicationText="This is an application text for registration testing",
                            applicationStatus="1"
                            ):
        return RegistrationApplication.objects.create(name=name,
                                                      surname=surname,
                                                      email=email,
                                                      applicationText=applicationText,
                                                      applicationDate=timezone.now(),
                                                      applicationStatus=applicationStatus)

    def test_registration_creation(self):
        registration = self.create_registration()
        self.assertTrue(isinstance(registration, RegistrationApplication))
        control_registration = RegistrationApplication.objects.filter(email="test@ss.com").values()
        self.assertEqual(control_registration[0].get('applicationText'), registration.applicationText)

    def create_tag(self,
                   WikiID="Q1485",
                   Label="systemic lupus erythematosus",
                   Description="inflammation of connective tissue marked by skin rashes, "
                               "joint pain and swelling, inflammation of the kidneys and "
                               "inflammation of the tissue surrounding the heart.",
                   Tokens="designated intractable/rare diseases, SLE, rare disease, rheumatic disease"
                          "lupus erythematosus, connective tissue disease"
                   ):
        tag = Tag.objects.create(WikiID=WikiID, Label=Label, Description=Description, Tokens=Tokens)
        tag.createTSvector()

        return tag

    def test_tag_creation(self):
        tag = self.create_tag()
        self.assertTrue(isinstance(tag, Tag))
        control_tag = Tag.objects.filter(WikiID="Q1485").values()
        self.assertEqual(control_tag[0].get('Description'), tag.Description)
        # check if the tsvector created correctly
        self.assertTrue(Tag.objects.filter(SearchIndex=SearchQuery('rare disease', search_type='phrase')).exists())

    def create_article(self, **kwargs):
        abstract = 'Coronary artery disease (CAD) is the number one cause of death worldwide and involves the ' \
                   'accumulation of plaques within the artery wall that can occlude blood flow to the heart and ' \
                   'cause myocardial infarction. The high mortality associated with CAD makes the development of ' \
                   'medical interventions that repair and replace diseased arteries a high priority for the ' \
                   'cardiovascular research community. Advancements in arterial regenerative medicine could benefit ' \
                   'from a detailed understanding of coronary artery development during embryogenesis and of how these ' \
                   'pathways might be reignited during disease. Recent research has advanced our knowledge on how the ' \
                   'coronary vasculature is built and revealed unexpected features of progenitor cell deployment that ' \
                   'may have implications for organogenesis in general. Here, we highlight these recent findings and ' \
                   'discuss how they set the stage to interrogate developmental pathways during injury and disease.'
        article_data = {
            'PMID': '27959616',
            'Title': 'Coronary Artery Development: Progenitor Cells and Differentiation Pathways',
            'Abstract': abstract,
            'PublicationDate': timezone.now(),
            'Journal' : self.create_journal()
        }
        article = Article.objects.create(**article_data)
        article.Authors.add(self.create_author())
        article.Tags.add(self.create_tag())
        article.Keywords.add(self.create_keyword())

        article.createTSvector()

        return article

    def test_article_creation(self):
        article = self.create_article()
        self.assertTrue(isinstance(article, Article))
        control_article = Article.objects.filter(PMID="27959616").values()
        self.assertEqual(control_article[0].get('Abstract'), article.Abstract)
        # check if the tsvector created correctly
        self.assertTrue(Article.objects.filter(SearchIndex=SearchQuery('implications for organogenesis', search_type='phrase')).exists())
        # Check tagging
        self.assertTrue(Article.objects.filter(Tags__SearchIndex=SearchQuery('SLE', search_type='phrase')).exists())

    # view tests
    def test_registration_view(self):
        url = reverse("tagpubDev:registration")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        # self.assertIn(w.title, resp.content)

    def test_registrationRequests_view(self):
        reg_request = self.create_registration()
        url = reverse("tagpubDev:registrationRequests")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(reg_request.name, resp.content.decode('utf-8'))

    def test_login_view(self):
        url = reverse("tagpubDev:userLogin")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

    def test_articleDetail_view(self):
        article = self.create_article()
        url = reverse("tagpubDev:articleDetail", args=[1])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(article.Title, resp.content.decode('utf-8'))
