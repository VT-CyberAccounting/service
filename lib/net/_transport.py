from asyncio import Lock, sleep
from time import monotonic as time
from httpx import AsyncHTTPTransport, Request, Response

class ThrottledTransport(AsyncHTTPTransport):
    
    def __init__(self, delay: float, **kwargs):
        super().__init__(**kwargs)
        if delay <= 0:
            raise ValueError("Delay must be positive.")
        self._delay = delay
        self._lock = Lock()
        self._lreq_time = 0

    async def handle_async_request(
            self, request: Request
    ) -> Response:
        async with self._lock:
            time_delta = time() - self._lreq_time
            if time_delta < self._delay:
                sleep_duration = self._delay - time_delta
                await sleep(sleep_duration)
            response = await super().handle_async_request(request)
            self._lreq_time = time()
            return response