import configparser
import aiohttp
import asyncio
import json

from aiohttp import ClientSession

log_values = []

async def main():
    global log_values
    api_key = get_api_key()
    url_for_keys = get_api_url_for_keys()
    url_for_values = get_api_url_for_values()
    
    async with ClientSession() as session:
        keys = await get_data_for_keys(session, url_for_keys, api_key)
    
    #[print(key['name']) for key in keys['result']]
    
    async with ClientSession() as session:
        tasks = []
        for key in keys['result']:
            values = asyncio.ensure_future(get_data_for_values(session, url_for_values, key['name'], api_key))
            tasks.append(values)
        log_values = await asyncio.gather(*tasks)
    #[print(value) for value in log_values]
    #print(log_values[1])
    with open('Log_Posiciones_FV.json', 'w') as json_file:
        json.dump(log_values, json_file)
        print('Log JSON creado.')

async def get_data_for_keys(session, url_for_keys, api_key):
    async with session.get(url_for_keys, headers={'Authorization': 'Bearer {0}'.format(api_key), 'Content-Type':'application/json; charset=utf-8'}) as response:
        result_data = await response.json()
        return result_data

async def get_data_for_values(session, url_for_values, value_name, api_key):
    async with session.get(url_for_values+value_name, headers={'Authorization': 'Bearer {0}'.format(api_key), 'Content-Type':'application/json; charset=utf-8'}) as response:
        result_data = await response.read()
        json_data = json.loads(result_data)
        return json_data

def get_api_url_for_keys():
    config_file = get_config_file()
    url = config_file['cloudflare_base_url']['base_url'] + config_file['cloudflare_account_url']['account_url'] + config_file['cloudflare_segment_storage_url']['segment_storage_url'] + config_file['cloudflare_namespaces']['namespaces_url'] + config_file['cloudflare_keys']['keys_url']
    return url

def get_api_url_for_values():
    config_file = get_config_file()
    url = config_file['cloudflare_base_url']['base_url'] + config_file['cloudflare_account_url']['account_url'] + config_file['cloudflare_segment_storage_url']['segment_storage_url'] + config_file['cloudflare_namespaces']['namespaces_url'] + config_file['cloudflare_segment_values']['segment_values_url']
    return url

def get_api_key():
    config_file = get_config_file()
    return config_file['cloudflare_api_key']['api_key']

def get_config_file():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())