
from fastapi import FastAPI, Request
import uvicorn
from fastapi_proxy import settings
import mock
from requests.exceptions import HTTPError
import requests



app = FastAPI()


def telegram_query(query):

    url = "https://www.telegram.com"
    params = {'q': query}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.content


def _mock_response(
        self,
        status=200,
        content="CONTENT",
        json_data=None,
        raise_for_status=None):

    mock_resp = mock.Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content
    # add json data if provided
    if json_data:
        mock_resp.json = mock.Mock(
            return_value=json_data
        )
    return mock_resp


@mock.patch('requests.get')
def test_telegram_query(self, mock_get):
    """test google query method"""
    mock_resp = self._mock_response(content="ELEPHANTS")
    mock_get.return_value = mock_resp

    result = telegram_query('elephants')
    self.assertEqual(result, 'ELEPHANTS')
    self.assertTrue(mock_resp.raise_for_status.called)

@mock.patch('requests.get')
def test_failed_query(self, mock_get):
    """test case where google is down"""
    mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("google is down"))
    mock_get.return_value = mock_resp
    self.assertRaises(HTTPError, telegram_query, 'elephants')


@app.post(f"/bot{settings.tg_token}/{{endpoint_method}}")
async def give_response(endpoint_method: str, request: Request):
    return test_telegram_query(request)


@app.get("/test_get")
async def test_get(request: Request):
    return test_telegram_query(request)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
