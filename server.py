from flask import Flask
import concurrent.futures
import json
import requests
import random
import time
import threading


LETTERS_PARAMS = {
    'FL': {
        'url': 'http://192.168.88.151',
        'length': 438,
    },
    'FR': {
        'url': 'http://192.168.88.149',
        'length': 774,
    },
    'P': {
        'url': 'http://192.168.88.146',
        'length': 824,
    },
    'ML': {
        'url': 'http://192.168.88.150',
        'length': 598,
    },
    'MR': {
        'url': 'http://192.168.88.147',
        'length': 576,
    },
    'I': {
        'url': 'http://192.168.88.145',
        'length': 1043,
    }
}

ENABLE_FLAG_REQUEST_TEMPLATE = {
    "on": True,
    "udpn": {
        "send": False,
        "recv": True
    },
    "seg": {
        "id": 0,
        "i": []
    }
}

DISABLE_LETTERS_REQUEST = {
    "on": False,
    "udpn": {
        "send": True,
        "recv": True
    }
}

ENABLE_PRESET_REQUEST = {
    "on": True,
    "udpn": {
        "send": True,
        "recv": True
    },
    "ps": 0
}

ENABLE_PLAYLIST_REQUEST = {
    "on": True,
    "udpn": {
        "send": False,
        "recv": True
    },
    "playlist": {
        "ps": [],
        "dur": [],
        "transition": 20,    
        "repeat": -1,
        "end": 2
    }
}


app = Flask(__name__)
mutex = threading.RLock()


def print_response(response):
    if response.status_code != 200:
        print('Response failed:', response, response.reason)


@app.route('/flag/<group_id>')
def enable_flag(group_id):
    print('Incoming request to enable flag of group {}'.format(group_id))

    with open('flags_for_letters_json/{}.json'.format(group_id), 'r') as f:
        letters_mapping = json.load(f)

    def send_enable_flag_request(url, letter, params, rand_disable):
        if len(params['colors']) == 0:
            return
        for start_led in range(0, len(params['colors']), 500):
            req = ENABLE_FLAG_REQUEST_TEMPLATE.copy()
            zipped_colors = params['colors'][start_led:start_led + 500]

            for i in range(len(zipped_colors)):
                if random.randint(0, rand_disable) != 0:
                    zipped_colors[i] = '000000'
            
            req["seg"]["i"] = [start_led] + zipped_colors
            
            response = requests.post('{url}/json/state'.format(url=url), json=req)
            print_response(response)

    with mutex:
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            for rand_disable in range(1, -1, -1):
                futures_to_url = (executor.submit(send_enable_flag_request, LETTERS_PARAMS[letter]['url'], letter, params, rand_disable ** 2) for letter, params in letters_mapping.items())
                concurrent.futures.wait(futures_to_url)

        print(time.time() - start)
        
    return 'Success'


@app.route('/disable')
def disable_letters():
    print('Incoming request to disable letters')

    with mutex:
        response = requests.post('{url}/json/state'.format(url=LETTERS_PARAMS['P']['url']), json=DISABLE_LETTERS_REQUEST)
        print_response(response)

    return 'Success'


@app.route('/idle')
def idle():
    print('Incoming request to idle')

    with mutex:
        request = ENABLE_PRESET_REQUEST.copy()
        request['ps'] = 2

        def send_enable_preset(url, request):
            response = requests.post('{url}/json/state'.format(url=url), json=request)
            print_response(response)
            

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)

    return 'Success'
    

@app.route('/transition2')
def transition2():
    print('Incoming request to transition')

    with mutex:
        request = ENABLE_PRESET_REQUEST.copy()

        def send_enable_preset(url, request):
            response = requests.post('{url}/json/state'.format(url=url), json=request)
            print_response(response)
            

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            request['ps'] = 1
            request['bri'] = 250
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)

            request['ps'] = 2
            request['bri'] = 70
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)


    return 'Success'


@app.route('/init')
def init():
    print('Incoming request to init')
    with mutex:
        request = ENABLE_PRESET_REQUEST.copy()
        request['ps'] = 1

        def send_enable_preset(url, request):
            response = requests.post('{url}/json/state'.format(url=url), json=request)
            print_response(response)

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)

    return 'Success'


@app.route('/concerts/gp')
def conecert_gp():
    print('Incoming request to play concert GP')
    with mutex:
        request = ENABLE_PLAYLIST_REQUEST.copy()
        request['udpn']['send'] = False
        request['playlist']['ps'] = [5, 5, 4, 4, 3]
        request['playlist']['dur'] = [350, 160, 310, 230, 460]

        def send_enable_preset(url, request):
            response = requests.post('{url}/json/state'.format(url=url), json=request)
            print_response(response)

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)

    return 'Success'


@app.route('/concerts/tanya')
def concert_tanya():
    print('Incoming request to play concert Tanya')
    with mutex:
        request = ENABLE_PLAYLIST_REQUEST.copy()
        request['udpn']['send'] = False
        request['playlist']['ps'] = [6]
        request['playlist']['dur'] = [1890]

        def send_enable_preset(url, request):
            response = requests.post('{url}/json/state'.format(url=url), json=request)
            print_response(response)

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)

    return 'Success'


@app.route('/concerts/resonance')
def concert_resonance():
    print('Incoming request to play concert Resonance')
    with mutex:
        request = ENABLE_PLAYLIST_REQUEST.copy()
        request['udpn']['send'] = False
        request['playlist']['ps'] = [] # TODO:
        request['playlist']['dur'] = [] # TODO:

        def send_enable_preset(url, request):
            response = requests.post('{url}/json/state'.format(url=url), json=request)
            print_response(response)

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)

    return 'Success'


@app.route('/concerts/spectr')
def concert_spectr():
    print('Incoming request to play concert Spectrum')
    with mutex:
        request = ENABLE_PLAYLIST_REQUEST.copy()
        request['udpn']['send'] = False
        request['playlist']['ps'] = [] # TODO:
        request['playlist']['dur'] = [] # TODO:

        def send_enable_preset(url, request):
            response = requests.post('{url}/json/state'.format(url=url), json=request)
            print_response(response)

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures_to_url = (executor.submit(send_enable_preset, LETTERS_PARAMS[letter]['url'], request) for letter in LETTERS_PARAMS.keys())
            concurrent.futures.wait(futures_to_url)

    return 'Success'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)

 