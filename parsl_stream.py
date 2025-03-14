import parsl
import logging
import sys
import os

from uuid import uuid4

from parsl import Config
from parsl import HighThroughputExecutor

from proxystore.stream import StreamConsumer, StreamProducer
from proxystore.ex.stream.shims.mofka import MofkaSubscriber
from proxystore.ex.stream.shims.mofka import MofkaPublisher

assert (MOFKA_GROUPFILE := os.environ["MOFKA_GROUPFILE"])
assert os.environ["MOFKA_PROTOCOL"]

logger = logging.getLogger(__name__)

config = Config(
    executors=[
        HighThroughputExecutor(
            max_workers_per_node=2,
            cpu_affinity="block",
        )
    ]
)
parsl.clear()
parsl.load(config)


@parsl.python_app
def task_server():
    import logging
    import os
    from uuid import uuid4
    from proxystore.stream import StreamConsumer, StreamProducer
    from proxystore.ex.stream.shims.mofka import MofkaSubscriber
    from proxystore.ex.stream.shims.mofka import MofkaPublisher

    logger = logging.getLogger(__name__)

    assert (MOFKA_GROUPFILE := os.environ["MOFKA_GROUPFILE"])
    assert os.environ["MOFKA_PROTOCOL"]
    subscriber = MofkaSubscriber(
        group_file=MOFKA_GROUPFILE,
        topic_name="mofa_test2_requests",
        subscriber_name=str(f"MOFA-request-{uuid4()}"),
    )
    consumer = StreamConsumer(
        subscriber=subscriber,
    )

    req = consumer.next_object()
    logger.debug(f"Task server consumer received message: {req}")

    publisher = MofkaPublisher(group_file=MOFKA_GROUPFILE)
    producer = StreamProducer(publisher=publisher)
    producer.send("mofa_test2_generation_result", "1234")
    return "task server completed"


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

subscriber = MofkaSubscriber(
    group_file=MOFKA_GROUPFILE,
    topic_name="mofa_test2_generation_result",
    subscriber_name=str(f"MOFA-result-{uuid4()}"),
)
consumer = StreamConsumer(
    subscriber=subscriber,
)

publisher = MofkaPublisher(group_file=MOFKA_GROUPFILE)
producer = StreamProducer(publisher=publisher)

futures = []
for i in range(200):
    producer.send(
        "mofa_test2_requests",
        "thinker message",
    )
    future = task_server()
    futures.append(future)
    consumed_event = consumer.next_object()
    logger.debug(f"{consumed_event=}")

print([f.result() for f in futures])

parsl.dfk().cleanup()
