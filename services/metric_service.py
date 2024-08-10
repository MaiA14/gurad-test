from typing import Dict, Any

class MetricService:
    _data = {
        'request_count': 0,
        'error_count': 0,
        'incoming_bytes': 0,
        'outgoing_bytes': 0,
        'response_times': []
    }

    @classmethod
    def increment_request_count(cls) -> None:
        cls._data['request_count'] += 1

    @classmethod
    def increment_error_count(cls) -> None:
        cls._data['error_count'] += 1

    @classmethod
    def add_incoming_bytes(cls, bytes_count: int) -> None:
        cls._data['incoming_bytes'] += bytes_count

    @classmethod
    def add_outgoing_bytes(cls, bytes_count: int) -> None:
        cls._data['outgoing_bytes'] += bytes_count

    @classmethod
    def add_response_time(cls, response_time: float) -> None:
        cls._data['response_times'].append(response_time)

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        response_times = cls._data.get('response_times', [])
        if response_times:
            average_response_time = sum(response_times) / len(response_times)
        else:
            average_response_time = 0

        return {
            'request_count': cls._data['request_count'],
            'error_count': cls._data['error_count'],
            'incoming_bytes': cls._data['incoming_bytes'],
            'outgoing_bytes': cls._data['outgoing_bytes'],
            'average_response_time': average_response_time
        }