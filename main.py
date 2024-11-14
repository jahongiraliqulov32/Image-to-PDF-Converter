import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from PIL import Image
from pdf2image import convert_from_path
# back button
back = KeyboardButton("Orqaga")
# Image to PDF
img_to_pdf= KeyboardButton("Image to PDF")
download_pdf = KeyboardButton("PDF Faylni Yuklash")
pdf = ReplyKeyboardMarkup(resize_keyboard=True)
pdf.add(download_pdf)
pdf.add(back)
# PDF to Image
pdf_to_img = KeyboardButton("PDF to Image")
get_pdf_to_image = KeyboardButton("Rasmlarni yuklab olish")
image = ReplyKeyboardMarkup(resize_keyboard=True)
image.add(get_pdf_to_image)
image.add(back)
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(img_to_pdf)
menu.add(pdf_to_img)

# Bot setup
API_TOKEN = '7878470879:AAEJLlxuLHFWvje1Pq3G1yuveAxLTwRYnJM'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Temp folder to store downloaded images
os.makedirs("images", exist_ok=True)
image_paths = []

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Assalomun alaykum. Quydagilardan birini tanlang 👇", reply_markup=menu)

@dp.message_handler(lambda message: message.text == "Image to PDF")
async def ask_for_images(message: types.Message):
    await message.reply("Rasmni PDF-ga aylantirish uchun rasm yuboring. Barcha rasmlarni yuborganingizdan keyin "
                        "'PDF Faylni Yuklash' tugmasini bosing.", reply_markup=pdf)

@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_photos(message: types.Message):
    # Download photo
    photo = message.photo[-1]
    file = await photo.download(destination='images')
    image_paths.append(file.name)  # Add image path to the list

@dp.message_handler(lambda message: message.text == "PDF Faylni Yuklash")
async def send_pdf(message: types.Message):
    if not image_paths:
        await message.reply("Avval rasmlar yuboring.")
        return

    await message.answer("PDF tayyorlanmoqda...")
    pdf_path = "PDF_Convert.pdf"
    images = [Image.open(img).convert('RGB') for img in image_paths]
    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    # Send PDF to user
    with open(pdf_path, 'rb') as pdf_file:
        await message.reply_document(pdf_file)
    # Clear images after conversion
    for img_path in image_paths:
        os.remove(img_path)
    image_paths.clear()
    # Remove PDF file
    os.remove(pdf_path)

@dp.message_handler(lambda message: message.text == "PDF to Image")
async def ask_for_images(message: types.Message):
    await message.reply("PDF ni rasmga alyantirish uchun PDF fayl yuboring. Yuborib bo'lgandan so'ng "
                        "'PDF Faylni Yuklash' tugmasini bosing", reply_markup=image)


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def handle_pdf_to_image(message: types.Message):
    if message.document.mime_type != 'application/pdf':
        await message.reply("Iltimos, faqat PDF fayl yuboring.")
        return
    elif message.text == "Orqaga":
        await message.reply("Quydagilardan birini tanlang 👇", reply_markup=menu)
    file = await message.document.download(destination='images')
    pdf_path = file.name  # Fayl yo‘lini olish

    # Fayl yo‘li mavjudligini tekshirish
    if not os.path.exists(pdf_path):
        await message.reply("PDF faylni yuklab olishda xatolik yuz berdi.")
        return

    # PDF faylni tasvirga aylantirish
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        await message.reply(f"PDF faylni rasmga aylantirishda xatolik: {e}")
        return

    # Rasmni saqlash va yuborish
    image_paths = []
    for i, image in enumerate(images):
        image_path = f"images/page_{i+1}.png"
        image.save(image_path, 'PNG')
        image_paths.append(image_path)

    for image_path in image_paths:
        with open(image_path, 'rb') as img:
            await message.reply_photo(img)

    # Fayllarni o‘chirish
    for image_path in image_paths:
        os.remove(image_path)
    os.remove(pdf_path)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)