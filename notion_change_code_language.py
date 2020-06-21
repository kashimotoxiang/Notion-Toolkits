import os

from notion.client import NotionClient

notion_note_links = "https://www.notion.so/GO-358587a971f14e36b961cb4629d842cc"
code_languages = "Go"
# notion
notion_token_v2 = os.getenv("notion_token_v2")
notion_client = NotionClient(token_v2=notion_token_v2)


def change_block_language(link):
    page = notion_client.get_block(link)
    for child in page.children:
        if child._type == "code":
            child.language = code_languages


change_block_language(notion_note_links)
