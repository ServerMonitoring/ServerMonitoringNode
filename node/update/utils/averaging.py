from collections import defaultdict
from copy import deepcopy


def average_metric_list(metrics_list, round_digits=3):
    if not metrics_list:
        return {}

    def recursive_average(values):
        if all(isinstance(v, (int, float)) for v in values):
            return round(sum(values) / len(values),round_digits)
        elif all(isinstance(v, dict) for v in values):
            merged = defaultdict(list)
            for d in values:
                for k, v in d.items():
                    merged[k].append(v)
            return {k: recursive_average(v) for k, v in merged.items()}
        elif all(isinstance(v, list) for v in values):
            # Для списков - обрабатываем по индексам
            transposed = defaultdict(list)
            for l in values:
                for idx, item in enumerate(l):
                    transposed[idx].append(item)
            return [recursive_average(items) for idx, items in sorted(transposed.items())]
        else:
            # Если не можем усреднить, берём первое значение (например, строки и т.д.)
            return deepcopy(values[0])

    merged = defaultdict(list)
    for entry in metrics_list:
        for k, v in entry.items():
            merged[k].append(v)

    averaged_result = {k: recursive_average(v) for k, v in merged.items()}
    return averaged_result


if __name__ == "__main__":
    pass
