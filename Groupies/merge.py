import bisect

class SegmentStructure:
    def __init__(self):
        self.segments = []

    def add_segment(self, start, end, height):
        self.segments.append((start, end, height))

    def compute_result(self):
        # 收集所有点
        points = set()
        for seg in self.segments:
            points.add(seg[0])
            points.add(seg[1])
        if not points:
            return []
        points = sorted(points)
        n = len(points)
        if n < 2:
            return []
        # 生成区间列表
        intervals = [(points[i], points[i + 1]) for i in range(n - 1)]
        m = len(intervals)
        # 初始化高度集合
        heights = [set() for _ in range(m)]

        # 处理每个线段
        for seg in self.segments:
            start, end, h = seg
            # 计算i_min
            pos_start = bisect.bisect_right(points, start)
            i_min = pos_start - 1
            if i_min < 0:
                i_min = 0
            # 计算i_max
            pos_end = bisect.bisect_left(points, end)
            i_max = pos_end - 1
            # 确保i_max不超过区间的最大索引
            if i_max >= m:
                i_max = m - 1
            # 遍历所有覆盖的区间
            for i in range(i_min, i_max + 1):
                heights[i].add(h)

        # 生成结果
        result = []
        for i in range(m):
            s, e = intervals[i]
            sorted_heights = sorted(heights[i])
            result.append((s, e, sorted_heights))
        return result


# 示例用法
if __name__ == "__main__":
    # 创建结构并添加线段
    structure = SegmentStructure()
    structure.add_segment(1, 3, 2)
    structure.add_segment(2, 5, 3)
    structure.add_segment(3, 7, 4)
    structure.add_segment(4, 9, 5)

    # 计算结果
    result = structure.compute_result()
    for interval in result:
        print(f"Start: {interval[0]}, End: {interval[1]}, Heights: {interval[2]}")