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
                "(set_attribute)": 0.0
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

            # Calculate the adjusted time for the task function
            task_time_adjusted = func_times["(task)"] - (func_times["(add_event)"] + func_times["(set_attribute)"])

            # Rename the functions in func_times dictionary and add the adjusted times
            renamed_func_times = {
                "configuration": func_times.pop("(configure_opentelemetry)"),
                "task": task_time_adjusted,  # Adjusted task time
                "export": func_times.pop("(end)"),
                "instrumentation": func_times.pop("(start_span)") + func_times["(add_event)"] + func_times["(set_attribute)"],  # Add add_event and set_attribute times
                "total": func_times.pop("(workload)")
            }

            # Append this run's function times to the list
            times_dict_list.append(renamed_func_times)

            if not os.path.exists(PROFILE_DIR):
                os.makedirs(PROFILE_DIR)
            profiler.dump_stats(f"{PROFILE_DIR}/workload-{experiment_name}-{start_mode}.prof")

            return result

        return wrapper
    return decorator


def profile_route(profiling_data_list, endpoint_name=""):
    def decorator(func2):
        @wraps(func2)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            result = func2(*args, **kwargs)
            profiler.disable()

            # Capture the profiling data
            s = StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats()

            full_stats = s.getvalue()
            print(full_stats)

            # Define the categories for OpenTelemetry-related functions
            config_functions = ['configure_opentelemetry']
            instrumentation_functions = ['opentelemetry.instrumentation']
            exporting_functions = ['opentelemetry.exporter']
            total_time_functions = ['updates', 'db']

            # Initialize the time tracking
            total_time = 0
            time_spent = {
                'Configuration': 0,
                'Instrumentation': 0,
                'Exporting': 0,
                'Workload': 0,
                'Total': 0,
            }

            # Dictionary to store function relationships
            call_graph = {}

            # Analyze the stats
            for func, stat in ps.stats.items():
                filename, line, funcname = func
                time_spent_fn = stat[3]  # cumtime (total time including subcalls)

                # Determine the category
                if any(fn in funcname for fn in config_functions):
                    time_spent['Configuration'] += time_spent_fn
                elif any(fn in funcname for fn in instrumentation_functions):
                    time_spent['Instrumentation'] += time_spent_fn
                elif any(fn in funcname for fn in exporting_functions):
                    time_spent['Exporting'] += time_spent_fn
                elif any(fn in funcname for fn in total_time_functions):
                    time_spent['Total'] += time_spent_fn
                else:
                    time_spent['Workload'] += time_spent_fn

                # Record the call hierarchy
                if stat[4]:  # Check if there are subcalls
                    for subfunc in stat[4]:
                        if func not in call_graph:
                            call_graph[func] = []
                        call_graph[func].append(subfunc)

            # Process the call graph to accumulate times for OpenTelemetry
            for parent, children in call_graph.items():
                _, _, parent_funcname = parent
                if any(fn in parent_funcname for fn in
                       config_functions + instrumentation_functions + exporting_functions):
                    for child in children:
                        child_cumtime = ps.stats[child][3]
                        if any(fn in child[2] for fn in config_functions):
                            time_spent['Configuration'] += child_cumtime
                        elif any(fn in child[2] for fn in instrumentation_functions):
                            time_spent['Instrumentation'] += child_cumtime
                        elif any(fn in child[2] for fn in exporting_functions):
                            time_spent['Exporting'] += child_cumtime

            # Append the results to the profiling data list
            profiling_data_list.append({
                'endpoint': endpoint_name,
                'total_time': time_spent['Total'],
                'time_spent': time_spent
            })

            # Save the profiling data to a .prof file for further analysis if needed
            profiler.dump_stats(f"{endpoint_name}-request-based.prof")

            return result

        return wrapper

    return decorator