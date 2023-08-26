import subprocess
import logging
import datetime as dt
import time
import re
from winsound import Beep

from observable import Variable

def_td = dt.timedelta(minutes=9)


class TripleBeep:

    def __init__(self):
        Beep(740, 400)
        time.sleep(0.2)
        Beep(659, 800)
        time.sleep(0.2)


def force_sleep():
    subprocess.run("C:/Windows/System32/rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)


def get_last_wakeup() -> dt.datetime:
    text = subprocess.Popen("""C:/Windows/System32/wevtutil qe System /rd:true /f:Text /c:1 /q:"<QueryList><Query Id='0' Path='System'><Select Path='System'>*[System[Provider[@Name='Microsoft-Windows-Kernel-Power']]]</Select></Query></QueryList>""",
                            stdout=subprocess.PIPE, stderr=None, shell=True)
    # text = text.stdout.decode("ANSI").replace('\r\n', ';;')
    text = text.communicate()[0].decode("ANSI").replace('\r\n', ';;')
    print(f'text of subprocess is {text}\n{type(text)=}')
    # logging.debug(f'{text=}')
    res = re.findall("Date: [\d:\-.T]+", text)
    # logging.debug(f'{res=}')
    return dt.datetime.fromisoformat(res[0].split(" ")[-1])


def get_last_boot() -> dt.datetime:
    text = subprocess.Popen("C:/Windows/System32/wbem/wmic path Win32_OperatingSystem get LastBootUpTime",
                            stdout=subprocess.PIPE, stderr=None, shell=True)
    text = re.findall("\d+", text.communicate()[0].decode("ANSI"))[0]
    return dt.datetime.strptime(text, "%Y%m%d%H%M%S")


def counter(variable):
    while True:
        start_count(variable)


def start_count(variable):
    td = dt.timedelta(seconds=10)
    fail = 0
    while True:
            #  check if the pc was re awaken manually
        last_date = get_last_wakeup()
        cur_time = dt.datetime.now()
        available_time = def_td.seconds - (cur_time - last_date).seconds
        if available_time <= 0:
            if fail < 4:
                time.sleep(1)
                fail += 1
                logging.debug(("failed to count time left",
                               f"OK if timeOUT Or if after turn ON {last_date=}"))
                continue
            last_boot = get_last_boot()
            cur_time = dt.datetime.now()
            available_time = def_td.seconds - (cur_time - last_boot).seconds
            if available_time <= 0:
                logging.debug(f"{available_time=} {def_td.seconds=} {(cur_time - last_boot).seconds=} is less than 0")
                break

        minutes_left = int(available_time/60)
        seconds = available_time - minutes_left * 60
        if 0 <= seconds < 10:
            seconds = f'0{seconds}'

        message = (f'''Сон в {dt.datetime.fromtimestamp(
            time.time() + available_time).strftime("%H:%M:%S")}\n'''
                   f'{minutes_left}:{seconds}')
        variable.state.value = (f'{message}')

        time.sleep(td.seconds)

    logging.debug("Спящий режим через 60сек")
    variable.state.value = "Спящий режим через 60сек"
    TripleBeep()

    time.sleep(57)


    _last_date = get_last_wakeup()
    if _last_date not in (last_date, last_boot):
        message = "Перезапуск программы."
        logging.debug(message)
        variable.state.value = message
        return
    TripleBeep()
    force_sleep()
