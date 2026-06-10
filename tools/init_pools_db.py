"""
init_pools_db.py — 从 txt 种子数据初始化 civilight.db

行为：
1. 连接 Custom/characters/pools/civilight.db
2. 建表（IF NOT EXISTS）
3. 从 character.txt / world.txt / event.txt 读取数据
4. INSERT OR IGNORE 写入（Ab-001: 幂等）
5. 标注 source = "seed_txt"
"""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POOLS_DIR = ROOT / "Custom" / "characters" / "pools"
DB_PATH = POOLS_DIR / "civilight.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS character (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    tags TEXT,
    source TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS world (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    tags TEXT,
    source TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    tags TEXT,
    source TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    pool_type TEXT NOT NULL,
    used_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_usage_log_used_at ON usage_log(used_at);
CREATE INDEX IF NOT EXISTS idx_usage_log_pool_type ON usage_log(pool_type);
"""


def load_txt_lines(pool_type: str) -> list[str]:
    """从 txt 文件读取非注释、非空行。"""
    path = POOLS_DIR / f"{pool_type}.txt"
    if not path.exists():
        print(f"WARNING: {path} not found, skipping")
        return []
    lines = [
        line.strip()
        for line in path.read_text("utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    print(f"  {pool_type}: {len(lines)} entries from {path.name}")
    return lines


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))

    # 建表
    db.executescript(SCHEMA_SQL)
    print(f"Connected to {DB_PATH}")

    # 种子数据入库（幂等：仅当 source='seed_txt' 的行数为 0 时写入）
    for pool_type in ["character", "world", "event"]:
        existing = db.execute(
            f"SELECT COUNT(*) FROM {pool_type} WHERE source = 'seed_txt'"
        ).fetchone()[0]
        if existing > 0:
            print(f"  {pool_type}: seed data already exists ({existing} rows), skipping")
            continue

        entries = load_txt_lines(pool_type)
        for entry in entries:
            db.execute(
                f"INSERT INTO {pool_type} (content, source) VALUES (?, 'seed_txt')",
                (entry,)
            )
        print(f"  {pool_type}: inserted {len(entries)} seed rows")

    db.commit()
    db.close()
    print("Done.")


if __name__ == "__main__":
    init_db()
