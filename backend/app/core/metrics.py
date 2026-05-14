from prometheus_client import Counter, Gauge, Histogram

anomalies_detected_total = Counter("anomalies_detected_total", "Total anomalies detected")
active_alerts_gauge = Gauge("active_alerts_gauge", "Current active alerts")
model_inference_latency_seconds = Histogram(
    "model_inference_latency_seconds", "Model inference latency in seconds"
)
