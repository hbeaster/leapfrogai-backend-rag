import os
import tempfile
import uuid
from typing import List

from langchain.docstore.document import Document
from langchain_community.document_loaders import (CSVLoader, Docx2txtLoader,
                                                  UnstructuredFileLoader,
                                                  UnstructuredHTMLLoader,
                                                  UnstructuredMarkdownLoader,
                                                  UnstructuredPowerPointLoader)
from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import PyPDFLoader


# Chroma

def load_file(file_path) -> List[Document]:
    _, file_extension = os.path.splitext(file_path)
    data: List[Document]
    if file_extension.lower() == '.html':
        loader = UnstructuredHTMLLoader(file_path)
        return loader.load()
    elif file_extension.lower() == '.pdf':
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif file_extension.lower() == '.md':
        loader = UnstructuredMarkdownLoader(file_path)
        return loader.load()
    elif file_extension.lower() == '.csv':
        loader = CSVLoader(file_path)
        return loader.load()
    elif file_extension.lower() == '.pptx':
        loader = UnstructuredPowerPointLoader(file_path)
        return loader.load()
    elif file_extension.lower() == '.docx':
        loader = Docx2txtLoader(file_path)
        return loader.load()
    else:
        # Perform action for other files or skip
        return UnstructuredFileLoader(file_path).load()


def update_metadata(file_name: str, doc_uuid: str, metadata: dict) -> dict:
    metadata['source'] = file_name
    metadata['uuid'] = doc_uuid
    return metadata


def get_uuids_for_document_texts(texts: list[Document]) -> list[str]:
    return [str(uuid.uuid4()) for idx in enumerate(texts)]


class Ingest:
    def __init__(self, collection, chunk_size: int, chunk_overlap: int):
        self.collection = collection
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_name: str, file_path: str) -> None:
        # disallowed_special is set so that technical documents that contain special tokens can be loaded
        text_splitter = TokenTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap,
                                          disallowed_special=())
        try:
            data: list[Document] = load_file(file_path=file_path)
            texts: list[Document] = text_splitter.split_documents(data)
            contents: list[str] = [d.page_content for d in texts]
            doc_uuid: str = str(uuid.uuid4())
            all_metadata: list[dict] = [update_metadata(file_name, doc_uuid, d.metadata) for d in texts]
            ids: list[str] = get_uuids_for_document_texts(texts)
            self.collection.add(documents=contents, metadatas=all_metadata, ids=ids)
            # split and load into vector db
            print(f"Found {len(data)} parts in file {file_path}")
        except Exception as e:
            print(f"process_file: Error parsing file {file_path}.  {e}")

    def load_file_bytes(self, file_bytes: bytes, file_name: str) -> None:
        _, file_extension = os.path.splitext(file_name)
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, prefix=file_name) as fp:
            fp.write(file_bytes)
            fp.close()
            self.process_file(file_name, fp.name)