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

notion_export_dir = "/Users/yuxiangli/Downloads/Export-b47f2118-cba9-4797-b656-04cf91486207"
notion_token_v2 = os.getenv("notion_token_v2")
writepath = Path("./tmp")
aws_url_prefix = "https://kashimotoxiang-blog.s3-us-west-1.amazonaws.com/"
aws_bucket_name = 'kashimotoxiang-blog'
# imgur
if not os.path.exists(writepath):
    os.makedirs(writepath)

# imgur
s3_client = boto3.client('s3')
# notion
notion_client = NotionClient(token_v2=notion_token_v2)


def convert_img(child_source):
    print(child_source)
    try:
        image_name = str(uuid.uuid4()) + ".png"
        image_path = writepath / image_name
        response = requests.get(child_source)
        img = Image.open(BytesIO(response.content))
        img.save(image_path, "png")
        response = s3_client.upload_file(
            str(image_path),
            aws_bucket_name,
            image_name,
            ExtraArgs={'ContentType': 'image/png'})
    except:
        print("ERROR!!!!!!!!!!" + child_source)

    return aws_url_prefix + image_name


def async_map(func, data, cpu=(multiprocessing.cpu_count() - 1)):
    with multiprocessing.Pool(processes=cpu) as pool:
        async_result = pool.map_async(func, data)
        pool.close()
        pool.join()
        results = async_result.get()
        return results


def get_image_blocks(link):
    page = notion_client.get_block(link)
    image_block_list = []
    for child in page.children:
        if child._type == "image" and child.source.startswith(
                "http") and not child.source.startswith(
                    aws_url_prefix) and not child.source.endswith("gif"):
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
    links = get_all_links(notion_export_dir)
    for link in links:
        image_block_list = get_image_blocks(link)
        # upload image to s3
        if image_block_list:
            image_source_list = [x.source for x in image_block_list if x]
            res = async_map(convert_img, image_source_list)
            # update notion
            for c, i in zip(image_block_list, res):
                c.source = i
