from datetime import date
import json
import argparse
import beancount
from beancount.core.data import Transaction
from beancount.parser import printer
from beancount.core.data import EMPTY_SET

"""
"dataList": [
        {
            "amount": 1.44,
            "billname": "支付交易",
            "billstatus": 2,
            "billtype": "支付交易",
            "paytime": "2024/09/08 00:39:54",
            "refno": "20240908003954317844",
            "tradecode": "6600",
            "tradetype": "2",
            "termname": "一卡通"
        },
        {
            "amount": 0.1,
            "billname": "水控消费",
            "billstatus": 2,
            "billtype": "水控消费",
            "paytime": "2024/09/07 14:23:18",
            "refno": "20240908072046326249",
            "tradecode": "3330",
            "tradetype": "2",
            "termname": "KS101_宝山南11_4F"
        },
        {
            "amount": 12.0,
            "billname": "在线刷卡消费",
            "billstatus": 2,
            "billtype": "在线刷卡消费",
            "paytime": "2024/09/07 12:47:55",
            "refno": "20240907124802284107",
            "tradecode": "6630",
            "tradetype": "2",
            "termname": "宝山山明二楼20号机2024"
        },
        {
            "amount": 200.0,
            "billname": "第三方充值",
            "billstatus": 2,
            "billtype": "第三方充值",
            "paytime": "2024/09/06 20:17:55",
            "refno": "20240906201755239220",
            "tradecode": "6503",
            "tradetype": "1",
            "termname": "一卡通"
        },
"""


trade_map = {
    "6600": {
        "payee": "上海大学",
        "narration": "洗澡",
        "payAccount": "Assets:SchoolCard",
        "receiveAccount": "Expenses:School:Shower",
    },
    "3330": {
        "payee": "上海大学",
        "narration": "热水",
        "payAccount": "Assets:SchoolCard",
        "receiveAccount": "Expenses:School:HotWater",
    },
    "6630": {
        "payee": "上海大学",
        "narration": "食堂",
        "payAccount": "Assets:SchoolCard",
        "receiveAccount": "Expenses:School:Food",
    },
    "6640": {
        "payee": "上海大学",
        "narration": "食堂",
        "payAccount": "Assets:SchoolCard",
        "receiveAccount": "Expenses:School:Food",
    },
    "6615": {
        "payee": "上海大学",
        "narration": "食堂",
        "payAccount": "Assets:SchoolCard",
        "receiveAccount": "Expenses:School:Food",
    },
}


def main():
    parser = argparse.ArgumentParser(description="A simple command line program")
    parser.add_argument(
        "-i", "--input", type=str, help="Input file to read from", required=True
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output file to write to", required=True
    )
    args = parser.parse_args()
    with open(args.input, "r", encoding="utf-8") as input_file:
        data = json.load(input_file)
        with open(args.output, "w", encoding="utf-8") as output_file:
            data = data["dataList"]
            transactions = []
            for item in data:
                try:
                    _ = trade_map[item["tradecode"]]
                except KeyError:
                    print(f"No Such Key: {item['tradecode']}")
                    if item["tradecode"] == "6503":
                        continue
                meta = {}
                meta["refno"] = item["refno"]
                meta["termname"] = item["termname"]
                payee = trade_map[item["tradecode"]]["payee"]
                narration = trade_map[item["tradecode"]]["narration"]
                receiveAccount = trade_map[item["tradecode"]]["receiveAccount"]
                if "宝山商业街面包房" in item["termname"]:
                    narration = "面包"
                    payee = "上海大学西门面包店"
                if "山明" in item["termname"]:
                    narration = "食堂"
                    receiveAccount = "Expenses:School:Food"
                entry = Transaction(
                    meta,
                    date(
                        int(item["paytime"][0:4]),
                        int(item["paytime"][5:7]),
                        int(item["paytime"][8:10]),
                    ),
                    "*",
                    payee,
                    narration,
                    EMPTY_SET,
                    EMPTY_SET,
                    [],
                )
                beancount.core.data.create_simple_posting(
                    entry,
                    trade_map[item["tradecode"]]["payAccount"],
                    str(-round(float(item["amount"]), 2)),
                    "CNY",
                )
                beancount.core.data.create_simple_posting(
                    entry, receiveAccount, None, None
                )
                transactions.append(entry)
            printer.print_entries(transactions, file=output_file)


if __name__ == "__main__":
    main()
