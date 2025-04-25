# app.py
from flask import Flask, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route("/")
def home():
    return "霖Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    # ここにLINEのWebhookイベント受信処理を入れる（後で追加）
    return "OK"

if __name__ == "__main__":
    app.run()
