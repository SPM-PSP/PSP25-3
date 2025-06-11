import bisect

class SegmentStructure:
    def __init__(self):
        self.segments = []

    def add_segment(self, start, end, height):
        self.segments.append((start, end, height))

    def compute_result(self):
        if not self.segments:
            return [], []

        # 生成事件点：(时间, 类型, 线段索引)
        events = []
        for idx, (start, end, _) in enumerate(self.segments):
            events.append((start, 'start', idx))
            events.append((end, 'end', idx))

        # 按时间排序事件点
        events.sort(key=lambda x: (x[0], x[1]))

        # 扫描线算法：维护当前活跃的线段
        active_segments = {}  # {线段索引: (start, end, height)}
        result = []
        rest = []
        prev_time = None

        for time, typ, idx in events:
            if prev_time is not None and time != prev_time:
                # 当前区间 [prev_time, time] 是否被至少一个线段完全覆盖？
                has_coverage = any(
                    seg_start <= prev_time and seg_end >= time
                    for seg_start, seg_end, _ in active_segments.values()
                )
                if has_coverage:
                    # 收集所有重叠线段的高度（去重后排序）
                    heights = sorted({h for _, _, h in active_segments.values()})
                    result.append((prev_time, time, heights))
                else:
                    rest.append((prev_time, time))

            if typ == 'start':
                active_segments[idx] = self.segments[idx]
            else:
                active_segments.pop(idx, None)
            prev_time = time

        return result, rest

# 示例用法
if __name__ == "__main__":
    structure = SegmentStructure()
    structure.add_segment(1, 5, 2)   # 长线段A
    structure.add_segment(2, 3, 3)   # 短线段B
    structure.add_segment(4, 6, 4)   # 长线段C

    result, rest = structure.compute_result()
    for interval in result:
        print(f"Start: {interval[0]}, End: {interval[1]}, Heights: {interval[2]}")
    for seg in rest:
        print(f"Start: {seg[0]}, End: {seg[1]}")