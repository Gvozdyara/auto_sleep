# ctypes required for using GetTickCount64()
import ctypes
import datetime as dt
from functools import partial
import logging
import os
import re
import subprocess
import time
import sys
from threading import Thread
from gui import App, ViewMaster
from pystray import MenuItem as item
import pystray
from PIL import Image


def set_user_timer(timer: dict):
    try:
        u_time = int(input(
            f"Введите кол-во минут, не более {timer['available']} минут: ").strip())
        input("Нажмите Enter, чтобы продолжить")
    except ValueError:
        print("Ошибка ввода")
        u_time = timer["available"]
    if u_time > timer['available']:
        u_time = timer["available"]
    update_time(timer, timer.get("u_time"), u_time)
    print(f"Таймер на {timer.get('u_time')}мин запущен")


def update_time(timer: dict, prev_val: int, value: int):
    if prev_val == value:
        return
    timer["u_time"] = value
    timer["started"] = True


def start_count(timer: dict):
    available_time = timer["available"]
    start_time = dt.datetime.now()
    sleep_down = start_time + dt.timedelta(minutes=available_time)
    print(f"Таймер на {available_time} мин запущен")
    td = dt.timedelta(minutes=1)
    cur_time = start_time
    while cur_time < sleep_down:
        if timer.get("last_date") is None:
            pass
        else:
            #  check if the pc was re awaken manually
            text = subprocess.run("""wevtutil qe System /rd:true /f:Text /c:1 /q:"<QueryList><Query Id='0' Path='System'><Select Path='System'>*[System[Provider[@Name='Microsoft-Windows-Kernel-Power']]]</Select></Query></QueryList>\"""",
                                  capture_output=True)
            text = text.stdout.decode("ANSI").replace('\r\n', ';;')
            res = re.findall("Date: [\d:\-.T]+", text)
            last_date = dt.datetime.fromisoformat(res[0].split(" ")[-1])
            if last_date != timer.get("last_date"):
                print("Видимо компьтер был перезапущен вручную. Перезапуск программы.")
                return
            if (dt.datetime.now() - last_date) > dt.timedelta(minutes=28):
                print("Неверная дата включения")
                break


        print(f'{(cur_time - start_time).seconds/60} после старта')
        print(f'Сон для здоровья в {sleep_down.strftime("%H:%M:%S")}')
        print("CTRL + C для выхода\n")
        cur_time += td
        time.sleep(td.seconds)

    for i in range(5):
        print("\a")
        time.sleep(1)
    print("Спящий режим через 60сек")
    time.sleep(50)

    if timer.get("last_date") is None:
        pass
    else:
        #  check if the pc was re awaken manually
        text = subprocess.run("""wevtutil qe System /rd:true /f:Text /c:1 /q:"<QueryList><Query Id='0' Path='System'><Select Path='System'>*[System[Provider[@Name='Microsoft-Windows-Kernel-Power']]]</Select></Query></QueryList>\"""",
                              capture_output=True)
        text = text.stdout.decode("ANSI").replace('\r\n', ';;')
        res = re.findall("Date: [\d:\-.T]+", text)
        last_date = dt.datetime.fromisoformat(res[0].split(" ")[-1])
        print(f'{last_date=} {timer.get("last_date")=}')
        if last_date != timer.get("last_date"):
            print("Видимо компьтер был перезапущен вручную. Перезапуск программы.")
            return
    print("\a")
    subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def counter(user_time: dict):
    #  reset data that could be saved from the prev turn
    user_time["u_time"] = None
    user_time["started"] = None
    user_time["available"] = None
    user_time["last_date"] = None

    text = subprocess.run("""wevtutil qe System /rd:true /f:Text /c:1 /q:"<QueryList><Query Id='0' Path='System'><Select Path='System'>*[System[Provider[@Name='Microsoft-Windows-Kernel-Power']]]</Select></Query></QueryList>\"""",
                          capture_output=True)
    text = text.stdout.decode("ANSI").replace('\r\n', ';;')
    res = re.findall("Date: [\d:\-.T]+", text)
    last_date = dt.datetime.fromisoformat(res[0].split(" ")[-1])
    print(f'    Последнее включение {last_date.strftime("%d.%m.%Y %H:%M")}\n')

    available_time = dt.timedelta(minutes=28) - (dt.datetime.now() - last_date)
    available_time = int(available_time.seconds / 60)
    user_time["available"] = available_time
    user_time["last_date"] = last_date


    if available_time not in range(3, 28):
        print(f'---!!!---\nОшибка. Рекомендую переключить компьютер в сон и включить заново\n---!!!---\n')

    #start_count(user_time)
    subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


def quit_window(icon, item):
    icon.stop()
    root.destroy()


def show_window(icon, item):
    icon.stop()
    root.after(0, root.deiconify)


def withdraw_window():
    root.withdraw()
    try:
        image = Image.open(os.path.join(
            os.path.split(sys.executable)[0], "icon.png"))
    except FileNotFoundError:
        image = Image.open("icon.png")
    menu = (item('Quit', quit_window), item('Show', show_window))
    icon = pystray.Icon("name", image, "Auto sleep", menu)
    icon.run()


def main():
    global root
    formatter = '[%(levelname)s] [%(funcName)s] [%(asctime)s] %(message)s'
    logging.basicConfig(filename="error.log",
                        encoding='utf-8',
                        level=logging.DEBUG,
                        format=formatter)
    root = App()
    ViewMaster(root)

    root.protocol('WM_DELETE_WINDOW', withdraw_window)
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f'on main {e}')



