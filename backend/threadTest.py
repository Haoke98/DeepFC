import time
import concurrent.futures

def worker(id):
    time.sleep(2)
    print(f'this is worker[{id}]')

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executer:
        futs = [executer.submit(worker,id) for id in range(0,20)]
        print("this is result:",[fut.result() for fut in concurrent.futures.as_completed(futs)])