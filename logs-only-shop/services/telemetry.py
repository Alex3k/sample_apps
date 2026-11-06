import os

from opentelemetry import metrics, trace
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

_providers = []


def _configured(signal):
    if os.environ.get("OTEL_SDK_DISABLED", "").lower() == "true":
        return False
    return bool(os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or os.environ.get(f"OTEL_EXPORTER_OTLP_{signal}_ENDPOINT"))


def configure():
    RequestsInstrumentor().instrument()
    PsycopgInstrumentor().instrument()
    if os.environ.get("SERVICE"):
        os.environ.setdefault("OTEL_SERVICE_NAME", os.environ["SERVICE"])

    from opentelemetry.sdk.resources import Resource

    resource = Resource.create()
    if _configured("TRACES"):
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(tracer_provider)
        _providers.append(tracer_provider)
    if _configured("METRICS"):
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

        meter_provider = MeterProvider(resource=resource, metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())])
        metrics.set_meter_provider(meter_provider)
        _providers.append(meter_provider)


def shutdown():
    for provider in _providers:
        provider.shutdown()
