import multiprocessing
import os
import uuid
from io import BytesIO
from pathlib import Path
from time import sleep

import boto3
import requests
import wget
from notion.client import NotionClient
from PIL import Image

# imgur
album = "swsX3RB"
client_id = 'b142535f88ce193'
client_secret = 'd651ce00c676c4253171292749a646244b5e9e63'
_access_token = '6f5ad22455b0aa542ad5c19312dd799edbe7f455'
_refresh_token = '79d6ad7b7eb54d573ffc9ee60eb87a412dc5d42b'
writepath = Path("./tmp")
if not os.path.exists(writepath):
    os.makedirs(writepath)

# imgur
s3_client = boto3.client('s3')

# notion
notionClient = NotionClient(
    token_v2=
    "21f65b444c4f98428e9f1c06031c7f0c5ec27a4a88cb9bddc5fdae2f39ab87690b1b5e60dca8817d15ddd9939573833e4b1c3ab74d5f47bc1f204a570393602245233d4c1b8bb1f098966bf86063"
)

metadata = {'Metadata': {'Content-Type': 'image/png'}}


def convert_img(child_source):
    image_name = str(uuid.uuid4()) + ".png"
    image_path = Path("./tmp") / image_name
    response = requests.get(child_source)
    img = Image.open(BytesIO(response.content))
    img.save(image_path, "png")
    response = s3_client.upload_file(str(image_path),
                                     'kashimotoxiang-blog',
                                     image_name,
                                     ExtraArgs=metadata)
    return "https://kashimotoxiang-blog.s3-us-west-1.amazonaws.com/" + image_name


def async_map(func, data, cpu=(multiprocessing.cpu_count() - 1)):
    with multiprocessing.Pool(processes=cpu) as pool:
        async_result = pool.map_async(func, data)
        pool.close()
        pool.join()
        results = async_result.get()
        return results


image_block_list = []


def foo(page):
    for child in page.children:
        if child._type == "image" and child.source.startswith("http"):
            image_block_list.append(child)
        elif child._type == "page":
            foo(child)


if __name__ == "__main__":
    # Replace this URL with the URL of the page you want to edit
    page = notionClient.get_block(
        "https://www.notion.so/Reading-List-fe75079b4869419fb66254e58d34a2d4")
    foo(page)

    image_source_list = [x.source for x in image_block_list][:5]
    res = async_map(convert_img, image_source_list)
    # convert_img(image_source_list[0])
    for c, i in zip(image_block_list, res):
        c.source = i
