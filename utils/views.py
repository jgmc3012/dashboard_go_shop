from django.apps import apps

from collections import defaultdict
import asyncio
import logging
import subprocess
import re
import itertools

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class AppLoop(metaclass=Singleton):
    event_loop = None

    def __init__(self):
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # enable uvloop
            logging.info("USANDO uvloop :D")
        except Exception as e:
            logging.warn(f"Error ({e}) uvloop no soportado :'( ")
        self.event_loop = asyncio.get_event_loop()

    def __del__(self):
        if not self.event_loop.is_closed():
            logging.info(dir(self.event_loop))
            self.event_loop.close()

    def get_loop(self):
        return self.event_loop

class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self._update_queues = defaultdict(list)
        self._update_fields = defaultdict(set)
        self.chunk_size = chunk_size

    def _commit_create(self, model_class):
        model_key = model_class._meta.label
        logging.info(f'Insertando {len(self._create_queues[model_key])} registros')
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def _commit_update(self, model_class):
        model_key = model_class._meta.label
        logging.info(f'Actualizando {len(self._update_queues[model_key])} registros')
        model_class.objects.bulk_update(
            self._update_queues[model_key],
            self._update_fields[model_key]
        )
        self._update_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit_create(model_class)

    def update(self, obj, fields:set):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._update_queues[model_key].append(obj)
        self._update_fields[model_key] |= fields
        if len(self._update_queues[model_key]) >= self.chunk_size:
            self._commit_update(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit_create(apps.get_model(model_name))

        for model_name, objs in self._update_queues.items():
            if len(objs) > 0:
                self._commit_update(apps.get_model(model_name))


async def running_semaphore(sem, coro, name, len_coros, print_every_percent=10):
    global total_process
    async with sem:
        res = await coro
        total_process[name] = total_process.get(name, 0) + 1

        if print_every_percent:
            current_percent = round(total_process.get(name, 0) / len_coros * 100, 4)
            if (
                current_percent
                and (current_percent % print_every_percent) == 0
                and len_coros >= 10
                and total_process.get(name, 0) != len_coros
            ):
                logging.info(
                    f"{name}, processed courotines {total_process[name]}: {current_percent}%"
                )
        if total_process.get(name, 0) == len_coros:
            logging.info(
                f"{name}, processed courotines {total_process[name]}: finished"
            )
            del total_process[name]
        return res

async def get_with_semaphore(
    coros:list, count_sem=100, name="my_semaphore", print_every_percent=10
):
    if coros:
        global total_process
        name = name.replace(" ", "_") + f"_{count_sem}"
        if "total_process" not in globals():
            total_process = {}
        len_coros = len(coros)
        sem = asyncio.Semaphore(count_sem)
        return await asyncio.gather(
            *[
                running_semaphore(sem, coro, name, len_coros, print_every_percent)
                for coro in coros
            ]
        )

class WebClient(metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        self.all_sessions = None
        self.lock = asyncio.Lock()
        # faster
        # http://azenv.net/
        # http://httpheader.net/azenv.php
        # http://proxyjudge.us/azenv.php
        # http://www.proxyfire.net/fastenv

        # medium
        # http://httpbin.org/get?show_env
        # http://www.sbjudge3.com/azenv.php
        # https://httpbin.org/get?show_env

        # > 0.2 sec
        # http://www.proxy-listen.de/azenv.php
        # https://www.proxy-listen.de/azenv.php
        # http://www.sbjudge2.com/azenv.php
        # http://www.proxyjudge.info/azenv.php

        # ?
        # https://api.ipify.org?format=json
        # http://ip-api.com/json
        # http://httpbin.org/ip

        self.url_judges = ("http://azenv.net/", "http://httpheader.net/azenv.php")

    async def internet_check(self, session, skip=False):
        if skip:
            public_ip = session._connector._local_addr[0]
            self.ip_publics.append(public_ip)
            return session
        for url_judge in self.url_judges:
            async with session.get(url_judge, timeout=20) as resp:
                if resp:
                    resp = await resp.text()
                    public_ip = re.findall(r"\d+\.\d+\.\d+\.\d+", resp)

                    if public_ip not in self.ip_publics:
                        self.ip_publics.append(public_ip)
                        return session
            logging.warn(
                f"internet_check error con: url_judge: {url_judge}, {session._connector._local_addr[0]}"
            )

        await session.close()
        return

    async def starts(self):
        try:
            cmd = r"ip -o -4 addr show|grep ' en\| eth\| wl'|awk '{print $4}'|cut -d/ -f1"  # deja solo las redes : "enp|eth" sin vpn sin docker
            ps = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            ips = ps.communicate()[0].decode().strip().split()
        except Exception as e:  # si es windows
            logging.warn(f"ERROR. {e}, is windows?")
            ips = ["0.0.0.0"]
        if not ips:
            raise Exception("no hay ips de salida disponibles")

        self.sessions = []
        self.ip_publics = []
        coros = []
        for ip in ips:
            conn = aiohttp.TCPConnector(
                local_addr=(ip, 0), limit=300, loop=AppLoop().get_loop()
            )
            session = AutoRetrySession(
                connector=conn,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible MSIE 9.0 Windows NT 6.1 Trident/5.0)"
                },
            )
            coros.append(self.internet_check(session, skip=len(ips) > 10))

        self.sessions = filter(None, await asyncio.gather(*coros))
        if len(self.ip_publics) > 0:
            logging.info(
                f"Usando {len(self.ip_publics)} Ips_rotativas"
            )
        else:
            raise Exception(
                f"Error, no hay ips disponibles con internet testeado con: {self.url_judges}"
            )
            exit()

        self.all_sessions = self.get_all_sessions()

    async def get_session(self):
        with await self.lock:
            if not self.all_sessions:
                await self.starts()
        return self.session

    @property
    def session(self):
        return next(self.all_sessions)

    def get_all_sessions(self):
        positions = itertools.cycle(self.sessions)
        for session in itertools.islice(
            positions, randint(0, len(self.ip_publics)), None
        ):
            yield session

def chunk_list_every(iter_object, chunk_every:int):
    i = iter(iter_object)
    piece = list(islice(i, chunk_every))
    while piece:
        yield piece
        piece = list(islice(i, chunk_every))