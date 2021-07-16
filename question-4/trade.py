from typing import Dict, List, Union
import pandas
from pandas.core.frame import DataFrame
import json


def get_data(filepath: str) -> DataFrame:
    excel = pandas.read_excel(filepath, None)
    return excel["Sheet1"]


def get_users_trades(data: DataFrame) -> Dict[int, List[int]]:
    trades = dict()
    for trade, user_id in zip(data["ArzeshKole"], data["userid"]):
        if trades.get(user_id):
            trades[user_id].append(int(trade))
        else:
            trades[user_id] = [trade]
    return trades


def sort_user_scores(user_scores: Dict[int, int]) -> Dict[int, int]:
    return list(sorted(user_scores.items(), key=lambda item: item[1], reverse=True))


def get_user_trades_scores(data: DataFrame) -> Dict[int, int]:
    user_trades = get_users_trades(data)
    return sort_user_scores(
        {user_id: sum(trxs) / len(trxs) for user_id, trxs in user_trades.items()}
    )


def grouping_by_trades_score(
    user_scores: Dict[int, int], discount_groups: Dict[int, int]
) -> Dict[int, int]:
    groups = dict()
    start, end = (0, 0)
    for indx, (percent, quantity) in enumerate(discount_groups.items()):
        end += quantity
        groups.update(
            {
                f"group_{indx}": {
                    "percent": f"{percent}%",
                    "users": [us[0] for us in user_scores[start:end]],
                }
            }
        )
        start += quantity
    return groups


def grouping_users(
    data: DataFrame, discount_groups: Dict[int, int]
) -> Dict[str, Dict[str, Union[int, List[int]]]]:
    user_scores = get_user_trades_scores(data)
    return grouping_by_trades_score(user_scores, discount_groups)


def check_discount_groups(discount_groups: Dict[int, int]) -> Dict[int, int]:
    discount_groups = dict(
        sorted(discount_groups.items(), key=lambda item: item[0], reverse=True)
    )
    for k, v in discount_groups.items():
        if k > 50 or k < 0:
            raise ValueError(
                f"Error in parsing key {k}: groups percentage must be between 0 and 50"
            )
        if not isinstance(k, int) or not isinstance(v, int):
            raise ValueError(
                f"Error in parsing key {k}: key and values must be type of integer"
            )
    return discount_groups


def print_result(result: Dict[str, Dict[str, Union[int, List[int]]]]) -> None:
    for group, data in result.items():
        print(
            group,
            ":\tDiscount percent: ",
            data.get("percent"),
            f"\nUsers: ({len(data['users'])})\n",
        )
        [print(user, end="\t") for user in data["users"]]
        print("\n")


def save(filepath: str, results: str) -> None:
    with open(filepath, "w") as file:
        file.write(results)


def main(discount_groups: Dict[int, int], datapath: str) -> None:
    data = get_data(datapath)
    discount_groups = check_discount_groups(discount_groups)
    results = grouping_users(data, discount_groups)
    # you can simply print the result, save it in a file or ...
    print_result(results)
    # save("test.txt", str(json.dumps(results, indent=4)))


if __name__ == "__main__":
    # sample data:
    discount_groups = {
        #   percent: quantity
        50: 20,
        40: 30,
        30: 50,
        20: 100,
    }
    main(discount_groups, "trade.xlsx")
