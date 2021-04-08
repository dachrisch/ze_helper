from logging import getLogger


class DryRunner(object):
    def __init__(self, method, url, arguments, response_json):
        self.method = method
        self.url = url
        self.arguments = arguments
        self.response_json = response_json

        getLogger(__name__).debug(f'{self.method}({self.url}, {self.arguments})')
        getLogger(__name__).debug(f'response->({self.response_json})')

    def json(self):
        return self.response_json


def post_logger(*args, **kwargs):
    return DryRunner('post', args[0], kwargs, {'success': 1})


def delete_logger(*args, **kwargs):
    return DryRunner('delete', args[0], kwargs, {'success': 1})
