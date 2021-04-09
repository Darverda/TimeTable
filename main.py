import config
import requests
import lxml.html
import datetime
from collections import OrderedDict


# Данные для формы авторизации
formdata = {
    'login': config.LOGIN,
    'password': config.PASSWORD,
}


def login(session):
    '''
    Авторизация
    :param session:
    :return:
    '''
    session.post(config.AUTH_URL, data=formdata)

def get_timetable(text, required_date):
    '''
    Получение расписания с сайта
    :param text:
    :param required_date:
    :return: Упорядоченный словарь, ключи - дни недели(например, 13.01),
    значения - кортеж. Первый элемент - день недели, второй - список уроков
    '''

    # признак получения расписания за определенный день
    on_day = False
    if required_date != "":
        on_day = True

    ord_dict = OrderedDict()

    doc = lxml.html.document_fromstring(text)

    days = doc.xpath("//div[contains(@class, 'diaries_mobile__day ')]")
    for d in days:
        day_of_week = d.xpath(".//div[@class='diaries_mobile__day__dayweek']")[0]
        date = d.xpath(".//div[@class='diaries_mobile__day__data']")[0]
        if on_day and date.text != required_date:
            continue

        lessons = d.xpath(".//div[@class='diaries_mobile__lesson']")
        lesson_list = []
        if len(lessons) == 0:
            lesson_list.append("Нет занятий")
        for l in lessons:
            name = l.xpath(".//div[@class='diaries_mobile__lesson__discipline']")
            time = l.xpath(".//span[@class='diaries_mobile__lesson__time']")
            lesson_list.append(f"✔ {time[0].text.strip()} {name[0].text.strip()}")

        ord_dict[date.text.strip()] = (day_of_week.text.strip(), lesson_list)
    return ord_dict


def get_on_week(session):
    '''
    Расписание на неделю
    :param session:
    :return:
    '''
    timetable_lst = ["⏰ Расписание на неделю:\n"]
    site_response = session.get(config.DIARY_URL)
    text = site_response.text

    timetable = get_timetable(text, "")

    for date in timetable:
        day_name, lessons = timetable[date]
        timetable_lst.append(f"📅 {date} {day_name}")
        for lesson in lessons:
            timetable_lst.append(lesson)
        timetable_lst.append("\n")
    return "\n".join(timetable_lst)


def get_by_date(session, date):
    '''
    Получение расписания на определенную дату
    :param session:
    :param date:
    :return:
    '''
    splitted_date = date.split('.')
    day = splitted_date[0]
    month = splitted_date[1]
    year = splitted_date[2]

    dt = datetime.datetime(int(year), int(month), int(day))
    week = dt.isocalendar()[1] + 1
    site_response = session.get(config.DIARY_URL+f"&year={dt.year}&week={week}&log=false")

    formatted_date = f"{day}.{month}"

    timetable = get_timetable(site_response.text, formatted_date)

    if formatted_date in timetable:
        day_of_week, lessons = timetable[formatted_date]
        timetable_lst = [f"⏰ Расписание на {date}, {day_of_week}:\n"]
        for i in lessons:
            timetable_lst.append(i)
        return '\n'.join(timetable_lst)
    else:
        return "NOT FOUND"

if __name__ == "__main__":
    session = requests.session()
    login(session)
    res = get_by_date(session, "01.02.2021")
    #s = get_on_week(session)
    #print(s)
    print(res)
    #print('\n'.join(res))