from utils.image import ImageTextOverlay
from aiogram.types import BufferedInputFile

class ImageService:
    
    classmethod
    async def generate_offer(label: str, path: str) -> BufferedInputFile:
        buffer = ImageTextOverlay.add_text_to_image(
            f"{path}",
            label,
            "./fonts/Montserrat-ExtraBold.ttf",
            64,
            "white"
        )

        return BufferedInputFile(buffer.read(), filename="any.jpg")