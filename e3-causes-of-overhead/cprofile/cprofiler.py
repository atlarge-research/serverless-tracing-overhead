import cProfile
import pstats
import time
from io import StringIO


# Convert pstats to microseconds
def f8(x):
    # ret = "%8.3f" % x
    # if ret != '   0.000':
    #     return ret
    return "%6d" % (x * 10000000)

pstats.f8 = f8


def filter_opentelemetry_stats(full_stats):
    otel_prefixes = [
        "opentelemetry.",
        "otlp_exporter.",
        "SimpleSpanProcessor.",
        "ConsoleSpanExporter.",
        "TracerProvider."
    ]

    # Filter out OpenTelemetry functions
    def filter_func(func_name):
        return not any(func_name.startswith(prefix) for prefix in otel_prefixes)

    # Create a new Stats object with filtered functions
    filtered_stats = pstats.Stats()
    filtered_stats.stream = full_stats.stream

    for func, (cc, nc, tt, ct, callers) in full_stats.stats.items():
        if filter_func(pstats.func_std_string(func)):
            filtered_stats.stats[func] = (cc, nc, tt, ct, callers)

    return filtered_stats


def profile_function(times_dict_list):
    def decorator(func):
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()

            profiler.disable()

            s = StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats()
            full_stats = s.getvalue()

            # Initialize the function times dictionary
            func_times = {
                "(configure_opentelemetry)": 0.0,
                "(task)": 0.0,
                "(end)": 0.0,
                "(start_span)": 0.0,
                "(workload)": 0.0
            }

            # Extract times for each function of interest
            for func_name in func_times.keys():
                for line in full_stats.split('\n'):
                    if func_name in line:
                        parts = line.split()
                        if len(parts) > 3:
                            try:
                                func_times[func_name] = float(parts[3]) / 1_000  # Cumulative time column
                            except ValueError:
                                continue

            # Rename the functions in func_times dictionary
            renamed_func_times = {
                "configuration": func_times.pop("(configure_opentelemetry)"),
                "task": func_times.pop("(task)"),
                "export": func_times.pop("(end)"),
                "instrumentation": func_times.pop("(start_span)"),
                "total": func_times.pop("(workload)")
            }

            # Append this run's function times to the list
            times_dict_list.append(renamed_func_times)

            return result

        return wrapper
    return decorator