import uuid
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub


def my_publish_callback(envelope, status):
    print(envelope, status)


pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-60d39bd0-5cfb-11ec-96e9-32997ff5e1b9"
pnconfig.publish_key = "pub-c-0586af82-d21f-4eb0-a261-9b0ec1e03ba0"

pubnub = PubNub(pnconfig)
pubnub.publish() \
    .channel("azurcam-channel") \
    .message({"sender": uuid.getnode(), "content": "Motion Detected"}) \
    .pn_async(my_publish_callback)
