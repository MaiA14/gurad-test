from typing import Dict, Any, List

class MetricService:
    _data = {
        'request_count': 0,
        'error_count': 0,
        'incoming_bytes': 0,
        'outgoing_bytes': 0,
        'response_times': []  # type: List[float]
    }

    @staticmethod
    def increment_request_count() -> None:
        MetricService._data['request_count'] += 1

    @staticmethod
    def increment_error_count() -> None:
        MetricService._data['error_count'] += 1

    @staticmethod
    def add_incoming_bytes(bytes_count: int) -> None:
        MetricService._data['incoming_bytes'] += bytes_count

    @staticmethod
    def add_outgoing_bytes(bytes_count: int) -> None:
        MetricService._data['outgoing_bytes'] += bytes_count

    @staticmethod
    def add_response_time(response_time: float) -> None:
        MetricService._data['response_times'].append(response_time)
    
    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        response_times = MetricService._data.get('response_times', [])

        if len(response_times) > 0:
            total_response_time = sum(response_times)
            count = len(response_times)
            average_response_time = total_response_time / count
        else:
            average_response_time = 0

        return {
            'request_count': MetricService._data['request_count'],
            'error_count': MetricService._data['error_count'],
            'incoming_bytes': MetricService._data['incoming_bytes'],
            'outgoing_bytes': MetricService._data['outgoing_bytes'],
            'average_response_time': average_response_time
        }