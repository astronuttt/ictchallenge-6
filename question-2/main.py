import itertools
import timeit
from functools import wraps


def exec_time(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        start = timeit.default_timer()
        f = func(*args, **kwargs)
        end = timeit.default_timer()
        print(f"{func.__name__} execution time: {(end - start):.15f}")
        return f

    return decorator


def count_digits(n):
    n = str(n)
    return len(n)


@exec_time
def generate_largest_method1(_list: list) -> int:
    """
    در این متود تمام حالات ساخته میشه و بزرگترین تعیین میشود
    """
    if len(_list) > 50:
        raise ValueError("List length must up to 50")

    if not all(count_digits(i) <= 5 for i in _list):
        raise ValueError("All numbers in list must be maximum 5 digits")

    _list = map(lambda i: int(i), _list)  # to remove zero's leftside of digits
    _list = filter(lambda i: i >= 0, _list)  # to ignore negative numbers
    largest = 0
    for i in itertools.permutations(str(_) for _ in _list):
        n = int("".join(i))
        if n > largest:
            largest = n

    return largest


@exec_time
def generate_largest_method2(_list: list) -> int:
    """
    در این متود در چرخه های مختلف بزرگترین اعداد از نظر رقم چپ از لیست اعداد حذف شده
    و از چپ به راست بزرگترین عدد را میسازند
    این چرخه تا زمانی که لیست اعداد خالی شود ادامه پیدا میکند
    """
    if len(_list) > 50:
        raise ValueError("List length must up to 50")

    if not all(count_digits(i) <= 5 for i in _list):
        raise ValueError("All numbers in list must be maximum 5 digits")

    _list = map(lambda i: int(i), _list)  # to remove zero's leftside of digits
    _list = filter(lambda i: i >= 0, _list)  # to ignore negative numbers
    _list = list(_list)

    largest = ""
    while _list:
        m = max(_list, key=lambda i: str(i)[0])
        _list.remove(m)
        largest += f"{m}"

    return int(largest)


example_list = [0, 44, "00050", 6, 5, "09", 0, -2]


print("method 1:", generate_largest_method1(example_list))
print("method 2:", generate_largest_method2(example_list))
