import numpy as np
from random import choice, shuffle
from typing import Tuple, Union
from enum import Enum


class GameStatus(Enum):
    PLAYING = 'playing'
    FINISHED = 'finished'
    LOSS = 'loss'
    WIN = 'win'


def create_board(size=[9, 9]) -> np.array:
    board = np.zeros(size, dtype=int)
    return board


def load_board(array: list) -> np.array:
    board = np.array(array)
    return board


def hot_neighbors(board, stone) -> list:
    row, col = stone
    max_c = board.shape[0]
    sides = []
    if (c := col-1) >= 0:
        sides.append(((row, c), board[row][c]))  # left
    if (c := col+1) < max_c:
        sides.append(((row, c), board[row][c]))  # right
    if (r := row-1) >= 0:
        sides.append(((r, col), board[r][col]))  # top
    if (r := row+1) < max_c:
        sides.append(((r, col), board[r][col]))  # bottom

    return sides


def is_captured(neighbors, by) -> bool:
    if not neighbors:
        return False
    return all(s[1] == by for s in neighbors)


def check_game_status(board) -> Tuple[GameStatus, Union[tuple, None]]:
    row, col = board.shape
    no_zeroes = True
    for r in range(row):
        for c in range(col):
            stone = (r, c)
            val = board[r][c]

            if val == 0:
                no_zeroes = False
                continue

            if val == 1:
                neighbors = hot_neighbors(board, stone)
                if is_captured(neighbors, by=-1):
                    # damn... i lost, this stone captured
                    return (GameStatus.LOSS, stone)

    if no_zeroes is True:
        return (GameStatus.FINISHED, None)

    return (GameStatus.PLAYING, None)


def find_danger_neighbor(neighbors) -> tuple:
    shuffle(neighbors)
    for stone, value in neighbors:
        if value == 0:
            return stone


def bot_play(board) -> Tuple[tuple, bool, tuple]:
    row, col = board.shape
    for r in range(row):
        for c in range(col):
            stone = (r, c)
            if board[r][c] != 0:
                continue

            vboard = board.copy()
            neighbors = hot_neighbors(vboard, stone)

            vboard[r][c] = 1  # if i play on this
            for nei_stone, nei_val in neighbors:
                nei_stone_neighbors = hot_neighbors(vboard, nei_stone)
                # will i capture any of my neighbors?
                if is_captured(nei_stone_neighbors, by=1):
                    # yes i will, i'll play on this stone
                    return stone, True, nei_stone

            vboard[r][c] = -1  # if they play on this
            for nei_stone, nei_val in neighbors:
                nei_stone_neighbors = hot_neighbors(vboard, nei_stone)
                # will they capture me?
                if is_captured(nei_stone_neighbors, by=-1):
                    # yes they will, omg i should cover this
                    return stone, False, None

    # otherwise, play somewhere around -1's randomly
    wheres = np.argwhere(board == -1)
    if wheres.any():
        where = choice(wheres)
        neighbors = hot_neighbors(board, where)
        stone = find_danger_neighbor(neighbors)
        if stone is not None:
            return stone, False, None

    stone = choice(np.argwhere(board == 0))
    return stone, False, None


def play(board) -> Tuple[np.array, GameStatus, Union[tuple, None]]:
    status, hot_stone = check_game_status(board)
    if status == GameStatus.PLAYING:
        (r, c), win, _win_cap_stone = bot_play(board)
        board[r][c] = 1
        if win is True:
            status = GameStatus.WIN
            hot_stone = _win_cap_stone

    return (board, status, hot_stone)
