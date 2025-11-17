from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Tuple, Union

class ImageTextOverlay:
    @staticmethod
    def add_text_to_image(
        image_path: str,
        text: str,
        font_path: str = "./fonts/Montserrat-ExtraBold.ttf",
        font_size: int = 96,
        text_color: Union[str, Tuple[int, int, int]] = "white",
        right_padding: int = 280,
        bottom_padding: int = 110,
        output_format: str = "PNG"
    ) -> BytesIO:
        """
        Накладывает текст на изображение и возвращает BytesIO буфер
        
        :param image_path: Путь к исходному изображению
        :param text: Текст для наложения
        :param font_path: Путь к файлу шрифта
        :param font_size: Размер шрифта
        :param text_color: Цвет текста (строка или RGB-кортеж)
        :param right_padding: Отступ от правого края
        :param bottom_padding: Отступ от нижнего края
        :param output_format: Формат выходного изображения (PNG/JPEG)
        :return: BytesIO буфер с изображением
        """
        # Открываем изображение
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype(font_path, size=font_size)
        except OSError:
            # Fallback на стандартный шрифт если указанный не найден
            font = ImageFont.load_default()
        
        # Получаем размеры изображения
        img_width, img_height = image.size

        # Определяем координаты ЦЕНТРА текста
        center_x = img_width - right_padding
        center_y = img_height - bottom_padding

        # Наносим текст, используя центральную привязку
        draw.text(
            (center_x, center_y),
            text,
            font=font,
            fill=text_color,
            anchor='mm'  # mm = middle-middle (центр текста)
        )
        
        # Сохраняем в буфер
        image_bytes = BytesIO()
        image.save(image_bytes, format=output_format)
        image_bytes.seek(0)
        
        return image_bytes