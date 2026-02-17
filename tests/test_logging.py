import logging
import json
import io
from digital_alfred.infrastructure.logging import setup_logging

def test_json_logging_with_trace_id():
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    
    # We need to manually set up a logger for testing to capture output
    from pythonjsonlogger import json as json_logger
    formatter = json_logger.JsonFormatter('%(message)s %(trace_id)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("test_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Setup the factory
    setup_logging(trace_id="test-trace-123")
    
    logger.info("Test message", extra={"key": "value"})
    
    output = log_capture.getvalue()
    log_data = json.loads(output)
    
    assert log_data["message"] == "Test message"
    assert log_data["trace_id"] == "test-trace-123"
    assert log_data["key"] == "value"
