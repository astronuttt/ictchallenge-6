import time
import openpyxl
from strategy_engine import check_strategies, add_strategy
from random import randint


wb_obj = openpyxl.load_workbook('strategyengine.xlsx')
sheet = wb_obj.active


def extract_data() -> dict:
    output = {}
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        if i != 0:
            name, tradetime, LastTradedPrice = row
            if name not in output:
                output[name] = []
            output[name].append((tradetime, LastTradedPrice))
    return output


def push_fake_strategies():
    # اگر قیمت سهام سایپا کمتر مساوی از 1875 تومان شد به او اطلاع دهد
    add_strategy(randint(1000, 9999), '{SAIPA} < 1875')
    # اگر قیمت سهام سایپا بیشتر مساوی از 1870 تومان شد و قیمت سهام ایران خودرو کمتر از 2050 تومان بود به او اطلاع دهد
    add_strategy(randint(1000, 9999), '{SAIPA} >= 1870 and {IKCO} < 2050')
    # اگر قیمت ایران خودرو 2051 تومان نبود به او اطلاع دهد
    add_strategy(randint(1000, 9999), '{IKCO} != 2051')


def run_test():
    """
    just for test
    updates with fake data from excel file every 1 sec
    """
    fake_data = extract_data()

    def on_trigger(user_id, strategy):
        print(f"[*] This {strategy=} for user {user_id} occurred right now!")

    for idx in range(100):
        SAIPA = fake_data['سایپا'][idx][1]
        IKCO = fake_data['خودرو'][idx][1]
        print(f"[-] Checking with {SAIPA=} {IKCO=}")

        check_strategies(cb=on_trigger, SAIPA=SAIPA, IKCO=IKCO)
        time.sleep(1)


if __name__ == '__main__':
    push_fake_strategies()
    run_test()
