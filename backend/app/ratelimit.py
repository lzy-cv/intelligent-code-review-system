"""轻量内存限流：按用户限制审查接口的调用频率。

单进程内存实现，适合当前部署形态；多 worker / 多实例部署时应换成
Redis 之类的共享存储（接口保持不变即可替换）。
"""
import time
from collections import deque


class SlidingWindowLimiter:
    """滑动窗口限流：window 秒内同一 key 最多 max_calls 次。"""

    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window = window_seconds
        self._hits: dict[str, deque] = {}

    def check(self, key: str) -> int | None:
        """放行返回 None；被限流则返回建议等待的秒数。"""
        now = time.monotonic()
        q = self._hits.get(key)
        if q is None:
            q = self._hits[key] = deque()

        # 滑出窗口外的记录
        while q and now - q[0] >= self.window:
            q.popleft()

        if len(q) >= self.max_calls:
            return max(1, int(self.window - (now - q[0])) + 1)

        q.append(now)
        self._evict_empty()
        return None

    def _evict_empty(self):
        """清理过期空队列，避免长期运行下 key 无限增长。"""
        if len(self._hits) < 1024:
            return
        now = time.monotonic()
        for k in [k for k, q in self._hits.items() if not q or now - q[-1] >= self.window]:
            del self._hits[k]
