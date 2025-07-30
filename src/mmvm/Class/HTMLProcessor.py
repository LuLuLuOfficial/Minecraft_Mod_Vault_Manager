from typing import Self
from lxml.html import HtmlElement, fromstring

class HTMLElements():
    def __init__(self, Elements: list[HtmlElement] | None):
        self.Elements: list[HtmlElement] | None = Elements

    def __len__(self) -> int:
        return len(self.Elements) if self.Elements is not None else 0

    def Get(self, Attribute: str) -> list[str]:
        return [Element.Get(Attribute) or '' for Element in self.Elements] if self.Elements is not None else ''

    @property
    def Text(self) -> list[str]:
        return [(Element.text or '') for Element in self.Elements] if self.Elements is not None else ''

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

def FormatHTML(HTMLText: str) -> Self:
    return HTMLElement(fromstring(HTMLText))

