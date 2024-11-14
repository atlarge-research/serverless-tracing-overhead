import cProfile
import pstats
import time
from io import StringIO
import os
from functools import wraps

PROFILE_DIR = "profiles"


# Convert pstats to microseconds
def f8(x):
    # ret = "%8.3f" % x
    # if ret != '   0.000':
    #     return ret
    return "%6d" % (x * 1_000_000)


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


def profile_function(times_dict_list, experiment_name, start_mode):
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

            # For debugging
            # print(full_stats)

            # Initialize the function times dictionary
            func_times = {
                "(configure_opentelemetry)": 0.0,
                "(task)": 0.0,
                "(end)": 0.0,
                "(start_span)": 0.0,
                "(workload)": 0.0,
                "(add_event)": 0.0,
                "(set_attribute)": 0.0,
                "(set_span_in_context)": 0.0
            }

            start_span_calls = 0  # Count of how many times start_span was called
            end_calls = 0  # Count of how many times end was called

            # Extract times for each function of interest
            for func_name in func_times.keys():
                for line in full_stats.split('\n'):
                    if func_name in line:
                        parts = line.split()
                        if len(parts) > 3:
                            try:
                                # Convert from microseconds to milliseconds
                                func_times[func_name] = float(parts[3]) / 1_000  # Cumulative time column

                                # If this is a "start_span" line, increment the counter
                                if func_name == "(start_span)":
                                    start_span_calls = int(parts[0])  # The number of calls is in the first column

                                # If this is an "end" line, increment the counter
                                if func_name == "(end)":
                                    end_calls = int(parts[0])  # The number of calls is in the first column
                            except ValueError:
                                continue

            # Calculate the adjusted time for the task function
            task_time_adjusted = func_times["(task)"] - (
                    func_times["(add_event)"] +
                    func_times["(set_attribute)"] +
                    func_times["(set_span_in_context)"]
            )

            # Deduct the time for n-1 start_span calls, only if more than 1 start_span was called
            if start_span_calls > 1:
                task_time_adjusted -= (start_span_calls - 1) * (func_times["(start_span)"] / start_span_calls)

            # Deduct the time for n-1 end calls, only if more than 1 end was called
            if end_calls > 1:
                task_time_adjusted -= (end_calls - 1) * (func_times["(end)"] / end_calls)

            # Calculate the total instrumentation time
            instrumentation_time = (
                    func_times.pop("(start_span)") +
                    func_times["(add_event)"] +
                    func_times["(set_attribute)"] +
                    func_times["(set_span_in_context)"]
            )

            # Rename the functions in func_times dictionary and add the adjusted times
            renamed_func_times = {
                "configuration": func_times.pop("(configure_opentelemetry)"),
                "task": task_time_adjusted,  # Adjusted task time
                "export": func_times.pop("(end)"),
                "instrumentation": instrumentation_time,  # Total instrumentation time
                "total": func_times.pop("(workload)")
            }

            renamed_func_times = normalize_percentages(renamed_func_times)

            # Append this run's function times to the list
            times_dict_list.append(renamed_func_times)

            return result

        return wrapper

    return decorator


def profile_route(profiling_data_list, endpoint_name=""):
    def decorator(func2):
        @wraps(func2)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            start_time = time.time()
            result = func2(*args, **kwargs)
            end_time = time.time()

            profiler.disable()

            # Capture the profiling data
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.print_stats()

            full_stats = s.getvalue()
            # print(full_stats)

            # Define the categories for OpenTelemetry-related functions
            config_functions = ['configure_opentelemetry', 'get_tracer']
            instrumentation_functions = ['start_span', 'set_attribute']
            exporting_functions = ['end']
            total_time_function = endpoint_name

            # Initialize the time tracking
            time_spent = {
                'configuration': 0,
                'task': 0,
                'export': 0,
                'instrumentation': 0,
                'total': 0,
            }

            # Analyze the stats
            for func, stat in ps.stats.items():
                filename, line, funcname = func

                # Convert from seconds to milliseconds
                tottime = stat[2] * 1_000
                cumtime = stat[3] * 1_000

                # Determine the category
                if any(fn == funcname for fn in config_functions):
                    # The get_tracer line
                    if line == 490:
                        time_spent['configuration'] += cumtime
                elif any(fn == funcname for fn in instrumentation_functions):
                    time_spent['instrumentation'] += cumtime
                elif any(fn == funcname for fn in exporting_functions):
                    time_spent['export'] += cumtime
                elif funcname == total_time_function:
                    time_spent['total'] = cumtime

                # Handle special case for specific functions
                elif 'opentelemetry/instrumentation/sqlalchemy' in filename:
                    time_spent['instrumentation'] += tottime
                elif funcname == 'use_span':
                    time_spent['instrumentation'] += tottime

            # Calculate task time as total minus other categories
            time_spent['task'] = (
                    time_spent['total'] -
                    (time_spent['configuration'] +
                     time_spent['instrumentation'] +
                     time_spent['export'])
            )

            # Append the results to the profiling data list
            profiling_data_list.append(time_spent)

            return result

        return wrapper

    return decorator


def normalize_percentages(func_times):
    total_time = func_times["total"]

    # Calculate the sum of the parts (configuration, task, export, instrumentation)
    sum_of_parts = func_times["configuration"] + func_times["task"] + func_times["export"] + func_times[
        "instrumentation"]

    # Check if the sum of the parts matches the total
    if sum_of_parts != total_time:
        # Calculate the difference
        diff = total_time - sum_of_parts

        # Add the difference to the task time to ensure the total matches
        func_times["task"] += diff

    return func_times