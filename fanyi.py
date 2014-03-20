# coding: utf-8
#!/usr/bin/env python

import requests
import json
import sys

KEYFROM = 'KEYFROM' # Your keyfrom string from youdao API
KEY = 'KEY'         # Your API key string from youdao API
APIURL = 'http://fanyi.youdao.com/openapi.do?keyfrom=%s&key=%s&type=data&doctype=json&version=1.1&q='

class Fanyi(object):
    def __init__(self, word):
        self.keyfrom = KEYFROM
        self.key = KEY
        self.request_url = APIURL % (self.keyfrom, self.key) + word.strip().lower()

    def lookup(self):
        self.result = requests.get(self.request_url)
        if self.result.status_code != 200:
            print('Failed to get to the YOUDAO API.')
            sys.exit(1)

        self._result_handling()
        self._parse_data()
        self._output_string()

    def _result_handling(self):
        self.data = json.loads(self.result.text)
        if self.data['errorCode'] == 20:
            print('word\'s length must be less than 200.')
            sys.exit(1)
        elif self.data['errorCode'] == 30:
            print('Could not get the translation.')
            sys.exit(1)
        elif self.data['errorCode'] == 40:
            print('No support this language.')
            sys.exit(1)
        elif self.data['errorCode'] == 50:
            print('Invalid key value.')
            sys.exit(1)
        elif self.data['errorCode'] == 0:
            if 'basic' in self.data:
                self._parse_data()
            else:
                print('No such a word')
                sys.exit(1)

    def _parse_data(self):
        webs = []
        for v in self.data['web']:
            tmp_string = ''
            tmp_string += v['key']
            tmp_string += ': '
            tmp_string += ', '.join(v['value'])
            webs.append(tmp_string)
        webs = '\n'.join(webs)

        self.result_dict = dict(
            word=self.data['query'],
            translation=' '.join([mean for mean in self.data['translation']]),
            pronounce='[' + self.data['basic']['phonetic'] + ']',
            explains='\n'.join([mean for mean in self.data['basic']['explains']]),
            webs=webs,
        )

    def _output_string(self):
        output_string = ''
        output_string += self._colored_string('%s', 'red')
        output_string += ' '
        output_string += self._colored_string('%s', 'gray')
        output_string += '\n\n'
        output_string += self._colored_string(u'翻译：', 'blue')
        output_string += '\n'
        output_string += '%s'
        output_string += '\n\n'
        output_string += self._colored_string(u'词典：', 'blue')
        output_string += '\n'
        output_string += '%s'
        output_string += '\n\n'
        output_string += self._colored_string(u'网络：', 'blue')
        output_string += '\n'
        output_string += '%s'
        output_string += '\n'

        print(output_string % (
            self.result_dict['word'],
            self.result_dict['pronounce'],
            self.result_dict['translation'],
            self.result_dict['explains'],
            self.result_dict['webs'],
        ))

    def _colored_string(self, string, mode):
        color_codes = {
            'gray':     '\033[1;30m',
            'red':      '\033[1;31m',
            'green':    '\033[1;32m',
            'yellow':   '\033[1;33m',
            'blue':     '\033[1;34m',
            'purple':   '\033[1;35m',
            'cyan':     '\033[1;36m',
            'white':    '\033[1;37m',
            'black':    '\033[1;38m',

            'reset':    '\033[0m',
        }
        return color_codes[mode] + string + color_codes['reset']
        

def main(word):
    fanyi = Fanyi(word)
    fanyi.lookup()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'give a word'
    else:
        word = sys.argv[1]
    main(word)
