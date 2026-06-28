import time
import uuid
import logging
from contextvars import ContextVar
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to store the trace ID
trace_id_contextvar: ContextVar[str] = ContextVar("trace_id", default="")

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        token = trace_id_contextvar.set(trace_id)
        
        start_time = time.time()
        
        # Add trace ID to request state so it can be accessed elsewhere if needed
        request.state.trace_id = trace_id
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = "{0:.2f}".format(process_time)
            
            logger.info(
                f"method={request.method} path={request.url.path} status={response.status_code} duration={formatted_process_time}ms",
                extra={"trace_id": trace_id}
            )
            
            # Add trace ID to response headers
            response.headers["X-Trace-ID"] = trace_id
            return response
        finally:
            trace_id_contextvar.reset(token)

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id_contextvar.get()
        return True

def setup_logging():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [traceId=%(trace_id)s] - %(message)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
