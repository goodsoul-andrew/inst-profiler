import json


class StatAnalyzer:
    def __init__(self):
        self.data = None
        self.rows = []

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

    def top_slowest_tottime(self, top):
        self.open_json_stat("stats.json")
        self.make_stat_table()
        rows_tot = self.rows
        rows_tot.sort(key=lambda x: x["tottime"])
        return [
            {"function": row["function"], "tottime": row["tottime"]}
            for row in rows_tot[:top]
        ]

    def top_slowest_cumtime(self, top):
        self.open_json_stat("stats.json")
        self.make_stat_table()
        rows_cum = self.rows
        rows_cum.sort(key=lambda x: x["cumtime"])
        return [
            {"function": row["function"], "cumtime": row["cumtime"]}
            for row in rows_cum[:top]
        ]
