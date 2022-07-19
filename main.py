import asyncio
import os
import time
import asyncio
import os
from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from surepy import Surepy
from surepy.entities import SurepyEntity
from surepy.entities.devices import SurepyDevice
from surepy.entities.pet import Pet
from dotenv import load_dotenv
from typing import Dict, List

ICON_SIZE = 100

TILE_WIDTH = 200
TILE_HEIGHT = 100

FONT_SIZE = 22
SPACE = 2

CAT_HOME_ICON_WIDTH = 186
CAT_HOME_ICON = "./icons/cat-home.PNG8"
CAT_HOME_TEXT = "CAT IS HOME"

CAT_AWAY_ICON_WIDTH = 167
CAT_AWAY_ICON = "./icons/cat-away.PNG8"
CAT_AWAY_TEXT = "CAT IS OUT HUNTING"


async def getCatLocation(cat_name):
    # # user/password authentication (gets a token in background)
    surepy = Surepy(email=os.environ['SUREPET_EMAIL'],
                    password=os.environ['SUREPET_PASSWORD'])

    # list with all pets
    pets: List[Pet] = await surepy.get_pets()
    for pet in pets:
        # find the cat we're looking for
        if pet.name == cat_name:
            return pet.location


def convert(img):  # 8 bit indexed color image (white, black, red)
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0))
    return img.convert("RGB").quantize(palette=pal_img)


def get_icon(name):
    return convert(Image.open(name))


async def main():
    old_cat_status = ""
    load_dotenv()

    while(True):
        # get cat location from SurePet APIs
        cat_status = str(await getCatLocation(os.environ['SUREPET_PETNAME']))
        # only update the display if the cats status has changed, otherwise you
        # get a flickering display (while it's updating) every 5 minutes
        if old_cat_status != cat_status:
            old_cat_status = cat_status

            # initialise the drawing components
            img = convert(Image.new("P", (400, 300), 255))
            draw = ImageDraw.Draw(img)
            inky_display = InkyWHAT("red")
            inky_display.set_border(inky_display.RED)

            font = ImageFont.truetype(
                "fonts/BungeeColor-Regular_colr_Windows.ttf", FONT_SIZE)

            cat_image = CAT_HOME_ICON
            cat_text = CAT_HOME_TEXT
            cat_image_width = CAT_HOME_ICON_WIDTH
            if cat_status == "Outside":
                cat_text = CAT_AWAY_TEXT
                cat_image = CAT_AWAY_ICON
                cat_image_width = CAT_AWAY_ICON_WIDTH

            icon = get_icon(cat_image)
            x = (TILE_WIDTH - ICON_SIZE)
            y = TILE_HEIGHT
            img.paste(icon, (x, y))

            w, h = font.getsize(cat_text)
            x = (TILE_WIDTH + cat_image_width / 2 - w)
            y = TILE_HEIGHT + ICON_SIZE + SPACE
            draw.text((x, y), cat_text, inky_display.BLACK, font)

            inky_display.set_image(img)
            inky_display.show()

        # update every 5 minutes
        time.sleep(300)

asyncio.run(main())
