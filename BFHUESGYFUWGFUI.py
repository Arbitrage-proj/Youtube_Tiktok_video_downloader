import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = "8033159498:AAHX9srehZoT2M8e2AabLuO_w2FVKOCv_b0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a YouTube or TikTok link, and I'll download the video for you!")

async def download_video(url: str, path: str = ".") -> str:
    ydl_opts = {
        'outtmpl': f'{path}/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        if not filename.endswith(".mp4"):
            filename = os.path.splitext(filename)[0] + ".mp4"
    return filename

def is_supported_url(url: str) -> bool:
    return any(domain in url for domain in [
        "youtube.com/watch",
        "youtu.be/",
        "tiktok.com/"
    ])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not is_supported_url(url):
        await update.message.reply_text("Please send a valid YouTube or TikTok video URL.")
        return

    msg = await update.message.reply_text("Downloading video, please wait...")

    try:
        filename = await download_video(url)
        file_size = os.path.getsize(filename)

        if file_size > 2 * 1024 * 1024 * 1024:
            await update.message.reply_text("Sorry, the video is too large to send via Telegram.")
            os.remove(filename)
            return

        with open(filename, "rb") as video_file:
            await update.message.reply_video(video_file)

        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    app.run_polling()