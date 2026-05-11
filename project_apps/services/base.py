import requests
import logging
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

class BaseHTTPService:
    """
    A generalized HTTP wrapper for making API calls.
    """
    def __init__(
        self, 
        base_url: Optional[str] = None, 
        headers: Optional[Dict[str, str]] = None, 
        auth: Optional[Any] = None, 
        timeout: int = 30
    ):
        self.base_url = base_url
        self.headers = headers or {}
        self.auth = auth
        self.timeout = timeout
        self.session = requests.Session()

    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Any] = None, 
        json: Optional[Any] = None, 
        headers: Optional[Dict[str, str]] = None, 
        **kwargs
    ) -> requests.Response:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,
                auth=self.auth,
                timeout=self.timeout,
                **kwargs
            )
            # We don't call raise_for_status() here to allow the service layer 
            # to handle different status codes as needed.
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error occurred: {e}")
            raise e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise e

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)
