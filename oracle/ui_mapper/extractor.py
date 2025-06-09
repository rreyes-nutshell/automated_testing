
# ------------------------------
# extractor.py (entry point)
# ------------------------------

from oracle.ui_mapper.db_inserter import insert_crawl_session, insert_ui_path
from oracle.ui_mapper.nav_crawler import extract_nav_metadata
from oracle.ui_mapper.page_scanner import extract_page_contents

__all__ = [
	"insert_crawl_session",
	"insert_ui_path",
	"extract_nav_metadata",
	"extract_page_contents"
]
