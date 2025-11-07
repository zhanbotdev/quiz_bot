import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# === Загружаем вопросы ===
with open("questions.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

# === Стартовое сообщение с кнопкой "Старт" ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("▶️ Старт", callback_data="show_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в викторину!", reply_markup=reply_markup)

# === Меню с кнопкой "Начать викторину" ===
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🎯 Начать викторину", callback_data="start_quiz")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Готов? Нажми, чтобы начать:", reply_markup=reply_markup)

# === Старт викторины ===
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["quiz"] = random.sample(ALL_QUESTIONS, 10)   # 10 случайных
    context.user_data["score"] = 0
    context.user_data["index"] = 0

    await send_question(update, context)

# === Показать текущий вопрос ===
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = context.user_data["quiz"]
    index = context.user_data["index"]

    if index < len(quiz):
        q = quiz[index]
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"answer_{i}")] for i, opt in enumerate(q["options"])]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(q["question"], reply_markup=reply_markup)
    else:
        await finish_quiz(update, context)

# === Проверка ответа ===
async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected = int(query.data.split("_")[1])
    quiz = context.user_data["quiz"]
    index = context.user_data["index"]
    correct = quiz[index]["answer"]

    if selected == correct:
        context.user_data["score"] += 1

    context.user_data["index"] += 1
    await send_question(update, context)

# === Завершение викторины ===
async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = context.user_data["score"]
    total = len(context.user_data["quiz"])

    if score <= 3:
        text = f"Ты набрал {score}/{total}. Попробуй ещё раз!"
    elif score <= 7:
        text = f"Ты набрал {score}/{total}. Хороший результат, но можно лучше!"
    else:
        text = f"Ты набрал {score}/{total}. Отлично! Ты молодец!"

    # показываем кнопку вернуться в меню
    keyboard = [[InlineKeyboardButton("🔁 Сыграть снова", callback_data="show_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

# === Основной запуск ===
def main():
    app = Application.builder().token("8475542493:AAGs2uuy0n419oTMqflZKtyl907NsWk5Vsg").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_menu, pattern="^show_menu$"))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^start_quiz$"))
    app.add_handler(CallbackQueryHandler(check_answer, pattern="^answer_"))

    app.run_polling()

if __name__ == "__main__":
    main()
