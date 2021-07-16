"""
This is just a test database that stores in memory
"""
from fakeredis import FakeStrictRedis
from typing import Dict

redis = FakeStrictRedis(decode_responses=True)


def add_strategy(user_id, strategy):
    return redis.sadd(f'strategies:{user_id}', strategy)


def get_strategies() -> Dict[int, set]:
    res = dict()
    for key in redis.scan_iter("strategies:*"):
        user_id = int(key.split(':')[-1])
        res[user_id] = redis.smembers(key)

    return res


def get_strategies_by_user(user_id: int) -> set:
    return redis.smembers(f'strategies:{user_id}')


def remove_strategy(user_id, strategy):
    return redis.srem(f'strategies:{user_id}', strategy)
