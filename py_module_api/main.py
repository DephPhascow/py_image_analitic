from dataclasses import dataclass
from io import BytesIO
import os
from typing import Dict, List
from enum import Enum
from PIL import Image, ImageFont
from PIL.ImageDraw import ImageDraw

import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


class ImageAnaliticsDataType(Enum):
    DATE_RANGE = 1
    DIAGRAM = 2
    
    
class ImageAnaliticsConfig:
    FONT_NAME: str
    BACKGROUND_IMAGE: str

    def __init__(self, font_name: str, background_image: str):
        self.FONT_NAME = font_name
        self.BACKGROUND_IMAGE = background_image
        if not os.path.exists(self.FONT_NAME):
            raise Exception('Font not found')
        if not os.path.exists(self.BACKGROUND_IMAGE):
            raise Exception('Background image not found')
    
@dataclass
class ImageAnaliticsDateRange:
    this_day: float
    this_week: float
    this_month: float
    all_time: float
    
@dataclass 
class ImageAnaliticsGraph:
    title: str
    x_label: str
    y_label: str
    dates: List[str]
    values: List[float]
    
class ImageAnaliticsColors:
    BACKGROUND = (75, 178, 240, 0)
    PANEL_BACKGROUND = (255, 255, 255, 255)
    INFO_COLOR = (51, 51, 255)
    TEXT_COLOR = (0, 0, 0)
    MAIN_TEXT_SIZE = 12
    TITLE_TEXT_SIZE = 16
    INFO_TEXT_SIZE = 17
    
class ImageAnaliticsData:
    title: str
    type: ImageAnaliticsDataType
    data: List[ImageAnaliticsDateRange] | ImageAnaliticsGraph
    image: str = None
    
    def __init__(self, title: str, type: ImageAnaliticsDataType, data: List[ImageAnaliticsDateRange] | ImageAnaliticsGraph, image: str = None):
        self.title = title
        self.type = type
        self.data = data
        self.image = image
        
    def gen(self, x: int, y: int, width: int, draw: ImageDraw, img: Image.Image, config: ImageAnaliticsConfig):
        if isinstance(self.data, ImageAnaliticsGraph):
            dates = [datetime.strptime(date, "%d.%m.%Y") for date in self.data.dates]
            plt.figure(figsize=(7.7, 4))
            plt.plot(dates, self.data.values, )
            plt.fill_between(dates, self.data.values, color='blue', alpha=0.1) 
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            plt.title(self.data.title, fontsize=10)  
            plt.xlabel(self.data.x_label, fontsize=10)             
            plt.ylabel(self.data.y_label, fontsize=10)           

            plt.grid(True)

            graph_bytes = BytesIO()
            plt.savefig(graph_bytes)
            graph_bytes.seek(0)
            graph_image = Image.open(graph_bytes, formats=['png'])
            img.paste(
                graph_image,
                (15, y - 100, )
            )
            plt.close()
            
        elif isinstance(self.data[0], ImageAnaliticsDateRange):
            panel = Image.new('RGBA', (int(img.width), int(img.height)), color = ImageAnaliticsColors.PANEL_BACKGROUND)
            rect = ImageDraw(panel)
            rect.rounded_rectangle((x, y, width + x - 1, 100 + y + 9), outline=(0, 0, 0), radius=10, fill=(255, 255, 255, 255))
            blended = Image.blend(img, panel, 0.5)
            blended = blended.crop((x, y, int(width + x), int(100 + y) + 10))
            img.paste(blended, (int(x), int(y)), blended)
            # out = Image.alpha_composite(img, panel)
            # # out = out.resize((int(width), 100))
            # img.paste(out, (int(x), int(y)))
            
            # draw.rounded_rectangle((x, y, width + x, 110 + y), radius=10, fill=ImageAnaliticsColors.PANEL_BACKGROUND)
            font = ImageFont.truetype(font=config.FONT_NAME, size=ImageAnaliticsColors.MAIN_TEXT_SIZE, encoding='utf-8')
            font_title = ImageFont.truetype(font=config.FONT_NAME, size=ImageAnaliticsColors.TITLE_TEXT_SIZE, encoding='utf-8')
            add_x = 5
            if self.image:
                with Image.open(self.image) as im:
                    im = im.resize((24, 24))
                    img.paste(im, (x + 5, y + 5)) 
                    add_x = 30
            draw.text((x + add_x, y + 5), self.title, font=font_title, fill=ImageAnaliticsColors.TEXT_COLOR)
            
            data_y = y + 30
            for item in self.data:
                data = [
                    item.this_day, item.this_week, item.this_month, item.all_time
                ]
                for index, text in enumerate([
                    "Сегодня: ", "Эта неделя: ", "Этот месяц: ", "Все время: "
                ]):
                    draw.text((x + 5, data_y), text, font=font, fill=ImageAnaliticsColors.TEXT_COLOR)
                    size = draw.textbbox((x + 5, data_y), text, font=font)
                    draw.text((x + 5 + (size[2] - size[0]),  data_y), f"{data[index]}", font=font, fill=(0, 0, 255, 255))
                    data_y += 20
                data_y += 80
    
class ImageAnaliticsColumnInfo:
    data: List[ImageAnaliticsData]
    
    def __init__(self, data: List[ImageAnaliticsData] = None):
        if not data:
            data = []
        self.data = data
        
    def gen(self, y: int, image_width: int, padding: int, draw: ImageDraw, img: Image, config: ImageAnaliticsConfig):
        if len(self.data) == 0:
            raise Exception('No data')
        if len(self.data) == 1:
            panel_width = 150
            self.data[0].gen( image_width / 2 - (panel_width / 2), y, panel_width, draw, img, config)
        else:
            width = image_width / len(self.data) - 20
            x = padding
            for column in self.data:
                column.gen(x, y, width, draw, img, config)
                x += width + padding * 2
        return y + 100 + padding

class ImageAnalitics:
    IMAGE_WIDTH: int
    IMAGE_HEIGHT: int
    PADDING: int = 10
    bot_username: str 
    config: ImageAnaliticsConfig
    __data: Dict[str, ImageAnaliticsColumnInfo]
    
    def __init__(self, image_width: int, image_height: int, bot_username: str, config: ImageAnaliticsConfig):
        self.IMAGE_WIDTH = image_width
        self.IMAGE_HEIGHT = image_height
        self.bot_username = bot_username
        self.config = config
        self.__data = {}
        
    def add_row(self, title: str, data: ImageAnaliticsColumnInfo = None):
        if not data:
            data = ImageAnaliticsColumnInfo()
        if title in self.__data:
            raise Exception('Title already exists')
        self.__data[title] = data
        
    def info_panel(self, x: int, y: int, width: int, draw: ImageDraw):
        draw.rounded_rectangle((x, y, width + x, 80 + y), radius=10, fill=ImageAnaliticsColors.PANEL_BACKGROUND)
        font = ImageFont.truetype(font=self.config.FONT_NAME, size=ImageAnaliticsColors.INFO_TEXT_SIZE, encoding='utf-8')
        date = datetime.now().strftime("%d.%m.%Y")
        text_parts = [f"Актуально {date} |", self.bot_username]
        colors = [ImageAnaliticsColors.TEXT_COLOR, ImageAnaliticsColors.INFO_COLOR]
        x_position = x + 35
        
        for part, color in zip(text_parts, colors):
            draw.text((x_position, y + 30), part, font=font, fill=color)
            x_position += x + 200
        
    def gen(self):
        background_image = Image.open(self.config.BACKGROUND_IMAGE)
        img = Image.new('RGBA', (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), color = ImageAnaliticsColors.PANEL_BACKGROUND)
        y = self.PADDING
        img.paste(background_image, (0, 0))
        
        for data in self.__data.values():
            y += data.gen(y, self.IMAGE_WIDTH, self.PADDING, ImageDraw(img), img, self.config)
        self.info_panel(self.PADDING, self.IMAGE_HEIGHT - self.PADDING - 80, self.IMAGE_WIDTH - (self.PADDING * 2), ImageDraw(img))
        img.show()

if __name__ == '__main__':
    dates = [
        "01.01.2024", "02.01.2024", "03.01.2024", "04.01.2024", "05.01.2024",
        "06.01.2024", "07.01.2024", "08.01.2024", "09.01.2024", "10.01.2024"
    ]
    img = ImageAnalitics(800, 800, '@DPhascow', ImageAnaliticsConfig('BOOKOS.TTF', 'background_image.png'))
    img.add_row('test', ImageAnaliticsColumnInfo([
        ImageAnaliticsData('Заказы', ImageAnaliticsDataType.DATE_RANGE, [
            ImageAnaliticsDateRange(
                this_day=3,
                this_week=6,
                this_month=9,
                all_time=12
            ), 
        ], 'icon.png'),
        ImageAnaliticsData('Количество', ImageAnaliticsDataType.DATE_RANGE, [
            ImageAnaliticsDateRange(
                this_day=3,
                this_week=6,
                this_month=9,
                all_time=12
            ), 
        ]),
        ImageAnaliticsData('Количество', ImageAnaliticsDataType.DATE_RANGE, [
            ImageAnaliticsDateRange(
                this_day=3,
                this_week=6,
                this_month=9,
                all_time=12
            ), 
        ]),
        ImageAnaliticsData('Количество', ImageAnaliticsDataType.DATE_RANGE, [
            ImageAnaliticsDateRange(
                this_day=3,
                this_week=6,
                this_month=9,
                all_time=12
            ), 
        ])                
    ]))

    img.add_row('звд', ImageAnaliticsColumnInfo([
        ImageAnaliticsData('Музыка', ImageAnaliticsDataType.DATE_RANGE, [
            ImageAnaliticsDateRange(
                this_day=3,
                this_week=6,
                this_month=9,
                all_time=12
            ), 
        ])
    ]))
    img.add_row('График', ImageAnaliticsColumnInfo([
        ImageAnaliticsData('График', ImageAnaliticsDataType.DIAGRAM, ImageAnaliticsGraph('График', 'Дата', 'Количество', dates, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    ]))
    img.gen()
