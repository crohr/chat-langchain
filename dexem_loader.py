"""Loader that loads ReadTheDocs documentation directory dump."""
from pathlib import Path
from typing import Any, List, Optional

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

from pprint import pprint

class DexemLoader(BaseLoader):
    """Loader that loads ReadTheDocs documentation directory dump."""

    def __init__(
        self,
        path: str,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        **kwargs: Optional[Any]
    ):
        """Initialize path."""
        try:
            from bs4 import BeautifulSoup

        except ImportError:
            raise ValueError(
                "Could not import python packages. "
                "Please install it with `pip install beautifulsoup4`. "
            )

        try:
            _ = BeautifulSoup(
                "<html><body>Parser builder library test.</body></html>", **kwargs
            )
        except Exception as e:
            raise ValueError("Parsing kwargs do not appear valid") from e

        self.file_path = path
        self.encoding = encoding
        self.errors = errors
        self.bs_kwargs = kwargs

    def load(self) -> List[Document]:
        """Load documents."""
        from bs4 import BeautifulSoup

        if ("/feed/" in self.file_path or "/author/" in self.file_path):
            print(self.file_path)
            print("ignore")
            return []

        with open(self.file_path, encoding=self.encoding, errors=self.errors) as f:
            try:
              soup = BeautifulSoup(f.read(), **self.bs_kwargs)
            except UnicodeDecodeError as e:
              print(e)
              return []

            # help.dexem.com
            text = soup.find_all("article")
            # dexem.com
            if len(text) == 0:
                text = soup.find_all(".content")

            if len(text) > 0:
                text = text[0].get_text()
                text = "\n".join([t for t in text.split("\n") if t])
                metadata = {"source": str(self.file_path), "title": str(soup.title.string).split(" |")[0]}
                return [Document(page_content=text, metadata=metadata)]
            else:
                return []