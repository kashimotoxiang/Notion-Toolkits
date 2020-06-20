import glob
import itertools
import multiprocessing
import os
import uuid
from io import BytesIO
from pathlib import Path

import boto3
import requests
from notion.client import NotionClient
from PIL import Image

# imgur
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


def convert_img(child_source):
    print(child_source)
    try:
        image_name = str(uuid.uuid4()) + ".png"
        image_path = Path("./tmp") / image_name
        response = requests.get(child_source)
        img = Image.open(BytesIO(response.content))
        img.save(image_path, "png")
        response = s3_client.upload_file(
            str(image_path),
            'kashimotoxiang-blog',
            image_name,
            ExtraArgs={'ContentType': 'image/png'})
    except:
        print("ERROR!!!!!!!!!!" + child_source)

    return "https://kashimotoxiang-blog.s3-us-west-1.amazonaws.com/" + image_name


def async_map(func, data, cpu=(multiprocessing.cpu_count() - 1)):
    with multiprocessing.Pool(processes=cpu) as pool:
        async_result = pool.map_async(func, data)
        pool.close()
        pool.join()
        results = async_result.get()
        return results


def foo(link):
    page = notionClient.get_block(link)
    image_block_list = []
    for child in page.children:
        if child._type == "image" and child.source.startswith(
                "http") and not child.source.startswith(
                    "https://kashimotoxiang-blog.s3-us-west-1.amazonaws.com/"
                ) and not child.source.endswith("gif"):
            image_block_list.append(child)
    return image_block_list


def get_all_links(export_path):
    links = [
        "https://www.notion.so/" + path.name.replace(' ', '-')[:-3]
        for path in Path(export_path).rglob('*.md')
    ]
    return links


if __name__ == "__main__":
    # get all image block
    links = get_all_links(
        "/Users/yuxiangli/Downloads/Export-b47f2118-cba9-4797-b656-04cf91486207"
    )
    for link in links:
        image_block_list = foo(link)
        # upload image to s3
        if image_block_list:
            image_source_list = [x.source for x in image_block_list if x]
            res = async_map(convert_img, image_source_list)
            # update notion
            for c, i in zip(image_block_list, res):
                c.source = i
