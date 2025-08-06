from typing import Self
from lxml.html import fromstring as _fromstring_
from lxml.html import HtmlElement as _HtmlElement_

class HTMLElement():
    def __init__(self, Element: _HtmlElement_ | None):
        self.Element: _HtmlElement_ | None = Element

    def Get(self, Attribute: str) -> str:
        return (self.Element.get(Attribute) or '') if self.Element is not None else ''

    @property
    def Text(self) -> str:
        return (self.Element.text or '') if self.Element is not None else ''

    def SubElement(self, XPATH: str) -> Self:
        Element: _HtmlElement_ = self.Element.xpath(XPATH)
        if Element: return HTMLElement(Element[0])
        else: return HTMLElement(None)

    def SubElements(self, XPATH: str) -> list[Self]:
        Elements: list[_HtmlElement_] = self.Element.xpath(XPATH)
        if Elements: return [HTMLElement(Element) for Element in Elements]
        else: return []

def FormatHTML(HTMLText: str) -> HTMLElement:
    return HTMLElement(_fromstring_(HTMLText))

