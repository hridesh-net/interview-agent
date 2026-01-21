import asyncio

# Global async queue
frame_queue: asyncio.Queue = asyncio.Queue(maxsize=128)

async def push_frame(frame, meta: dict):
    await frame_queue.put((frame, meta))

async def pop_frame():
    return await frame_queue.get()