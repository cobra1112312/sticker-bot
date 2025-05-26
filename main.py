import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN
from PIL import Image
from moviepy.editor import VideoFileClip
from lottie import objects, exporters, parsers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

@dp.message_handler(content_types=types.ContentType.STICKER)
async def sticker_to_image(message: types.Message):
    file = await bot.get_file(message.sticker.file_id)
    file_path = file.file_path
    downloaded_file = await bot.download_file(file_path)

    base_name = os.path.join(DOWNLOAD_PATH, message.sticker.file_unique_id)
    input_path = ""
    output_path = ""

    if message.sticker.is_animated:
        input_path = base_name + ".tgs"
        with open(input_path, "wb") as f:
            f.write(downloaded_file.read())

        try:
            animation = parsers.tgs.parse_tgs(input_path)
            mp4_path = base_name + ".mp4"
            exporters.export_mp4(animation, mp4_path, resolution=512, framerate=30)
            await message.reply_video(video=types.InputFile(mp4_path), caption="هذا هو الفيديو المحول من الملصق المتحرك")
        except Exception as e:
            await message.reply(f"فشل تحويل الملصق المتحرك: {e}")
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(mp4_path): os.remove(mp4_path)
        return

    elif message.sticker.is_video:
        input_path = base_name + ".webm"
        with open(input_path, "wb") as f:
            f.write(downloaded_file.read())

        try:
            clip = VideoFileClip(input_path)
            frame = clip.get_frame(0.1)
            img = Image.fromarray(frame)
            output_path = base_name + ".png"
            img.save(output_path)
            await message.reply_photo(photo=types.InputFile(output_path), caption="أول فريم من الملصق الفيديو")
        except Exception as e:
            await message.reply(f"خطأ في تحويل الملصق الفيديو: {e}")
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)
        return

    else:
        input_path = base_name + ".webp"
        output_path = base_name + ".png"
        with open(input_path, "wb") as f:
            f.write(downloaded_file.read())

        try:
            img = Image.open(input_path).convert("RGB")
            img.save(output_path)
            await message.reply_photo(photo=types.InputFile(output_path), caption="تحويل الملصق إلى صورة")
        except Exception as e:
            await message.reply(f"فشل التحويل: {e}")
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
