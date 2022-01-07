import asyncio
import logging
import os.path
from pathlib import Path

import aiofiles
from aiohttp import web
from parser import parser
from functools import partial

BYTES_PER_CHUNK = 500 * 1024


async def archivate(request, path_to_photos, delay=3):
    response = web.StreamResponse()
    arch_name = request.match_info['archive_hash']
    if not os.path.exists(os.path.join(path_to_photos, arch_name)):
        raise web.HTTPNotFound(text="Архив не существует или был удален")

    response.headers['Content-Type'] = "application/octet-stream"
    response.headers['Content-Disposition'] = f"attachment; " \
                                              f"filename={arch_name}.zip"

    await response.prepare(request)

    proc = await asyncio.create_subprocess_exec(
        "zip", "-r", "-", f"{arch_name}",
        cwd=f"./{path_to_photos}/",
        stdout=asyncio.subprocess.PIPE,
        preexec_fn=os.setsid
    )
    try:
        while not proc.stdout.at_eof():
            archive = await proc.stdout.read(BYTES_PER_CHUNK)
            await response.write(archive)
            logging.info(f"Sending archive named {arch_name} chunk...")
            await asyncio.sleep(delay)
    except asyncio.CancelledError as exc:
        proc.kill()
        logging.info("Download was interrupted")
        raise exc
    finally:
        await proc.communicate()

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def main():
    args = parser.parse_args()
    log, delay, path_to_photos = args.log, int(args.delay), args.path_to_photos

    if log:
        logging.basicConfig(level=logging.DEBUG)
    archive_handler = partial(archivate, delay=delay, path_to_photos=path_to_photos)
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive_handler),
    ])
    web.run_app(app)


if __name__ == '__main__':
    main()
