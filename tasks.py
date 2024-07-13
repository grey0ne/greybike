from typing import Any, Coroutine, TypeVar, Callable
from aiohttp import web
import asyncio
import logging

def _handle_task_result(task: asyncio.Task[Any]) -> None:
    # This is used to log exceptions in tasks immediately when they are raised.
    # https://quantlane.com/blog/ensure-asyncio-task-exceptions-get-logged/
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    except Exception:  # pylint: disable=broad-except
        logging.exception('Exception raised by task = %r', task)


TaskResult = TypeVar('TaskResult')

def create_task(
    coroutine: Coroutine[Any, Any, TaskResult],
) -> asyncio.Task[TaskResult]:
    task = asyncio.create_task(coroutine)
    task.add_done_callback(_handle_task_result)
    return task

def create_periodic_task(
    async_function: Callable[[web.Application], Coroutine[Any, Any, None]],
    app: web.Application,
    interval: float,
) -> asyncio.Task[None]:
    async def closure():
        while True:
            await async_function(app)
            await asyncio.sleep(interval)
    return create_task(closure())

