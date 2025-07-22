from requests import get, post, put, delete
from requests.models import Response
from lxml.html import HtmlElement, fromstring

SearchTerm: str = 'Carpet'

url: str = f'https://search.mcmod.cn/s?key={SearchTerm}&site=&filter=1&mold=0'
zResponse: Response = get(url)
zResponse.raise_for_status()

ModSearshResultList: list[HtmlElement] = fromstring(zResponse.text).xpath('*//div[@class="search-result-list"]/div[@class="result-item"]')
if not ModSearshResultList: raise ValueError('No search results found.')

for ModElement in ModSearshResultList:
    ModURL: list[HtmlElement] = ModElement.xpath('./div[@class="head"]/a[@target="_blank"]/@href')
    ModName: list[HtmlElement] = ModElement.xpath('./div[@class="head"]/a[@target="_blank"]')
    ModDescription: list[HtmlElement] = ModElement.xpath('./div[@class="body"]')
    if not all((ModURL, ModName, ModDescription)): continue
    print()
    print(ModURL)
    print(ModName[0].text_content().strip())
    print(ModDescription[0].text_content().strip())   