from typing import Any, Coroutine, TypeVar
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

