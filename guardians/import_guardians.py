# import_guardians.py
# Loads a guardains.csv from assets/guardians.csv
# Resolves ENS names to addresses
# Downloads images, converts them to PNGs and resizes to 128x128, 256x256, 384x384 pixels
# Exports guardians data to data/guardians/guardians.json
# Exports guardian images to data/guardians/images/<address>_<1|2|3>x.png
#
# You must set the INFURA_PROJECT_ID environment variable with the correct Infura project ID.
# Otherwise, the ENS resolution won't work and script will fail.
#
# You must create a "guardians.sqlite" database with schema from "create_db.sql"

import csv
import io
import os
import sqlite3
import re
import sys

# for resolving ENS names
from web3 import Web3
from web3.providers import HTTPProvider
from ens import ENS

# for downloading images
import requests

# for getting image file extension based on file contents
import imghdr

# for svg - jpeg conversion
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# for image resizing and saving to PNGs
from PIL import Image
from PIL.Image import Resampling


from wand.api import library
import wand.color
import wand.image

import json

DB_FILE = 'intermediates/guardians.sqlite'
CSV_FILE = 'assets/guardians.csv'
IMAGE_DIR = 'assets/images'


def clean_guardians():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    cur.execute('''DELETE FROM guardians''')
    con.commit()
    con.close()


# guardians.csv columns
# 0 - typeform id
# 1 - name
# 2 - reason
# 3 - contribution
# 4 - ens/address
# 5 - profile picture url
# 6 - start date
# 7 - submit date
# 8 - network id
# 9 - tags
def import_guardians():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    # import data from csv
    with open(CSV_FILE, newline='') as csvfile:
        guardian_reader = csv.reader(csvfile)
        # skip header row
        next(guardian_reader)

        for row in guardian_reader:
            guardian_id, name, reason, contribution, ens, image_url, _, _, _, _ = row
            cur.execute('''
            INSERT OR REPLACE INTO guardians
            (id, name, reason, contribution, address_or_ens, image_url)
            VALUES
            (?, ?, ?, ?, ?, ?)''',
                        (guardian_id, name, reason, contribution, ens, image_url))
            con.commit()
    con.close()


def resolve_ens(ens):
    infura_project_id = os.environ.get('INFURA_PROJECT_ID')
    w3 = Web3(HTTPProvider(f"https://mainnet.infura.io/v3/{infura_project_id}"))
    ns = ENS.fromWeb3(w3)
    address = ns.address(ens)
    return address


def resolve_ens_names():
    address_re = re.compile('(0x[a-fA-F0-9]{40})')
    ens_re = re.compile(r"(\S+\.\S+)")

    con = sqlite3.connect(DB_FILE)
    cur_select = con.cursor()
    cur_update = con.cursor()
    for row in cur_select.execute("SELECT id, address_or_ens FROM guardians ORDER BY id"):
        address_m = address_re.search(row[1])
        address = address_m.group() if address_m else None

        ens_m = ens_re.search(row[1])
        ens = ens_m.group() if ens_m else None

        if ens and not address:
            print(f"resolving {row[0]}: {ens}")
            address = resolve_ens(ens)

        if not address:
            print(f"Guardian {id} does not have ens or address")
            con.close()
            sys.exit(2)

        cur_update.execute("UPDATE guardians SET address=?, ens=? WHERE id=?", (address, ens, row[0]))
        con.commit()
    con.close()


def download_images():
    con = sqlite3.connect(DB_FILE)
    cur_select = con.cursor()
    cur_update = con.cursor()
    for row in cur_select.execute("SELECT id, image_url FROM guardians ORDER BY id"):
        id, image_url = row

        if image_url:
            print(f"downloading {id}: {image_url}")
            img_r = requests.get(image_url)

            if img_r.ok:
                cur_update.execute("UPDATE guardians SET image_src=? WHERE id=?", (sqlite3.Binary(img_r.content), id))
        con.commit()
    con.close()


def substitute_images():
    con = sqlite3.connect(DB_FILE)
    cur_select = con.cursor()
    cur_update = con.cursor()

    directory = os.fsencode(IMAGE_DIR)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        guardian_name = os.path.splitext(filename)[0]

        for row in cur_select.execute("SELECT id FROM guardians WHERE name LIKE ? ORDER BY id LIMIT 1", [guardian_name]):
            id = row[0]
            print(id, guardian_name)
            with open(os.path.join(directory, file), mode='rb') as img_file:
                img_content = img_file.read()

                cur_update.execute("UPDATE guardians SET image_src=? WHERE id=?", (sqlite3.Binary(img_content), id))
                con.commit()


def svg_to_pil(svgbytes):

    buf = io.BytesIO(svgbytes)

    with wand.image.Image(blob=buf, format="svg", background=wand.color.Color('transparent')) as image:

        with image.convert('png') as converted:
            pil = Image.open(io.BytesIO(converted.make_blob()))
            return pil


def png_to_pil(pngbytes):
    return Image.open(io.BytesIO(pngbytes), formats=["PNG"])


def jpeg_to_pil(jpegbytes):
    return Image.open(io.BytesIO(jpegbytes), formats=["JPEG"])


def pil_to_png(pil, size):
    out = io.BytesIO()
    pil.thumbnail(size, Resampling.LANCZOS)
    pil.save(out, format="PNG")
    return out.getvalue()


def convert_images():
    con = sqlite3.connect(DB_FILE)
    cur_select = con.cursor()
    cur_update = con.cursor()

    for row in cur_select.execute("SELECT id, image_url, image_src FROM guardians ORDER BY id"):
        id, image_url, image_src = row
        if image_src:
            print(id)
            extension = imghdr.what(file=None, h=image_src)
            if not extension:
                extension = os.path.splitext(image_url)[1][1:]

            # Python Image Library object
            pil = None

            if extension == 'svg':
                pil = svg_to_pil(image_src)

            elif extension == 'png':
                pil = png_to_pil(image_src)

            elif extension == 'jpeg':
                pil = jpeg_to_pil(image_src)

            if pil:
                png_3x = pil_to_png(pil, (384, 384))
                png_2x = pil_to_png(pil, (256, 256))
                png_1x = pil_to_png(pil, (128, 128))
                cur_update.execute("UPDATE guardians SET image_1x=?, image_2x=?, image_3x=? WHERE id=?",
                                   (sqlite3.Binary(png_1x), sqlite3.Binary(png_2x), sqlite3.Binary(png_3x), id))
                con.commit()

    con.close()


def export_guardians_json():
    con = sqlite3.connect(DB_FILE)
    cur_select = con.cursor()
    guardians = []
    for row in cur_select.execute("SELECT name, address, ens, reason, contribution FROM guardians ORDER BY name"):
        name, address, ens, reason, contribution = row
        guardian = {
            "name": name,
            "address": address,
            "ens": ens,
            "image": f"{address}_3x.png",
            "reason": reason,
            "contribution": contribution
        }
        guardians.append(guardian)
    con.close()

    with open('../data/guardians/guardians.json', 'w', encoding='utf-8') as out_file:
        json.dump(guardians, out_file, ensure_ascii=False, indent=4)


def export_guardian_images():
    con = sqlite3.connect(DB_FILE)
    cur_select = con.cursor()
    for row in cur_select.execute("SELECT address, image_1x, image_2x, image_3x FROM guardians WHERE image_3x IS NOT NULL ORDER BY address"):
        address, image1, image2, image3 = row
        print(address)
        with open(f"data/guardians/images/{address}_1x.png", 'wb') as f1, open(
                f"data/guardians/images/{address}_2x.png", 'wb') as f2, open(
                f"data/guardians/images/{address}_3x.png", 'wb') as f3:
            f1.write(image1)
            f2.write(image2)
            f3.write(image3)
    con.close()


if __name__ == '__main__':
    clean_guardians()
    import_guardians()
    resolve_ens_names()
    download_images()
    substitute_images()
    convert_images()
    export_guardians_json()
    export_guardian_images()
