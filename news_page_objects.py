import bs4
import requests
from common import config

class NewsPage:
    def __init__(self, news_site_uid):
        self._config = config()["news_sites"][news_site_uid] # trae el archivo config de coomon qye a su vez etsa con config .yaml
        self._queries = self._config["queries"] #le da al metodo privado (_queries) las queries que estan en confing de la linea de arriba
        self._html = None
        self._visit(self._config['url'])
        
    def _select(self, query_string):
        nodes = self._html.select(query_string)

        if not nodes:
            return None

        return nodes

    def _visit(self, url):
        response = requests.get(url) #obtiene la URL que se selecciono en un GET y la guarda en la varibale response

        response.raise_for_status() # metodo que sale error si la solicitud no es enviada correctamente.
        self._html = bs4.BeautifulSoup(response.text, "html.parser") # importa el texto de la variable response parseada con bs4  a el metodo _html

class HomePage(NewsPage):    # clase de pagina principal
    def __init__(self, news_site_uid):
        super().__init__(news_site_uid)
        
    @property #def dentro de un def
    def article_links(self):
        link_list=[] # crea una lista vacia
        for link in self._select(self._queries["homepage_article_links"]): #itera en los queries que estan con atributo CSS definido en confing.yaml los guarda en la variable link
            if link and link.has_attr("href"): #si la vairble link tiene el atributo href entonces la agrega a la lista que tenemos vacia y que creamos
               link_list.append(link)

        return set(link ["href"] for link in link_list) #hace un set (es decir quita los duplicados) queremos la propiedad href por cada link en la lista de links


class ArticlePage(NewsPage):

    def __init__(self, news_site_uid):
        super().__init__(news_site_uid)
    
    @property
    def body(self):
        result = self._select(self._queries['article_body'])
        return result[0].text if len(result) else ''

        
    @property
    def title(self):
        result = self._select(self._queries['article_title'])
        return result[0].text if len(result) else ''