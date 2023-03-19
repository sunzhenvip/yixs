import asyncio
import aiohttp
import time
import blog

# 信号量控制并发数量
semaphore = asyncio.Semaphore(50)


# 协程函数
async def async_craw(url):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.text()
                # await asyncio.sleep(5)  # 等待五秒
                print(f"craw url:{url}, {len(result)}")


def start_task():
    start = time.time()

    loop = asyncio.get_event_loop()

    tasks = [loop.create_task(async_craw(url)) for url in blog.urls]  # task任务

    loop.run_until_complete(asyncio.wait(tasks))  # 等待所有的任务完成

    end = time.time()
    print("协程 async cost:", end - start, "seconds")


if __name__ == "__main__":
    start_task()
