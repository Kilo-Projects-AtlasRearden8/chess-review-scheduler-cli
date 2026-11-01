import json
import os

SEED = [
    {
        "id": "seed-1",
        "category": "opening",
        "title": "Italian Game",
        "fen": "r1bqkbnr/pppp1ppp/2n5/1Bb2p2/4P3/5N2/PPPP1PPP/RNBQK1NR w KQkq - 4 4",
        "moves": "1. e4 e5 2. Nf3 Nc6 3. Bc4",
        "notes": "Classical open game",
        "created": "2026-01-01",
        "next_review": "2026-01-01",
        "interval": 0,
        "repetitions": 0,
        "ease_factor": 2.5,
    },
    {
        "id": "seed-2",
        "category": "tactic",
        "title": "Back-rank mate pattern",
        "fen": "",
        "moves": "",
        "notes": "Look for back-rank weaknesses",
        "created": "2026-01-01",
        "next_review": "2026-01-01",
        "interval": 0,
        "repetitions": 0,
        "ease_factor": 2.5,
    },
    {
        "id": "seed-3",
        "category": "endgame",
        "title": "Lucena position",
        "fen": "",
        "moves": "",
        "notes": "Bridge building with the rook",
        "created": "2026-01-01",
        "next_review": "2026-01-01",
        "interval": 0,
        "repetitions": 0,
        "ease_factor": 2.5,
    },
]

with open("/tmp/kilo/import_seed.json", "w", encoding="utf-8") as fh:
    json.dump(SEED, fh, indent=2)

os.makedirs("/tmp/kilo", exist_ok=True)
