"""Base crawler interface. All source-specific crawlers inherit from this."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ScrapedProduct:
    name: str
    source: str
    source_url: str
    price: float | None = None
    currency: str = "INR"
    unit: str | None = None
    brand: str | None = None
    category: str | None = None
    image_url: str | None = None
    ingredients: str | None = None
    certifications: list[str] = field(default_factory=list)
    description: str | None = None
    rating: float | None = None
    review_count: int | None = None
    in_stock: bool | None = None
    raw_data: dict = field(default_factory=dict)


class BaseCrawler(ABC):
    """All crawlers must implement search() and get_product()."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 20) -> list[ScrapedProduct]:
        """Search for products by query string."""
        ...

    @abstractmethod
    async def get_product(self, url: str) -> ScrapedProduct | None:
        """Scrape full product details from a product page URL."""
        ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass
