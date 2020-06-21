import os

from notion.client import NotionClient

notion_note_links = "https://www.notion.so/CSAPP-_-76a60ac12ec44ad290ba961772b96586"
code_languages = "C"
# notion
notion_token_v2 = os.getenv("notion_token_v2")
notion_client = NotionClient(token_v2=notion_token_v2)


def change_block_language(link):
    page = notion_client.get_block(link)
    for child in page.children:
        if child._type == "code":
            child.language = code_languages


change_block_language(notion_note_links)
