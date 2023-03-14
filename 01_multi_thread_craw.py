import time

import blog
import threading


# 单线程版本
def single_thread():
    for url in blog.urls:
        blog.craw(url)


# 多线程版本
def multi_thread():
    print("multi_thread begin")
    threads = []
    for url in blog.urls:
        threads.append(
            threading.Thread(target=blog.craw, args=(url,))
        )

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("multi_thread end")


if __name__ == "__main__":
    start = time.time()
    single_thread()
    end = time.time()
    print("single thread cost:", end - start, "seconds")

    start = time.time()
    multi_thread()
    end = time.time()

    print("multi thread cost:", end - start, "seconds")
    pass
