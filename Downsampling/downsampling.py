



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
