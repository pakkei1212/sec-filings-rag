from bs4 import BeautifulSoup

from src.parser.table_parser import process_table
from src.parser.image_parser import process_images
from src.parser.text_parser import extract_text_from_dom

from src.embedding_manager_transformer import TransformerEmbeddingManager

from config import VISION_MODEL, EMBEDDING_MODEL_NAME, OLLAMA_HOST

def parse_html(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")

    tables_json = []

    # 1️⃣ Tables FIRST (DOM mutation)
    for table in soup.find_all("table"):
        process_table(table, tables_json)

    # 2️⃣ Images SECOND (DOM mutation)
    embedding_manager = TransformerEmbeddingManager(embedding_model=EMBEDDING_MODEL_NAME,
                                                  vision_model=VISION_MODEL,
                                                  base_url=OLLAMA_HOST)

    images = process_images(
        soup=soup,
        base_url=base_url,
        embedding_manager=embedding_manager,
    )

    # 3️⃣ Text LAST (sees flattened tables)
    text = extract_text_from_dom(soup)

    return text, tables_json, images
