from __future__ import print_function, unicode_literals, division, absolute_import

from celery import task
from celery.utils.log import get_task_logger

@task
def add_task(a, b):
    logger = get_task_logger('celery')
    logger.info('Adding {} + {} = {}'.format(a, b, a + b))

    with open('/tmp/result', 'w') as f:
        f.write('{} + {} = {}'.format(a, b, a + b))
