# 1. Instrumented with configuration only
# 2. Instrumented with configuration + instrumentation
# 3. Instrumented with instrumentation only
# 4. Instrumented with instrumentation + export
# 5. Instrumented with configuration + instrumentation + export

## Cant do export only --> What to export?
### Can test without any instrumentation though but still need to start span?

## Can do without configuration by configuring first

def configuration():
    return

def configration_and_instrumentation():
    return

def instrumentation():
    return

def instrumentation_export():
    return
