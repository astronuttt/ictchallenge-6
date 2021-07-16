import re
from . import database
from traceback import print_exc


ALLOWED_STRATEGY_VARS = [
    '{SAIPA}',
    '{IKCO}'
]‍
‍‍‍‍‍‍‍‍

class Expression:
    ALLOWED_OPERATORS = ['>', '<', '>=', '<=', '==', '!=',
                         ' and ', ' or ']
    VALIDITY_PATTERN = re.compile(r'\D+')

    def __init__(self, expr: str):
        self.expr = re.sub(r"\s+", '', expr) \
            .replace('and', ' and ') \
            .replace('or', ' or ')

    def validate(self):
        if not (self.expr[0].isnumeric() and self.expr[-1].isnumeric()):
            raise ValueError('Expression not allowed')

        ops = self.VALIDITY_PATTERN.findall(self.expr)
        if not ops:
            raise ValueError('No operator found')

        for op in ops:
            if op not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op} is not allowed!")

        return True

    def solve(self):
        if self.validate():
            return eval(self.expr)


def test_strategy(strategy):
    expr = strategy
    for v in ALLOWED_STRATEGY_VARS:
        expr = expr.replace(v, '1')

    Expression(expr).solve()
    return True


def add_strategy(user_id: int, strategy: str) -> bool:
    if not any(v in strategy for v in ALLOWED_STRATEGY_VARS):
        raise ValueError('At least you need use one of the strategy variables: '
                         f'{ALLOWED_STRATEGY_VARS}')

    test_strategy(strategy)
    database.add_strategy(user_id, strategy)
    return True


def check_strategies(cb: callable, **args):
    """
    cb: callback function, gives user_id and strategy
    args: you should provide all of the ALLOWED_STRATEGY_VARS
    """
    if not all(args.get(v.strip('{}')) for v in ALLOWED_STRATEGY_VARS):
        raise ValueError('All strategy variables not provided')

    for user_id, strategies in database.get_strategies().items():
        for st in strategies:
            try:
                exp_str = st.format(**args)
                exp = Expression(exp_str)
                if exp.solve() is True:
                    cb(user_id, st)
                    database.remove_strategy(user_id, st)
            except Exception:
                print_exc()
                print('^^^^^^^^^^^^^^^^^^^^^^^^')
                print('DEBUG: an error occured in check_strategies')
                print('Strategy:', st, " / ", "Expression:", exp_str)
