"""
pool_selector.py — 元素池随机抽取模块（SQLite 版）

职责：
- 连接 civilight.db 操作 character/world/event 三张池表
- 支持 usage_log 去重窗口（默认 3 天）
- 每次 select 后自动清理超过 90 天前的 usage_log 记录
"""

import random
import sqlite3
from pathlib import Path


class PoolSelector:
    """元素池选择器。从 character/world/event 池中随机抽取元素。"""

    _POOL_TYPES = ["character", "world", "event"]

    def __init__(self, db_path: Path, logger, dedup_window_days: int = 3):
        self.logger = logger
        self.dedup_window_days = dedup_window_days
        self.db = sqlite3.connect(str(db_path))
        self.db.row_factory = sqlite3.Row
        self._init_db()
        self.logger.info(f"PoolSelector connected to {db_path}, dedup_window={dedup_window_days}d")

    def _init_db(self):
        """创建并初始化数据库表结构。"""
        self.db.executescript("""
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
        """)
        self.db.commit()

    def _select_from_pool(self, pool_type: str, limit: int = 2) -> list[tuple[int, str]]:
        """从指定池中随机抽取条目，排除去重窗口内已使用过的条目。

        Returns:
            list of (id, content) tuples
        """
        if self.dedup_window_days <= 0:
            # Ab-005: 窗口 <= 0 时跳过 usage_log 去重
            cursor = self.db.execute(
                f"SELECT id, content FROM {pool_type} ORDER BY RANDOM() LIMIT ?",
                (limit,)
            )
        else:
            cursor = self.db.execute(
                f"""SELECT id, content FROM {pool_type}
                    WHERE id NOT IN (
                        SELECT entry_id FROM usage_log
                        WHERE pool_type = ? AND used_at >= date('now', '-{self.dedup_window_days} days')
                    )
                    ORDER BY RANDOM() LIMIT ?""",
                (pool_type, limit)
            )
        return [(row["id"], row["content"]) for row in cursor.fetchall()]

    def _record_usage(self, entry_id: int, pool_type: str) -> None:
        """记录一条元素使用记录到 usage_log。"""
        self.db.execute(
            "INSERT INTO usage_log (entry_id, pool_type) VALUES (?, ?)",
            (entry_id, pool_type)
        )
        self.db.commit()

    def _cleanup_usage_log(self) -> None:
        """删除超过 90 天的 usage_log 记录。"""
        deleted = self.db.execute(
            "DELETE FROM usage_log WHERE used_at < date('now', '-90 days')"
        ).rowcount
        if deleted:
            self.db.commit()
            self.logger.debug(f"Cleaned up {deleted} old usage_log entries")

    def select(self, count: int = 2) -> list[str]:
        """从所有池中随机抽取 count 个元素。

        Returns:
            抽取的元素列表（字符串）
        """
        all_entries: list[tuple[str, int, str]] = []
        for pool_type in self._POOL_TYPES:
            rows = self._select_from_pool(pool_type, limit=count)
            for entry_id, content in rows:
                all_entries.append((pool_type, entry_id, content))

        if not all_entries:
            return []

        selected = random.sample(all_entries, min(count, len(all_entries)))

        for pool_type, entry_id, _ in selected:
            self._record_usage(entry_id, pool_type)

        self._cleanup_usage_log()
        result = [content for _, _, content in selected]
        self.logger.info(f"Pool selected: {result}")
        return result

    def format_context(self, entries: list[str]) -> str:
        """将抽取的元素格式化为注入 User Message 的上下文。

        Example output:
            "ところで、アーミヤが訓練場で剣の稽古をしている姿が目に入りました。
             ところで、チェルシーが新しい薬の実験をしているようです。"
        """
        if not entries:
            return ""

        context_lines = [f"ところで、{entry}" for entry in entries]
        return "\n".join(context_lines)
