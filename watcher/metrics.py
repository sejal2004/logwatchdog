from prometheus_client import Counter, Gauge

# Total pods being watched (live value)
pods_watched = Gauge("logwatchdog_pods_watched", "Number of pods currently being watched")

# Total restarts triggered
restarts_total = Counter("logwatchdog_restarts_total", "Total number of pod restarts triggered")

# AI action classification count
ai_actions_total = Counter(
    "logwatchdog_ai_actions_total",
    "Total number of AI actions suggested",
    ["action"]
)

def inc_action(action):
    ai_actions_total.labels(action=action).inc()

def inc_restart():
    restarts_total.inc()

def set_pods_watched(count):
    pods_watched.set(count)
