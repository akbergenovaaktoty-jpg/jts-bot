import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8803054985:AAGuBZ8DgwGvY7mFODUfXqOBOwGlTJVMJSo"
GROUP_ID = -5298600648

CURATORS = {
    "Айдана": {"id": 699436618, "username": "@Aidana_seitpeshova", "whatsapp": "https://chat.whatsapp.com/KTQWMSDY6MF0clO1F9hlPa"},
    "Нурай": {"id": 683139471, "username": "@nuray_ik", "whatsapp": "https://chat.whatsapp.com/Gzf8MM9kWqs2PhEgFRvEC9"},
    "Томирис": {"id": 862482306, "username": "@Tomiris_Kaken", "whatsapp": "https://chat.whatsapp.com/Bx3p2g1gaUdCBAbeufhH5W"},
    "Сара": {"id": 778335083, "username": "@Sarang_Saruman", "whatsapp": "https://chat.whatsapp.com/HVs09o62k3DDE0BVC1TiIB"},
    "Майра": {"id": None, "username": "@mayra", "whatsapp": "https://chat.whatsapp.com/Ll3Fe6j6n1tDdEfL48zlEr"},
}

logging.basicConfig(level=logging.INFO)

ANKETA = """Заполните анкету - скопируйте, вставьте свои данные и отправьте:

ФИО: 
Год рождения, дата, месяц: 
Номер: 
Email: 
Стаж работы: 
Языки проведения уроков: 
Уровни которые можете брать: 
Возрасты которые будете брать: 
Мои сертификаты: 
Спец тарифы которые ведете (Duolingo / IELTS / TOEFL и др.): """

QUESTIONS = [
    ("ФИО:", None),
    ("Сколько уроков выделяется на завершение одного уровня по гарантии?", "36"),
    ("Что нужно делать, если студент систематически опаздывает или отменяет уроки?", "менеджер куратор правила"),
    ("Какие причины могут стать триггером того, что студент не успеет закончить за 36 уроков?", "опоздани перенос отмен домашн медленн"),
    ("Что должен делать преподаватель, если студент не понимает материал и идёт медленнее программы?", "материал упражнени менеджер предупредить"),
    ("По каким материалам занимаемся со студентами?", "новым материалам"),
    ("Что означает 'обязывает заниматься по новым материалам'?", "speaking listening writing reading секци навык"),
    ("Почему обязательно заниматься по новым материалам со всеми студентами, включая гарантийных?", "навык уложиться гарантий план"),
    ("Что будет если не закончить 1 уровень со студентом за 36 уроков?", "гарантий ответственност нарушени"),
]

TEST_MSG = "Ответьте на все вопросы одним сообщением в таком формате:\n\n" + "\n\n".join(
    [f"{i+1}. {q}" for i, (q, _) in enumerate(QUESTIONS)]
) + "\n\nПример:\n1. Иванов Иван Иванович\n2. 36 уроков\n3. ..."

MSG1 = """Анкета отправлена куратору!

Изучите материалы:

Работа на платформе:
https://drive.google.com/drive/folders/1X-HZBiNUZ2tvgjR-EAspZdUl5SnETq0E

Работа по гарантийному формату:
https://drive.google.com/drive/folders/1HG5YoeOHrGiFUw5KkGdRpKAmjunWeDgX

Как отметить уроки в AlfaCRM:
https://drive.google.com/file/d/1lRwPZoMixWKmpxU7r2-BhUD2c14g6KZU/view

Как вытащить реестр зарплаты:
https://drive.google.com/file/d/1-3_KyhHGt11zFDmQWbLtQhvLEeoK6rOx/view"""

MSG2 = """Концепт работы:

- Реакция на студента в чате + резюме менеджеру в ЛС
- В день: 10-20 откликов
- Минимум 5 постоянных студентов (1 из них групповой)
- Первые 2 месяца можно вести 2-3 студента

Студентов ведёте до конца уровня. По гарантии - замена преподавателя не допускается.

ВАЖНО: На отметку урока 3 дня - иначе урок сгорает!"""


async def start(update, context):
    context.user_data.clear()
    context.user_data["step"] = "choose_curator"
    keyboard = [[InlineKeyboardButton(name, callback_data=f"curator_{name}")] for name in CURATORS]
    await update.message.reply_text(
        "Добро пожаловать в школу!\n\nВыберите вашего куратора:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("curator_"):
        name = query.data.replace("curator_", "")
        context.user_data["curator"] = name
        context.user_data["step"] = "anketa"
        await query.edit_message_text(
            f"Ваш куратор: {name}\n\nЗаполните анкету - скопируйте, вставьте свои данные и отправьте:\n\n" + ANKETA
        )

    elif query.data == "start_test":
        context.user_data["step"] = "test"
        await query.edit_message_text(TEST_MSG)

    elif query.data == "joined_whatsapp":
        curator_name = context.user_data.get("curator", "Неизвестно")
        curator_info = CURATORS.get(curator_name, {})
        curator_id = curator_info.get("id")
        curator_username = curator_info.get("username", "")
        user = query.from_user
        username = f"@{user.username}" if user.username else user.full_name
        msg = f"Преподаватель {username} вступил в WhatsApp чаты! Куратор: {curator_username}"

        await context.bot.send_message(chat_id=GROUP_ID, text=msg)
        if curator_id:
            try:
                await context.bot.send_message(chat_id=curator_id, text=msg)
            except:
                pass

        await query.edit_message_text("Отлично! Добро пожаловать в команду! Ваш куратор уведомлен.")


async def message_handler(update, context):
    step = context.user_data.get("step")
    text = update.message.text.strip()

    if not step or step == "choose_curator":
        await update.message.reply_text("Напишите /start чтобы начать.")
        return

    if step == "anketa":
        if len(text) < 20:
            await update.message.reply_text("Пожалуйста, скопируйте шаблон анкеты, заполните и отправьте:\n\n" + ANKETA)
            return

        curator_name = context.user_data.get("curator", "Неизвестно")
        curator_info = CURATORS.get(curator_name, {})
        curator_id = curator_info.get("id")
        curator_username = curator_info.get("username", "")
        context.user_data["step"] = "materials"

        report = f"Новый преподаватель!\nКуратор: {curator_username}\n\n{text}"
        await context.bot.send_message(chat_id=GROUP_ID, text=report)
        if curator_id:
            try:
                await context.bot.send_message(chat_id=curator_id, text=report)
            except:
                pass

        await update.message.reply_text(MSG1)
        await update.message.reply_text(
            "После изучения материалов нажмите кнопку чтобы пройти тест:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Начать тест", callback_data="start_test")]
            ])
        )

    elif step == "test":
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        answers = []
        for line in lines:
            if len(line) > 2 and line[0].isdigit() and ". " in line[:4]:
                answers.append(line.split(". ", 1)[1])
            else:
                answers.append(line)

        if len(answers) < len(QUESTIONS):
            await update.message.reply_text(f"Нужно ответить на все {len(QUESTIONS)} вопросов. У вас {len(answers)}. Попробуйте ещё раз.")
            return

        context.user_data["step"] = "done"
        correct = 0
        result_lines = []
        report_lines = []

        for i, (q, keywords) in enumerate(QUESTIONS):
            ans = answers[i] if i < len(answers) else ""
            if keywords is None:
                result_lines.append(f"{i+1}. {q}\nОтвет: {ans}")
                report_lines.append(f"В{i+1}: {q}\nОтвет: {ans}")
                correct += 1
            else:
                ok = any(kw in ans.lower() for kw in keywords.split())
                if ok:
                    correct += 1
                mark = "Верно" if ok else "Неверно"
                result_lines.append(f"{i+1}. {q}\nОтвет: {ans}\n{mark}")
                report_lines.append(f"В{i+1}: {q}\nОтвет: {ans}\n{mark}")

        total = len(QUESTIONS)
        summary = f"Тест завершен! Правильных: {correct} из {total}\n\n"
        if correct >= total * 0.7:
            summary += "Отлично! Вы успешно прошли тест."
        else:
            summary += "Рекомендуем повторить материалы и пройти тест заново. Напишите /start"

        await update.message.reply_text(summary + "\n\n" + "\n\n".join(result_lines))
        await update.message.reply_text(MSG2)

        curator_name = context.user_data.get("curator", "Неизвестно")
        curator_info = CURATORS.get(curator_name, {})
        curator_whatsapp = curator_info.get("whatsapp", "")

        await update.message.reply_text(
            "Вступайте в WhatsApp группы:\n\n"
            f"Чат вашего кураторства ({curator_name}):\n{curator_whatsapp}\n\n"
            "Группа всех преподавателей школы:\n"
            "https://chat.whatsapp.com/K8XoKiTVStE496t9m4E8r0\n\n"
            "Чат заявок студентов:\n"
            "https://chat.whatsapp.com/FPWhYg6tpEHKgPkrwmav4L\n"
            "https://chat.whatsapp.com/G6cb9sSkJFiEG3BgJ5oGFq\n\n"
            "После того как вступили - нажмите кнопку:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Я вступил в чаты", callback_data="joined_whatsapp")]
            ])
        )
        curator_id = curator_info.get("id")
        curator_username = curator_info.get("username", "")
        report = f"Результат теста (куратор: {curator_username}):\n{correct}/{total}\n\n" + "\n\n".join(report_lines)
        await context.bot.send_message(chat_id=GROUP_ID, text=report[:4000])
        if curator_id:
            try:
                await context.bot.send_message(chat_id=curator_id, text=report[:4000])
            except:
                pass

    elif step == "done":
        await update.message.reply_text("Вы уже завершили оформление! Если нужно начать заново - напишите /start")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()


if __name__ == "__main__":
    main()
