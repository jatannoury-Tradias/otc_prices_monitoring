"""
State of the art websocket connector. 23/10/2022
"""
import asyncio
import logging
import socket
import orjson
import websockets
import platform

from typing import Union, Optional, Callable

MAX_QUEUE_CHECK_TIME = 5
QUEUE_CHECK_TIME = 0.5

my_logger = logging.getLogger(__name__)

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class WebsocketHelper:
    CLOSE_TIMEOUT = 0.5

    def __init__(self,
                 url: str = None,
                 name: str = "Websocket Helper",
                 port=None):
        """

        :param url:
        :param name:
        """

        self.uri = url + f':{port}' if port else url
        self.name = name

        # These variables can only be set when you are in an event loop.
        self.force_websocket_close: Optional[asyncio.Event] = None
        self.receiver_queue: Optional[asyncio.Queue] = None
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.websocket_open: Optional[asyncio.Event] = None

    async def keep_open(self,
                        get_extra_headers: Callable = lambda: {},
                        print_response: bool = False,
                        extra_messages=None):
        """
        Keep connection open in case of disconnects or weird stuff.

        :param get_extra_headers: function to get headers.
        :param print_response: Prints the received response.
        :param extra_messages: Connection message to be sent when disconnect occurs.
        :return:
        """

        self.force_websocket_close = asyncio.Event()
        self.websocket_open = asyncio.Event()
        self.receiver_queue = asyncio.Queue()
        retry = 0
        initial_send_task = None
        gather_object = None

        if extra_messages is None:
            extra_messages = {}

        my_logger.debug(f"{self.name}: Starting websocket connection")
        my_logger.debug(f"{self.name}: Started receiver task")

        while not self.force_websocket_close.is_set():
            try:
                async with websockets.connect(self.uri,
                                              close_timeout=self.CLOSE_TIMEOUT,
                                              extra_headers=get_extra_headers()
                                              ) as ws:
                    self.websocket_open.set()
                    self.ws = ws
                    retry = 0

                    my_logger.debug("Opened websocket")
                    if extra_messages:
                        initial_send_task = asyncio.create_task(self.sender(extra_messages, print_it=print_response))
                        await initial_send_task
                    try:
                        gather_object = asyncio.gather(
                            self.force_websocket_close.wait(),
                            self._receiver(print_it=print_response))
                        await gather_object
                    except asyncio.CancelledError:
                        my_logger.exception(f"{self.name}: Cancelled error")
                        self.force_websocket_close.set()
                    except websockets.ConnectionClosed:
                        my_logger.exception(f"{self.name}: Connection closed")
                        self.websocket_open.clear()
            except ConnectionRefusedError:
                my_logger.error(f"{self.name}: Connection refused")
            except socket.gaierror as e:
                my_logger.error(f"{self.name}: Connection could not be established due to: {e}")
            except websockets.InvalidStatusCode:
                my_logger.exception(f"{self.name}: Invalid status code")
            retry = retry + 1
            my_logger.warning(f"Please wait {retry} second, websocket problem ... ")
            if initial_send_task:
                initial_send_task.cancel()
            if gather_object:
                gather_object.cancel()
            await asyncio.sleep(retry)

        my_logger.warning(f"{self.name}Escaped While Loop in 'keep_open'")

        # manual garbage collection
        self.force_websocket_close = None
        self.websocket_open = None
        self.ws = None

        try:
            my_logger.warning(f"{self.name}: Checking if receiver Queue is empty ...")
            await asyncio.wait_for(self._wait_for_empty_queue(), MAX_QUEUE_CHECK_TIME)
        except asyncio.TimeoutError:
            my_logger.warning(f"{self.name}: Queue not empty when destroying queue.")
        self.receiver_queue = None
        print(asyncio.all_tasks())
        return

    async def sender(self,
                     message: Union[dict, str, list],
                     expect_json: bool = True,
                     print_it: bool = False) -> None:
        """
        Sender that allows JSON & multiple messages. Not a scheduled task, can be called when needed.

        :param message: Message to be sent.
        :param expect_json: If True, it will try to convert the message to JSON.
        :param print_it: Prints the received response.
        :return:
        """

        if isinstance(message, str):
            message = [message]
        elif isinstance(message, dict):
            message = [message]

        if not isinstance(message, list):
            raise TypeError("Message must be a list, string or dict.")

        if expect_json:
            message = [self._json_encoder(m) for m in message]

        for m in message:
            await self.websocket_open.wait()
            await self.ws.send(m)
            if print_it:
                print(f"{self.name} sent: {m}")

    async def close_websocket(self, close_time: int = 0):
        """
        Closes the websocket connection.
        :param close_time: Timeout before closing the connection
        :return:
        """
        my_logger.debug(f"{self.name} function 'close_in' starts")
        await asyncio.sleep(close_time)
        my_logger.warning(f"{self.name} function 'close_in' ends")
        self.force_websocket_close.set()

    async def _receiver(self,
                        expect_json: bool = True,
                        print_it: bool = True):
        """
        Standard awaitable to just receive the output.

        :return:
        """
        while not self.force_websocket_close.is_set():
            await self.websocket_open.wait()
            receive_msg = await self.ws.recv()
            response = self._json_decoder(expect_json=expect_json, message=receive_msg)

            await self.receiver_queue.put(response)
            if print_it:
                print(f"{self.name} received: {response}")
        print("EXITED RECEIVER")

    async def _wait_for_empty_queue(self):
        while not self.receiver_queue.empty():
            await asyncio.sleep(QUEUE_CHECK_TIME)
        return

    @staticmethod
    def _json_decoder(expect_json: bool, message: str) -> Union[dict, list, str]:
        """
        Change JSON string into python dict / list of dict
        :return:
        """

        if expect_json:
            try:
                return orjson.loads(message)
            except orjson.JSONDecodeError:
                my_logger.warning(f"Received message: {message}\nare you receiving JSON?")
                return [{"error": "JSONDecodeError",
                         "message": message}]
        else:
            return message

    @staticmethod
    def _json_encoder(message: dict) -> str:
        """
        change python dict into JSON string

        :param message:
        :return:
        """
        if isinstance(message, dict):
            return orjson.dumps(message).decode()
        else:
            raise TypeError(f"Message is not a dict. Message: {message}")


if __name__ == "__main__":
    pass
