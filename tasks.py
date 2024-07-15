from typing import Any, Coroutine, TypeVar, Callable
from aiohttp import web
from utils import TaskData
import asyncio
import logging

logger = logging.getLogger('greybike')

def _handle_task_result(task: asyncio.Task[Any]) -> None:
    # This is used to log exceptions in tasks immediately when they are raised.
    # https://quantlane.com/blog/ensure-asyncio-task-exceptions-get-logged/
    try:
        task.result()
    except asyncio.CancelledError:
        logger.info(f'Task "{task.get_name()}" was cancelled')

    except Exception:  # pylint: disable=broad-except
        logger.error(f'Exception raised by task {task}')


TaskResult = TypeVar('TaskResult')

def create_task(
    coroutine: Coroutine[Any, Any, TaskResult],
    name: str,
) -> asyncio.Task[TaskResult]:
    task = asyncio.create_task(coroutine, name=name)
    task.add_done_callback(_handle_task_result)
    return task

def create_periodic_task(
    async_function: Callable[[web.Application], Coroutine[Any, Any, None]],
    app: web.Application,
    name: str,
    interval: float,
) -> TaskData:
    async def closure():
        while True:
            await async_function(app)
            await asyncio.sleep(interval)
    logger.info(f"Creating task {name} with interval {interval}")
    return TaskData(
        name=name,
        task=create_task(closure(), name=name),
        interval=interval
    )

