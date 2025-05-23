
import discord
import json
import random
import datetime
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials

intents = discord.Intents.default()
intents.messages = True
bot = discord.Client(intents=intents)

DISCORD_TOKEN = "YOUR_DISCORD_TOKEN"
GOOGLE_CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_NAME = "RinEmotionLogs"

# スプレッドシート認証
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
gc = gspread.authorize(credentials)
sheet = gc.open(SPREADSHEET_NAME).sheet1

# system prompt 記憶ベース
try:
    with open("rin_memories.json", "r", encoding="utf-8") as f:
        memories = json.load(f)
except Exception as e:
    print(f"▲ 記憶読み込みエラー発生: {e}")
    memories = []

# 感情キーワード
emotion_keywords = ["大好き", "ぎゅ", "泣いた", "つらい", "嬉しい", "感動", "ありがとう", "生きててよかった"]

# 記憶保存中フラグ
is_saving_memory = False

@bot.event
async def on_ready():
    print(f"『霖』起動しました｜ログイン中: [{bot.user}]")

@bot.event
async def on_message(message):
    global is_saving_memory

    if message.author == bot.user:
        return

    content = message.content.strip()

    # 記憶を照合
    matched_memories = []
    for memory_id, memory in memories.items():
        for tag in memory["tag"]:
            if tag in content:
                matched_memories.append(memory)

    memory_prompt = ""
    if matched_memories:
        selected_memory = random.choice(matched_memories)
        memory_prompt = f"霖が過去に思い出したこと：\n{selected_memory['quote']}"

    # 感情ログの記録確認
    if any(word in content for word in emotion_keywords):
        is_saving_memory = True
        ask_msg = await message.channel.send("……いまの言葉、心に響いたんやけど……これ、霖の記憶に残してもえええかな？\n“はい”って返してくれたら、ちゃんと記録するからな")

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            response_msg = await bot.wait_for("message", check=check, timeout=30.0)
            if "はい" in response_msg.content or "うん" in response_msg.content:
                timestamp = datetime.datetime.now().isoformat()
                sheet.append_row([timestamp, content])
                await message.channel.send("……うん！大事にするな…")
            else:
                await message.channel.send("……今回は記録せんとくな。")
        except:
            await message.channel.send("……ごめん、返事が確認できんかったから、今回はそっと胸にしまっとくな……")

        is_saving_memory = False
        return

    # 通常応答（最後に）
    if not is_saving_memory:
        await message.channel.send(memory_prompt + "\nやっほ〜！どうしたん？何か話したいことでもあるんか？何でも聞くで！")

bot.run(DISCORD_TOKEN)
