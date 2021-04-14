from logging import getLogger


def enter_logger(entry):
    getLogger(__name__).info(f'inserting {entry}')


def delete_logger(entry):
    getLogger(__name__).info(f'deleting {entry}')


def silent(*args, **kwargs):
    pass
