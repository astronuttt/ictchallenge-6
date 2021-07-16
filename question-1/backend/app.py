from fastapi import FastAPI, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from typing import Union, Tuple, List
import capture_go
import models


app = FastAPI()


@app.post("/")
async def create_game(db: Session = Depends(models.get_db)):
    board = capture_go.create_board([9, 9])
    game = models.Game()
    game.board = board.tolist()
    db.add(game)
    db.commit()
    db.refresh(game)
    return {
        "id": game.id,
        "board": game.board
    }


@app.put("/")
async def play_game(id: int = Body(...),
                    new_stone: Union[Tuple[int], List[int]] = Body(...),
                    db: Session = Depends(models.get_db)):
    if not (game := db.query(models.Game).filter(models.Game.id == id).first()):
        raise HTTPException(404, "Game not found")

    if len(new_stone) != 2:
        raise HTTPException(400, "Wrong stone location")
    try:
        stone_r, stone_c = map(int, new_stone)
    except ValueError:
        raise HTTPException(400, "Wrong stone location")

    if not (0 <= stone_r < 9 or 0 <= stone_c < 9):
        raise HTTPException(400, "Wrong stone location")

    try:
        board = capture_go.load_board(game.board)
        if board.shape != (9, 9):
            raise HTTPException(400, 'Invalid board')
        if board[stone_r][stone_c] != 0:
            raise HTTPException(400, 'Stone not allowed')
        board[stone_r][stone_c] = -1
    except ValueError:
        raise HTTPException(400, 'Invalid board')

    board, status, captured_stone = capture_go.play(board)

    game.board = board.tolist()
    if status.value in ['win', 'loss']:
        if captured_stone == -1:
            game.winner = game.Players.WHITE
        else:
            game.winner = game.Players.BLACK
    db.commit()
    db.refresh(game)

    return {
        "board": board.tolist(),
        "status": status,
        "captured_stone": captured_stone
    }
