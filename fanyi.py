#!/usr/bin/python
# coding: utf-8

import requests
import json
import sys
import os.path
import re
import subprocess

KEYFROM = ''    # Your keyfrom string from youdao API
KEY = ''        # Your API key string from youdao API
APIURL = 'http://fanyi.youdao.com/openapi.do?keyfrom=%s&key=%s&type=data&doctype=json&version=1.1&q='
LOCALFILE = False
LOCALFILEPATH = ''

class Fanyi(object):
    def __init__(self, word):
        self.word = word
        self.keyfrom = KEYFROM
        self.key = KEY
        self.request_url = APIURL % (self.keyfrom, self.key) + word.strip().lower()

    def lookup(self):
        if LOCALFILE:
            self._local_lookup()
        else:
            self._web_lookup()

    def _web_lookup(self):
        self.result = requests.get(self.request_url)
        if self.result.status_code != 200:
            print('Failed to get to the YOUDAO API.')
            sys.exit(1)

        self._result_handling()
        self._parse_data()
        self._web_output_string()

    def _local_lookup(self):
        if not os.path.exists(LOCALFILEPATH):
            try:
                localfile = open(LOCALFILEPATH, 'w+')
            except IOError as e:
                print('Failed at create local file. Error: %s' % e)
                sys.exit(1)

        local_word = ''
        with open(LOCALFILEPATH) as wordlist:
            for line in wordlist:
                if line.strip() == '':
                    wordline = wordlist.next()
                    if wordline.strip() == '':
                        continue
                    elif wordline.split()[0] == self.word:
                        local_word += wordline
                        try:
                            while True:
                                tmp_line = wordlist.next()
                                if tmp_line.strip() == '':
                                    break
                                else:
                                    local_word += tmp_line
                        except StopIteration:
                            pass
                        self._local_output_string(local_word.decode('utf-8'))

        if not local_word:
            self._web_lookup()
            self.save_to_local()

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
            print('Invalid API key.')
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

    def _result_string(self):
        result_string =\
u'''
%s %s
【翻译】
%s
【词典】
%s
【网络】
%s
'''\
        % (
            self.result_dict['word'],
            self.result_dict['pronounce'],
            self.result_dict['translation'],
            self.result_dict['explains'],
            self.result_dict['webs'],
        )

        return result_string

    def _local_output_string(self, local_word):
        # Parse the word paragraph
        lines = local_word.split('\n')
        word = lines[0].split()[0]
        pronounce = ' '.join(lines[0].split()[1:])

        pattern = re.compile(ur'\u3010([\u4e00-\u9fa5]+)\u3011')
        defs = lines[1:]
        lens = len(defs)
        definitions = {}
        for n, line in enumerate(defs):
            if pattern.match(line):
                tmp_key = pattern.match(line).group(1)
                definitions[tmp_key] = []

                try:
                    for i in xrange(1, lens+1):
                        if pattern.match(defs[n+i]):
                            break
                        else:
                            definitions[tmp_key].append(defs[n+i])
                except IndexError:
                    pass

        # Form the output
        output_string = '\n'
        output_string += self._colored_string('%s', 'red') % word
        output_string += ' '
        output_string += self._colored_string('%s', 'gray') % pronounce

        for k, v in definitions.items():
            output_string += '\n\n'
            output_string += self._colored_string('%s', 'blue') % k
            output_string += '\n'
            output_string += '\n'.join(v)



        print output_string

    def _web_output_string(self):
        output_string = '\n'
        output_string += self._colored_string('%s', 'red')
        output_string += ' '
        output_string += self._colored_string('%s', 'gray')
        output_string += '\n\n'
        output_string += self._colored_string(u'翻译', 'blue')
        output_string += '\n'
        output_string += '%s'
        output_string += '\n\n'
        output_string += self._colored_string(u'词典', 'blue')
        output_string += '\n'
        output_string += '%s'
        output_string += '\n\n'
        output_string += self._colored_string(u'网络', 'blue')
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

    def save_to_local(self):
        with open(LOCALFILEPATH, 'a') as wordlist:
            wordlist.write(self._result_string().encode('utf-8'))
        

def main(word):
    fanyi = Fanyi(word)
    fanyi.lookup()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'give a word'
        sys.exit(1)
    else:
        word = sys.argv[1]
        if word == '-l':
            if LOCALFILE:
                subprocess.call(['less', LOCALFILEPATH])
                sys.exit(0)
            else:
                print 'You should set LOCALFILE true to view local wordlist.'
                sys.exit(1)
        main(word)
