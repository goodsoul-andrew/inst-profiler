import json
import math


class StatAnalyzer:
    def __init__(self, filename="profiler_stat.json"):
        self.data = None
        self.rows = []
        self.filename = filename

    def open_json_stat(self, filename="profiler_stat.json"):
        with open(filename) as f:
            self.data = json.load(f)

    def make_stat_table(self):
        self.rows = []
        for func_name, stats in self.data.items():
            ncalls = stats["ncalls"]
            tottime = stats["tottime"]
            cumtime = stats["cumtime"]
            avg_time = cumtime / ncalls if ncalls else 0
            self.rows.append({
                "function": func_name,
                "ncalls": ncalls,
                "tottime": tottime,
                "cumtime": cumtime,
                "avg_call": avg_time
            })

        return self.rows

    def top_slowest_tottime(self, top=None):
        self.open_json_stat(self.filename)
        self.make_stat_table()
        if not top:
            top = self.get_top_number()
        rows_tot = self.rows
        rows_tot.sort(key=lambda x: x["tottime"], reverse=True)
        return [
            {"function": row["function"], "tottime": row["tottime"]}
            for row in rows_tot[:top]
        ]

    def top_slowest_cumtime(self, top=None):
        self.open_json_stat("stats.json")
        self.make_stat_table()
        if not top:
            top = self.get_top_number()
        rows_cum = self.rows
        rows_cum.sort(key=lambda x: x["cumtime"], reverse=True)
        return [
            {"function": row["function"], "cumtime": row["cumtime"]}
            for row in rows_cum[:top]
        ]

    def get_top_number(self):
        if len(self.rows) < 3:
            return 1
        elif 3 < len(self.rows) < 10:
            return 3
        elif 10 < len(self.rows) < 50:
            return 10
        elif 50 < len(self.rows) < 100:
            return 20
        else:
            return math.ceil(len(self.rows) * 0.2)