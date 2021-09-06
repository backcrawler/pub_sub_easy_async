1. Async Pub/Sub pattern

1.1 No side-packages needed

1.2 Python 3.7 required

2. Example of usage:

```python
import asyncio
import time
from pub_sub_easy_async import Observable, Observer

observable = Observable()
observer = Observer()


async def success_callback():
    await asyncio.sleep(1)  # some io nonblocking operation
    print('Success')
    

async def info_callback():
    start = time.time()
    await asyncio.sleep(1)  # some io nonblocking operation
    end = round(time.time()-start, 3)
    print(f'Took {end} sec for operation')    
    

async def main():
    # sub
    observer.listen_to(observable, 'click', success_callback)
    observer.listen_to(observable, 'click', info_callback)
    # emit event
    await observable.emit('click')
    
asyncio.run(main())
```