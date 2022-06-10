import json
import os
import re
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from random import choice

import requests


PATH = Path().resolve()


logger = logging.getLogger('PROXYHUB')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(name)s | %(asctime)s | %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger.addHandler(handler)


class ProxyParser:

    def __init__(self, sources: list, output_file='parsed_proxies.txt'):
        self.sources = sources
        self.output_file = output_file
        self.proxies = []

    def parse_url(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            self.proxies += re.findall(
                pattern=r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{2,5}',
                string=r.text
            )

    def parse(self):
        logger.info(f'Parsing from {len(self.sources)} sources...')
        threads = []
        for source in self.sources:
            thread = threading.Thread(target=self.parse_url, args=(source,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
        logger.info(f'Total parsed {len(self.proxies)} proxies')

    def save(self):
        with open(PATH.joinpath(self.output_file), 'w') as f:
            f.writelines([f'{i}\n' for i in set(self.proxies)])
        logger.info(f'Proxies was saved in {self.output_file}')


class ProxyChecker:
    TYPES = [
        'http',
        'https',
        'socks4',
        'socks5'
    ]

    def __init__(self, parsed_proxies_file='parsed_proxies.txt', output_file='proxies.json'):
        self.parsed = None
        self.proxies = {'updated_at': datetime.now()}
        self.parsed_proxies_file = parsed_proxies_file
        self.output_file = output_file

        self._setup()

    def _setup(self):
        with open(PATH.joinpath(self.parsed_proxies_file)) as f:
            self.parsed = [line.rstrip() for line in f]

    @staticmethod
    def _get_proxy_dict(proxy_type, proxy):
        return {
            'http': f'{proxy_type}://{proxy}',
            'https': f'{proxy_type}://{proxy}'
        }

    def _check_location(self, url, proxy_type, proxy):
        try:
            ip, port = proxy.split(':')
            r = requests.get(
                url=f'https://ipapi.co/{ip}/json',
                proxies=self._check_proxy(url, proxy_type, proxy),
                timeout=10
            ).json()
            return {
                'country': r['country_name'],
                'city': r['city']
            }
        except Exception:
            return {}

    def _check_proxy(self, url, proxy_type, proxy):
        try:
            r = requests.get(
                url=url,
                proxies=self._get_proxy_dict(proxy_type, proxy),
                timeout=10
            )
            if r.status_code == 200:
                self.proxies[proxy] = {'type': proxy_type}
                self.proxies[proxy].update(self._check_location(proxy_type, proxy))
        except Exception:
            pass

    def check(self, url='https://google.com/'):
        logger.info(f'Start checking {len(self.parsed)} proxies')
        threads = []
        for proxy in self.parsed:
            for proxy_type in self.TYPES:
                thread = threading.Thread(target=self._check_proxy, args=(url, proxy_type, proxy))
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()
        logger.info(f'{len(self.proxies.keys()) - 1} was checked successfully')

    def save(self):
        json.dump(self.proxies, open(PATH.joinpath(self.output_file), 'w'), indent=4, default=str)


class ProxyHub:

    def __init__(
            self,
            sources: list,
            update_per_hours: int = 1,
            checked_proxies_json_file: str = 'proxies.json'
    ):
        self.sources = sources
        self.update_per_hours = update_per_hours
        self.checked_proxies_json_file = checked_proxies_json_file

        self._setup()

    def _setup(self):
        if not os.path.exists(PATH.joinpath(self.checked_proxies_json_file)):
            with open(PATH.joinpath(self.checked_proxies_json_file), 'w') as f:
                json.dump({'updated_at': f'{datetime.min}.000'}, f)

    def _are_proxies_alive(self, parsed_datetime: str):
        return (
                datetime.strptime(parsed_datetime, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=self.update_per_hours)
                < datetime.now()
        )

    def refresh(self, check_url):
        pp = ProxyParser(sources=self.sources)
        pp.parse()
        pp.save()

        pc = ProxyChecker()
        pc.check(check_url)
        pc.save()

    def get(self, url='https://google.com/', force_refresh=False, allow_refresh=True):
        proxies = json.load(open(self.checked_proxies_json_file))

        if force_refresh or (allow_refresh and self._are_proxies_alive(proxies['updated_at'])):
            logger.info('Initializing...')
            logger.info('Proxies outdated, refreshing...')
            self.refresh(url)
            logger.info('Proxies was refreshed')
            return self.get(url, force_refresh, allow_refresh)

        proxies.pop('updated_at')
        proxy = choice(list(proxies.keys()))
        return proxy, proxies[proxy]
