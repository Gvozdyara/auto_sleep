import subprocess
import logging
import datetime as dt
import time
import re
from winsound import Beep

from observable import Variable

if __file__.endswith(".py"):
    def_td = dt.timedelta(minutes=2)
else:
    def_td = dt.timedelta(minutes=27)


class PowerChangeWarning(Exception):
    pass


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
    if not "resumecount" in text.lower():
        raise PowerChangeWarning()
    print(f'text of subprocess is {text}\n{type(text)=}')
    # logging.debug(f'{text=}')
    res = re.findall("Date: [\d:\-.T]+", text)
    # logging.debug(f'{res=}')
    last_wakeup = dt.datetime.fromisoformat(res[0].split(" ")[-1])
    last_boot = get_last_boot()
    return max((last_wakeup, last_boot))


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
        try:
            last_date = get_last_wakeup()
        except PowerChangeWarning:
            last_date = dt.datetime.now() - def_td
            break
        cur_time = dt.datetime.now()
        available_time = def_td.seconds - (cur_time - last_date).seconds
        if available_time <= 0:
            if fail < 4:
                time.sleep(1)
                fail += 1
                logging.debug(("failed to count time left",
                               f"OK if timeOUT Or if after turn ON {last_date=}"))
                continue
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
    try:
        last_date = get_last_wakeup()
    except PowerChangeWarning:
        last_date = dt.datetime.now() - def_td
    available_time = def_td.seconds - (dt.datetime.now() - last_date).seconds
    if available_time > 0:
        # in case if the user manually forced sleep
        message = "Перезапуск программы."
        logging.debug(message)
        variable.state.value = message
        TripleBeep()
        return
    TripleBeep()
    force_sleep()
