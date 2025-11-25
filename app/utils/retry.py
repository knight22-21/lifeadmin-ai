import time
import functools

def retry(max_attempts=3, delay=2, backoff=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e

                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper
    return decorator
