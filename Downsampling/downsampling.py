



def reduce_window(window:dict, row: dict):

    for key, value in row.items():

        if key == "timestamp":
            continue
        elif isinstance(value, (int, float)):
            if key not in window:
                window[key] = {
                    "sum": value,
                    "count": 1
                }
            else:
                window[key]["sum"] += value
                window[key]["count"] += 1
        else:
            window[key] = value
    
    return window

def init_window(row: dict):

    window = {}
    for key, value in row.items():

        if key == "timestamp":
            continue
        elif isinstance(value, (int, float)):
            window[key] = {
                "sum": value,
                "count": 1
            }
        else:
            window[key] = value

    return window


def aggregate_window(window: dict):
    result = {
        "timestamp": int(window["end"] * 1E6)
    }

    for key, value in window["value"].items():

        if "sum" in value:
            result[key] = value["sum"] / value["count"]
        else:
            result[key] = value

    return result