import logging
import sys
from pythonjsonlogger import json

def setup_logging(trace_id: str = None):
    handler = logging.StreamHandler(sys.stdout)
    
    # Custom formatter to include trace_id
    format_str = '%(asctime)s %(levelname)s %(name)s %(message)s'
    if trace_id:
        format_str += f' %(trace_id)s'
        
    formatter = json.JsonFormatter(format_str)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicate logs
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
        
    root_logger.addHandler(handler)
    
    # Add trace_id to all logs if provided
    if trace_id:
        old_factory = logging.getLogRecordFactory()
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.trace_id = trace_id
            return record
        logging.setLogRecordFactory(record_factory)
