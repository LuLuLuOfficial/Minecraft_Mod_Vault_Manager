from typing import Self
from lxml.html import HtmlElement, fromstring

class HTMLElement():
    def __init__(self, Element: HtmlElement | None):
        self.Element: HtmlElement | None = Element

    def Get(self, Attribute: str) -> str:
        return (self.Element.get(Attribute) or '') if self.Element is not None else ''

    @property
    def Text(self) -> str:
        return (self.Element.text or '') if self.Element is not None else ''

    def SubElement(self, XPATH: str) -> Self:
        Element: HtmlElement = self.Element.xpath(XPATH)
        if Element: return HTMLElement(Element[0])
        else: return HTMLElement(None)

    def SubElements(self, XPATH: str) -> list[Self]:
        Elements: list[HtmlElement] = self.Element.xpath(XPATH)
        if Elements: return [HTMLElement(Element) for Element in Elements]
        else: return []

def FormatHTML(HTMLText: str) -> HTMLElement:
    return HTMLElement(fromstring(HTMLText))

