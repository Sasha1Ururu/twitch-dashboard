Note

This is the base class used for all EventSub Transport implementations.

See [EventSub](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.html) for a list of all available Transports.

## Class Documentation[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#class-documentation "Link to this heading")

_class_ twitchAPI.eventsub.base.EventSubBase[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase "Link to this definition")

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC "(in Python v3.13)")

EventSub integration for the Twitch Helix API.

\_\_init\_\_(_twitch_, _logger\_name_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.__init__ "Link to this definition")

Parameters:

-   **twitch**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.params.twitch) ([`Twitch`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.twitch.html#twitchAPI.twitch.Twitch "twitchAPI.twitch.Twitch")) – a app authenticated instance of [`Twitch`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.twitch.html#twitchAPI.twitch.Twitch "twitchAPI.twitch.Twitch")
    
-   **logger\_name**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.params.logger_name) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the name of the logger to be used
    

logger_: [`Logger`](https://docs.python.org/3/library/logging.html#logging.Logger "(in Python v3.13)")_[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.logger "Link to this definition")

The logger used for EventSub related log messages

_abstract_ start()[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.start "Link to this definition")

Starts the EventSub client

Return type:

None

Raises:

[**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError "(in Python v3.13)") – if EventSub is already running

_abstract async_ stop()[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.stop "Link to this definition")

Stops the EventSub client

This also unsubscribes from all known subscriptions if unsubscribe\_on\_stop is True

Return type:

None

_async_ unsubscribe\_all()[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.unsubscribe_all "Link to this definition")

Unsubscribe from all subscriptions

_async_ unsubscribe\_all\_known()[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.unsubscribe_all_known "Link to this definition")

Unsubscribe from all subscriptions known to this client.

_async_ unsubscribe\_topic(_topic\_id_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.unsubscribe_topic "Link to this definition")

Unsubscribe from a specific topic.

Return type:

[`bool`](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")

_async_ listen\_channel\_update(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update "Link to this definition")

A broadcaster updates their channel properties e.g., category, title, mature flag, broadcast, or language.

No Authentication required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUpdateEvent "twitchAPI.object.eventsub.ChannelUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_update\_v2(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update_v2 "Link to this definition")

A broadcaster updates their channel properties e.g., category, title, content classification labels or language.

No Authentication required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update_v2.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update_v2.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUpdateEvent "twitchAPI.object.eventsub.ChannelUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_follow\_v2(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2 "Link to this definition")

A specified channel receives a follow.

User Authentication with [`MODERATOR_READ_FOLLOWERS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_FOLLOWERS "twitchAPI.type.AuthScope.MODERATOR_READ_FOLLOWERS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelfollow](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelfollow)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the moderator of the channel you want to get follow notifications for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelFollowEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelFollowEvent "twitchAPI.object.eventsub.ChannelFollowEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_subscribe(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscribe "Link to this definition")

A notification when a specified channel receives a subscriber. This does not include resubscribes.

User Authentication with [`CHANNEL_READ_SUBSCRIPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscribe](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscribe)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscribe.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscribe.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSubscribeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscribeEvent "twitchAPI.object.eventsub.ChannelSubscribeEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_subscription\_end(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_end "Link to this definition")

A notification when a subscription to the specified channel ends.

User Authentication with [`CHANNEL_READ_SUBSCRIPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptionend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptionend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_end.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_end.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSubscriptionEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscriptionEndEvent "twitchAPI.object.eventsub.ChannelSubscriptionEndEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_subscription\_gift(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_gift "Link to this definition")

A notification when a viewer gives a gift subscription to one or more users in the specified channel.

User Authentication with [`CHANNEL_READ_SUBSCRIPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptiongift](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptiongift)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_gift.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_gift.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSubscriptionGiftEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscriptionGiftEvent "twitchAPI.object.eventsub.ChannelSubscriptionGiftEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_subscription\_message(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_message "Link to this definition")

A notification when a user sends a resubscription chat message in a specific channel.

User Authentication with [`CHANNEL_READ_SUBSCRIPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptionmessage](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptionmessage)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_message.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_message.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSubscriptionMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscriptionMessageEvent "twitchAPI.object.eventsub.ChannelSubscriptionMessageEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_cheer(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_cheer "Link to this definition")

A user cheers on the specified channel.

User Authentication with [`BITS_READ`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.BITS_READ "twitchAPI.type.AuthScope.BITS_READ") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelcheer](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelcheer)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_cheer.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_cheer.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelCheerEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelCheerEvent "twitchAPI.object.eventsub.ChannelCheerEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_raid(_callback_, _to\_broadcaster\_user\_id\=None_, _from\_broadcaster\_user\_id\=None_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_raid "Link to this definition")

A broadcaster raids another broadcaster’s channel.

No authorization required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelraid](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelraid)

Parameters:

-   **from\_broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_raid.params.from_broadcaster_user_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – The broadcaster user ID that created the channel raid you want to get notifications for.
    
-   **to\_broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_raid.params.to_broadcaster_user_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – The broadcaster user ID that received the channel raid you want to get notifications for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_raid.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelRaidEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelRaidEvent "twitchAPI.object.eventsub.ChannelRaidEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_ban(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ban "Link to this definition")

A viewer is banned from the specified channel.

User Authentication with [`CHANNEL_MODERATE`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MODERATE "twitchAPI.type.AuthScope.CHANNEL_MODERATE") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelban](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelban)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ban.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ban.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelBanEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelBanEvent "twitchAPI.object.eventsub.ChannelBanEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_unban(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban "Link to this definition")

A viewer is unbanned from the specified channel.

User Authentication with [`CHANNEL_MODERATE`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MODERATE "twitchAPI.type.AuthScope.CHANNEL_MODERATE") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelunban](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelunban)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelUnbanEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUnbanEvent "twitchAPI.object.eventsub.ChannelUnbanEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_moderator\_add(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_add "Link to this definition")

Moderator privileges were added to a user on a specified channel.

User Authentication with [`MODERATION_READ`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATION_READ "twitchAPI.type.AuthScope.MODERATION_READ") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelmoderatoradd](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelmoderatoradd)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_add.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_add.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelModeratorAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelModeratorAddEvent "twitchAPI.object.eventsub.ChannelModeratorAddEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_moderator\_remove(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_remove "Link to this definition")

Moderator privileges were removed from a user on a specified channel.

User Authentication with [`MODERATION_READ`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATION_READ "twitchAPI.type.AuthScope.MODERATION_READ") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelmoderatorremove](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelmoderatorremove)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_remove.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_remove.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelModeratorRemoveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelModeratorRemoveEvent "twitchAPI.object.eventsub.ChannelModeratorRemoveEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_points\_custom\_reward\_add(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add "Link to this definition")

A custom channel points reward has been created for the specified channel.

User Authentication with [`CHANNEL_READ_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS") or [`CHANNEL_MANAGE_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel\_points\_custom\_rewardadd](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_rewardadd)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPointsCustomRewardAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardAddEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardAddEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_points\_custom\_reward\_update(_broadcaster\_user\_id_, _callback_, _reward\_id\=None_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update "Link to this definition")

A custom channel points reward has been updated for the specified channel.

User Authentication with [`CHANNEL_READ_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS") or [`CHANNEL_MANAGE_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel\_points\_custom\_rewardupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_rewardupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **reward\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update.params.reward_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – the id of the reward you want to get updates from.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPointsCustomRewardUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardUpdateEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_points\_custom\_reward\_remove(_broadcaster\_user\_id_, _callback_, _reward\_id\=None_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove "Link to this definition")

A custom channel points reward has been removed from the specified channel.

User Authentication with [`CHANNEL_READ_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS") or [`CHANNEL_MANAGE_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel\_points\_custom\_rewardremove](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_rewardremove)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **reward\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove.params.reward_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – the id of the reward you want to get updates from.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPointsCustomRewardRemoveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardRemoveEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardRemoveEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_points\_custom\_reward\_redemption\_add(_broadcaster\_user\_id_, _callback_, _reward\_id\=None_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add "Link to this definition")

A viewer has redeemed a custom channel points reward on the specified channel.

User Authentication with [`CHANNEL_READ_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS") or [`CHANNEL_MANAGE_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel\_points\_custom\_reward\_redemptionadd](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_reward_redemptionadd)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **reward\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add.params.reward_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – the id of the reward you want to get updates from.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPointsCustomRewardRedemptionAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionAddEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionAddEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_points\_custom\_reward\_redemption\_update(_broadcaster\_user\_id_, _callback_, _reward\_id\=None_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update "Link to this definition")

A redemption of a channel points custom reward has been updated for the specified channel.

User Authentication with [`CHANNEL_READ_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS") or [`CHANNEL_MANAGE_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel\_points\_custom\_reward\_redemptionupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_reward_redemptionupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **reward\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update.params.reward_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – the id of the reward you want to get updates from.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPointsCustomRewardRedemptionUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionUpdateEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_poll\_begin(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin "Link to this definition")

A poll started on a specified channel.

User Authentication with [`CHANNEL_READ_POLLS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_POLLS "twitchAPI.type.AuthScope.CHANNEL_READ_POLLS") or [`CHANNEL_MANAGE_POLLS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollbegin](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollbegin)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPollBeginEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPollBeginEvent "twitchAPI.object.eventsub.ChannelPollBeginEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_poll\_progress(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress "Link to this definition")

Users respond to a poll on a specified channel.

User Authentication with [`CHANNEL_READ_POLLS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_POLLS "twitchAPI.type.AuthScope.CHANNEL_READ_POLLS") or [`CHANNEL_MANAGE_POLLS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollprogress](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollprogress)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPollProgressEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPollProgressEvent "twitchAPI.object.eventsub.ChannelPollProgressEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_poll\_end(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end "Link to this definition")

A poll ended on a specified channel.

User Authentication with [`CHANNEL_READ_POLLS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_POLLS "twitchAPI.type.AuthScope.CHANNEL_READ_POLLS") or [`CHANNEL_MANAGE_POLLS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPollEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPollEndEvent "twitchAPI.object.eventsub.ChannelPollEndEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_prediction\_begin(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin "Link to this definition")

A Prediction started on a specified channel.

User Authentication with [`CHANNEL_READ_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS") or [`CHANNEL_MANAGE_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionbegin](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionbegin)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPredictionEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEvent "twitchAPI.object.eventsub.ChannelPredictionEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_prediction\_progress(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress "Link to this definition")

Users participated in a Prediction on a specified channel.

User Authentication with [`CHANNEL_READ_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS") or [`CHANNEL_MANAGE_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionprogress](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionprogress)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPredictionEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEvent "twitchAPI.object.eventsub.ChannelPredictionEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_prediction\_lock(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock "Link to this definition")

A Prediction was locked on a specified channel.

User Authentication with [`CHANNEL_READ_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS") or [`CHANNEL_MANAGE_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionlock](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionlock)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPredictionEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEvent "twitchAPI.object.eventsub.ChannelPredictionEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_prediction\_end(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end "Link to this definition")

A Prediction ended on a specified channel.

User Authentication with [`CHANNEL_READ_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS") or [`CHANNEL_MANAGE_PREDICTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPredictionEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEndEvent "twitchAPI.object.eventsub.ChannelPredictionEndEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_drop\_entitlement\_grant(_organisation\_id_, _callback_, _category\_id\=None_, _campaign\_id\=None_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant "Link to this definition")

An entitlement for a Drop is granted to a user.

App access token required. The client ID associated with the access token must be owned by a user who is part of the specified organization.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#dropentitlementgrant](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#dropentitlementgrant)

Parameters:

-   **organisation\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant.params.organisation_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The organization ID of the organization that owns the game on the developer portal.
    
-   **category\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant.params.category_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – The category (or game) ID of the game for which entitlement notifications will be received.
    
-   **campaign\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant.params.campaign_id) ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional "(in Python v3.13)")\[[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]) – The campaign ID for a specific campaign for which entitlement notifications will be received.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`DropEntitlementGrantEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.DropEntitlementGrantEvent "twitchAPI.object.eventsub.DropEntitlementGrantEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_extension\_bits\_transaction\_create(_extension\_client\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_extension_bits_transaction_create "Link to this definition")

A Bits transaction occurred for a specified Twitch Extension.

The OAuth token client ID must match the Extension client ID.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#extensionbits\_transactioncreate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#extensionbits_transactioncreate)

Parameters:

-   **extension\_client\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_extension_bits_transaction_create.params.extension_client_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_extension_bits_transaction_create.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ExtensionBitsTransactionCreateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ExtensionBitsTransactionCreateEvent "twitchAPI.object.eventsub.ExtensionBitsTransactionCreateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_goal\_begin(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_begin "Link to this definition")

A goal begins on the specified channel.

User Authentication with [`CHANNEL_READ_GOALS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_GOALS "twitchAPI.type.AuthScope.CHANNEL_READ_GOALS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalbegin](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalbegin)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_begin.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_begin.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`GoalEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.GoalEvent "twitchAPI.object.eventsub.GoalEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_goal\_progress(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_progress "Link to this definition")

A goal makes progress on the specified channel.

User Authentication with [`CHANNEL_READ_GOALS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_GOALS "twitchAPI.type.AuthScope.CHANNEL_READ_GOALS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalprogress](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalprogress)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_progress.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_progress.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`GoalEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.GoalEvent "twitchAPI.object.eventsub.GoalEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_goal\_end(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_end "Link to this definition")

A goal ends on the specified channel.

User Authentication with [`CHANNEL_READ_GOALS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_GOALS "twitchAPI.type.AuthScope.CHANNEL_READ_GOALS") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_end.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_end.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`GoalEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.GoalEvent "twitchAPI.object.eventsub.GoalEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_hype\_train\_begin(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_begin "Link to this definition")

A Hype Train begins on the specified channel.

User Authentication with [`CHANNEL_READ_HYPE_TRAIN`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN "twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype\_trainbegin](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype_trainbegin)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_begin.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_begin.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`HypeTrainEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.HypeTrainEvent "twitchAPI.object.eventsub.HypeTrainEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_hype\_train\_progress(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_progress "Link to this definition")

A Hype Train makes progress on the specified channel.

User Authentication with [`CHANNEL_READ_HYPE_TRAIN`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN "twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype\_trainprogress](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype_trainprogress)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_progress.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_progress.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`HypeTrainEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.HypeTrainEvent "twitchAPI.object.eventsub.HypeTrainEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_hype\_train\_end(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_end "Link to this definition")

A Hype Train ends on the specified channel.

User Authentication with [`CHANNEL_READ_HYPE_TRAIN`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN "twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN") is required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype\_trainend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype_trainend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_end.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_end.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`HypeTrainEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.HypeTrainEndEvent "twitchAPI.object.eventsub.HypeTrainEndEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_stream\_online(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_online "Link to this definition")

The specified broadcaster starts a stream.

No authorization required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamonline](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamonline)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_online.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_online.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`StreamOnlineEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.StreamOnlineEvent "twitchAPI.object.eventsub.StreamOnlineEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_stream\_offline(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_offline "Link to this definition")

The specified broadcaster stops a stream.

No authorization required.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamoffline](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamoffline)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_offline.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – the id of the user you want to listen to
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_offline.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`StreamOfflineEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.StreamOfflineEvent "twitchAPI.object.eventsub.StreamOfflineEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

A user’s authorization has been granted to your client id.

Provided client\_id must match the client id in the application access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userauthorizationgrant](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userauthorizationgrant)

Parameters:

-   **client\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_grant.params.client_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Your application’s client id.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_grant.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`UserAuthorizationGrantEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserAuthorizationGrantEvent "twitchAPI.object.eventsub.UserAuthorizationGrantEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_user\_authorization\_revoke(_client\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_revoke "Link to this definition")

A user’s authorization has been revoked for your client id.

Provided client\_id must match the client id in the application access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userauthorizationrevoke](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userauthorizationrevoke)

Parameters:

-   **client\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_revoke.params.client_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Your application’s client id.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_revoke.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`UserAuthorizationRevokeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserAuthorizationRevokeEvent "twitchAPI.object.eventsub.UserAuthorizationRevokeEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_user\_update(_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_update "Link to this definition")

A user has updated their account.

No authorization required. If you have the [`USER_READ_EMAIL`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_EMAIL "twitchAPI.type.AuthScope.USER_READ_EMAIL") scope, the notification will include email field.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userupdate)

Parameters:

-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_update.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID for the user you want update notifications for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`UserUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserUpdateEvent "twitchAPI.object.eventsub.UserUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_shield\_mode\_begin(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin "Link to this definition")

Sends a notification when the broadcaster activates Shield Mode.

Requires the [`MODERATOR_READ_SHIELD_MODE`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_SHIELD_MODE "twitchAPI.type.AuthScope.MODERATOR_READ_SHIELD_MODE") or [`MODERATOR_MANAGE_SHIELD_MODE`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE "twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshield\_modebegin](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshield_modebegin)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when they activate Shield Mode.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster or one of the broadcaster’s moderators.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ShieldModeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ShieldModeEvent "twitchAPI.object.eventsub.ShieldModeEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_shield\_mode\_end(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end "Link to this definition")

Sends a notification when the broadcaster deactivates Shield Mode.

Requires the [`MODERATOR_READ_SHIELD_MODE`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_SHIELD_MODE "twitchAPI.type.AuthScope.MODERATOR_READ_SHIELD_MODE") or [`MODERATOR_MANAGE_SHIELD_MODE`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE "twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshield\_modeend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshield_modeend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when they deactivate Shield Mode.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster or one of the broadcaster’s moderators.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ShieldModeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ShieldModeEvent "twitchAPI.object.eventsub.ShieldModeEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_charity\_campaign\_start(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_start "Link to this definition")

Sends a notification when the broadcaster starts a charity campaign.

Requires the [`CHANNEL_READ_CHARITY`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY "twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity\_campaignstart](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaignstart)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_start.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when they start a charity campaign.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_start.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`CharityCampaignStartEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityCampaignStartEvent "twitchAPI.object.eventsub.CharityCampaignStartEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_charity\_campaign\_progress(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_progress "Link to this definition")

Sends notifications when progress is made towards the campaign’s goal or when the broadcaster changes the fundraising goal.

Requires the [`CHANNEL_READ_CHARITY`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY "twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity\_campaignprogress](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaignprogress)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_progress.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when their campaign makes progress or is updated.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_progress.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`CharityCampaignProgressEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityCampaignProgressEvent "twitchAPI.object.eventsub.CharityCampaignProgressEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_charity\_campaign\_stop(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_stop "Link to this definition")

Sends a notification when the broadcaster stops a charity campaign.

Requires the [`CHANNEL_READ_CHARITY`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY "twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity\_campaignstop](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaignstop)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_stop.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when they stop a charity campaign.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_stop.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`CharityCampaignStopEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityCampaignStopEvent "twitchAPI.object.eventsub.CharityCampaignStopEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_charity\_campaign\_donate(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_donate "Link to this definition")

Sends a notification when a user donates to the broadcaster’s charity campaign.

Requires the [`CHANNEL_READ_CHARITY`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY "twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity\_campaigndonate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaigndonate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_donate.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when users donate to their campaign.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_donate.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`CharityDonationEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityDonationEvent "twitchAPI.object.eventsub.CharityDonationEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_shoutout\_create(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create "Link to this definition")

Sends a notification when the specified broadcaster sends a Shoutout.

Requires the [`MODERATOR_READ_SHOUTOUTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_SHOUTOUTS "twitchAPI.type.AuthScope.MODERATOR_READ_SHOUTOUTS") or [`MODERATOR_MANAGE_SHOUTOUTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHOUTOUTS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHOUTOUTS") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshoutoutcreate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshoutoutcreate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when they send a Shoutout.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that gave the Shoutout or one of the broadcaster’s moderators.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelShoutoutCreateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelShoutoutCreateEvent "twitchAPI.object.eventsub.ChannelShoutoutCreateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_shoutout\_receive(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive "Link to this definition")

Sends a notification when the specified broadcaster receives a Shoutout.

Requires the [`MODERATOR_READ_SHOUTOUTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_SHOUTOUTS "twitchAPI.type.AuthScope.MODERATOR_READ_SHOUTOUTS") or [`MODERATOR_MANAGE_SHOUTOUTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHOUTOUTS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHOUTOUTS") auth scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshoutoutreceive](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshoutoutreceive)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to receive notifications about when they receive a Shoutout.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that received the Shoutout or one of the broadcaster’s moderators.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelShoutoutReceiveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelShoutoutReceiveEvent "twitchAPI.object.eventsub.ChannelShoutoutReceiveEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_clear(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear "Link to this definition")

A moderator or bot has cleared all messages from the chat room.

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from chatting user. If app access token used, then additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") scope from chatting user, and either [`CHANNEL_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_BOT "twitchAPI.type.AuthScope.CHANNEL_BOT") scope from broadcaster or moderator status.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatclear](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatclear)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat clear events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatClearEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatClearEvent "twitchAPI.object.eventsub.ChannelChatClearEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_clear\_user\_messages(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages "Link to this definition")

A moderator or bot has cleared all messages from a specific user.

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from chatting user. If app access token used, then additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") scope from chatting user, and either [`CHANNEL_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_BOT "twitchAPI.type.AuthScope.CHANNEL_BOT") scope from broadcaster or moderator status.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatclear\_user\_messages](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatclear_user_messages)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat clear user messages events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatClearUserMessagesEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatClearUserMessagesEvent "twitchAPI.object.eventsub.ChannelChatClearUserMessagesEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_message\_delete(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete "Link to this definition")

A moderator has removed a specific message.

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from chatting user. If app access token used, then additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") scope from chatting user, and either [`CHANNEL_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_BOT "twitchAPI.type.AuthScope.CHANNEL_BOT") scope from broadcaster or moderator status.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage\_delete](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage_delete)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat message delete events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatMessageDeleteEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatMessageDeleteEvent "twitchAPI.object.eventsub.ChannelChatMessageDeleteEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_notification(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification "Link to this definition")

A notification for when an event that appears in chat has occurred.

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from chatting user. If app access token used, then additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") scope from chatting user, and either [`CHANNEL_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_BOT "twitchAPI.type.AuthScope.CHANNEL_BOT") scope from broadcaster or moderator status.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatnotification](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatnotification)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat notification events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatNotificationEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatNotificationEvent "twitchAPI.object.eventsub.ChannelChatNotificationEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_ad\_break\_begin(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ad_break_begin "Link to this definition")

A midroll commercial break has started running.

Requires the [`CHANNEL_READ_ADS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_ADS "twitchAPI.type.AuthScope.CHANNEL_READ_ADS") scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelad\_breakbegin](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelad_breakbegin)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ad_break_begin.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster that you want to get Channel Ad Break begin notifications for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ad_break_begin.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelAdBreakBeginEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelAdBreakBeginEvent "twitchAPI.object.eventsub.ChannelAdBreakBeginEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_message(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message "Link to this definition")

Any user sends a message to a specific chat room.

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from chatting user. If app access token used, then additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") scope from chatting user, and either [`CHANNEL_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_BOT "twitchAPI.type.AuthScope.CHANNEL_BOT") scope from broadcaster or moderator status.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat message events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatMessageEvent "twitchAPI.object.eventsub.ChannelChatMessageEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_settings\_update(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update "Link to this definition")

This event sends a notification when a broadcaster’s chat settings are updated.

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from chatting user. If app access token used, then additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") scope from chatting user, and either [`CHANNEL_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_BOT "twitchAPI.type.AuthScope.CHANNEL_BOT") scope from broadcaster or moderator status.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchat\_settingsupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchat_settingsupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat settings update events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatSettingsUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatSettingsUpdateEvent "twitchAPI.object.eventsub.ChannelChatSettingsUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_user\_whisper\_message(_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message "Link to this definition")

Sends a notification when a user receives a whisper. Event Triggers - Anyone whispers the specified user.

Requires [`USER_READ_WHISPERS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_WHISPERS "twitchAPI.type.AuthScope.USER_READ_WHISPERS") or [`USER_MANAGE_WHISPERS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_MANAGE_WHISPERS "twitchAPI.type.AuthScope.USER_MANAGE_WHISPERS") scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#userwhispermessage](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#userwhispermessage)

Parameters:

-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user\_id of the person receiving whispers.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`UserWhisperMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserWhisperMessageEvent "twitchAPI.object.eventsub.UserWhisperMessageEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_points\_automatic\_reward\_redemption\_add(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add "Link to this definition")

A viewer has redeemed an automatic channel points reward on the specified channel.

Requires [`CHANNEL_READ_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS") or [`CHANNEL_MANAGE_REDEMPTIONS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS") scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchannel\_points\_automatic\_reward\_redemptionadd](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchannel_points_automatic_reward_redemptionadd)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The broadcaster user ID for the channel you want to receive channel points reward add notifications for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelPointsAutomaticRewardRedemptionAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsAutomaticRewardRedemptionAddEvent "twitchAPI.object.eventsub.ChannelPointsAutomaticRewardRedemptionAddEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_vip\_add(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add "Link to this definition")

A VIP is added to the channel.

Requires [`CHANNEL_READ_VIPS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_VIPS "twitchAPI.type.AuthScope.CHANNEL_READ_VIPS") or [`CHANNEL_MANAGE_VIPS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS") scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelvipadd](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelvipadd)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the broadcaster
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelVIPAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelVIPAddEvent "twitchAPI.object.eventsub.ChannelVIPAddEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_vip\_remove(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove "Link to this definition")

A VIP is removed from the channel.

Requires [`CHANNEL_READ_VIPS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_READ_VIPS "twitchAPI.type.AuthScope.CHANNEL_READ_VIPS") or [`CHANNEL_MANAGE_VIPS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS "twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS") scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelvipremove](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelvipremove)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the broadcaster
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelVIPRemoveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelVIPRemoveEvent "twitchAPI.object.eventsub.ChannelVIPRemoveEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_unban\_request\_create(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create "Link to this definition")

A user creates an unban request.

Requires [`MODERATOR_READ_UNBAN_REQUESTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS "twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS") or [`MODERATOR_MANAGE_UNBAN_REQUESTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS") scope.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelunban\_requestcreate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelunban_requestcreate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster you want to get chat unban request notifications for.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the user that has permission to moderate the broadcaster’s channel and has granted your app permission to subscribe to this subscription type.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelUnbanRequestCreateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUnbanRequestCreateEvent "twitchAPI.object.eventsub.ChannelUnbanRequestCreateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_unban\_request\_resolve(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve "Link to this definition")

An unban request has been resolved.

Requires [`MODERATOR_READ_UNBAN_REQUESTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS "twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS") or [`MODERATOR_MANAGE_UNBAN_REQUESTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelunban\_requestresolve](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelunban_requestresolve)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the broadcaster you want to get unban request resolution notifications for.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of the user that has permission to moderate the broadcaster’s channel and has granted your app permission to subscribe to this subscription type.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelUnbanRequestResolveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUnbanRequestResolveEvent "twitchAPI.object.eventsub.ChannelUnbanRequestResolveEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_suspicious\_user\_message(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message "Link to this definition")

A chat message has been sent by a suspicious user.

Requires [`MODERATOR_READ_SUSPICIOUS_USERS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_SUSPICIOUS_USERS "twitchAPI.type.AuthScope.MODERATOR_READ_SUSPICIOUS_USERS") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelsuspicious\_usermessage](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelsuspicious_usermessage)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat message events for.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of a user that has permission to moderate the broadcaster’s channel and has granted your app permission to subscribe to this subscription type.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSuspiciousUserMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSuspiciousUserMessageEvent "twitchAPI.object.eventsub.ChannelSuspiciousUserMessageEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_suspicious\_user\_update(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update "Link to this definition")

A suspicious user has been updated.

Requires [`MODERATOR_READ_SUSPICIOUS_USERS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_SUSPICIOUS_USERS "twitchAPI.type.AuthScope.MODERATOR_READ_SUSPICIOUS_USERS") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelsuspicious\_userupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelsuspicious_userupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The broadcaster you want to get chat unban request notifications for.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The ID of a user that has permission to moderate the broadcaster’s channel and has granted your app permission to subscribe to this subscription type.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSuspiciousUserUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSuspiciousUserUpdateEvent "twitchAPI.object.eventsub.ChannelSuspiciousUserUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_moderate(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate "Link to this definition")

A moderator performs a moderation action in a channel. Includes warnings.

Requires all of the following scopes:

-   [`MODERATOR_READ_BLOCKED_TERMS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_BLOCKED_TERMS "twitchAPI.type.AuthScope.MODERATOR_READ_BLOCKED_TERMS") or [`MODERATOR_MANAGE_BLOCKED_TERMS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS")
    
-   [`MODERATOR_READ_CHAT_SETTINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_CHAT_SETTINGS "twitchAPI.type.AuthScope.MODERATOR_READ_CHAT_SETTINGS") or [`MODERATOR_MANAGE_CHAT_SETTINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_SETTINGS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_SETTINGS")
    
-   [`MODERATOR_READ_UNBAN_REQUESTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS "twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS") or [`MODERATOR_MANAGE_UNBAN_REQUESTS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS")
    
-   [`MODERATOR_READ_BANNED_USERS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_BANNED_USERS "twitchAPI.type.AuthScope.MODERATOR_READ_BANNED_USERS") or [`MODERATOR_MANAGE_BANNED_USERS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_BANNED_USERS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_BANNED_USERS")
    
-   [`MODERATOR_READ_CHAT_MESSAGES`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_CHAT_MESSAGES "twitchAPI.type.AuthScope.MODERATOR_READ_CHAT_MESSAGES") or [`MODERATOR_MANAGE_CHAT_MESSAGES`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES "twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES")
    
-   [`MODERATOR_READ_WARNINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS "twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS") or [`MODERATOR_MANAGE_WARNINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS")
    
-   [`MODERATOR_READ_MODERATORS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_MODERATORS "twitchAPI.type.AuthScope.MODERATOR_READ_MODERATORS")
    
-   [`MODERATOR_READ_VIPS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_VIPS "twitchAPI.type.AuthScope.MODERATOR_READ_VIPS")
    

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelmoderate-v2](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelmoderate-v2)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID of the broadcaster.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID of the moderator.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelModerateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelModerateEvent "twitchAPI.object.eventsub.ChannelModerateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_warning\_acknowledge(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge "Link to this definition")

Sends a notification when a warning is acknowledged by a user.

Requires [`MODERATOR_READ_WARNINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS "twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS") or [`MODERATOR_MANAGE_WARNINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelwarningacknowledge](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelwarningacknowledge)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the broadcaster.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the moderator.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelWarningAcknowledgeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelWarningAcknowledgeEvent "twitchAPI.object.eventsub.ChannelWarningAcknowledgeEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_warning\_send(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send "Link to this definition")

Sends a notification when a warning is send to a user. Broadcasters and moderators can see the warning’s details.

Requires [`MODERATOR_READ_WARNINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS "twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS") or [`MODERATOR_MANAGE_WARNINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS "twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelwarningsend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelwarningsend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the broadcaster.
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the moderator.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelWarningSendEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelWarningSendEvent "twitchAPI.object.eventsub.ChannelWarningSendEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_automod\_message\_hold(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold "Link to this definition")

Sends a notification if a message was caught by automod for review.

Requires [`MODERATOR_MANAGE_AUTOMOD`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD "twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodmessagehold](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodmessagehold)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the broadcaster (channel).
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the moderator.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`AutomodMessageHoldEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodMessageHoldEvent "twitchAPI.object.eventsub.AutomodMessageHoldEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_automod\_message\_update(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update "Link to this definition")

Sends a notification when a message in the automod queue has its status changed.

Requires [`MODERATOR_MANAGE_AUTOMOD`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD "twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodmessageupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodmessageupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the broadcaster (channel)
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the moderator.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`AutomodMessageUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodMessageUpdateEvent "twitchAPI.object.eventsub.AutomodMessageUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_automod\_settings\_update(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update "Link to this definition")

Sends a notification when the broadcaster’s automod settings are updated.

Requires [`MODERATOR_READ_AUTOMOD_SETTINGS`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_READ_AUTOMOD_SETTINGS "twitchAPI.type.AuthScope.MODERATOR_READ_AUTOMOD_SETTINGS") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodsettingsupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodsettingsupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the broadcaster (channel).
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the moderator.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`AutomodSettingsUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodSettingsUpdateEvent "twitchAPI.object.eventsub.AutomodSettingsUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_automod\_terms\_update(_broadcaster\_user\_id_, _moderator\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update "Link to this definition")

Sends a notification when a broadcaster’s automod terms are updated.

Requires [`MODERATOR_MANAGE_AUTOMOD`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD "twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD") scope.

Note

If you use webhooks, the user in moderator\_user\_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

If you use WebSockets, the ID in moderator\_user\_id must match the user ID in the user access token.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodtermsupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodtermsupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the broadcaster (channel).
    
-   **moderator\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update.params.moderator_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the moderator creating the subscription.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`AutomodTermsUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodTermsUpdateEvent "twitchAPI.object.eventsub.AutomodTermsUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_user\_message\_hold(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold "Link to this definition")

A user is notified if their message is caught by automod.

Note

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from the chatting user.

If WebSockets is used, additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") from chatting user.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatuser\_message\_hold](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatuser_message_hold)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat message events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatUserMessageHoldEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatUserMessageHoldEvent "twitchAPI.object.eventsub.ChannelChatUserMessageHoldEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_chat\_user\_message\_update(_broadcaster\_user\_id_, _user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update "Link to this definition")

A user is notified if their message’s automod status is updated.

Note

Requires [`USER_READ_CHAT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_READ_CHAT "twitchAPI.type.AuthScope.USER_READ_CHAT") scope from the chatting user.

If WebSockets is used, additionally requires [`USER_BOT`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.AuthScope.USER_BOT "twitchAPI.type.AuthScope.USER_BOT") from chatting user.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatuser\_message\_update](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatuser_message_update)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – User ID of the channel to receive chat message events for.
    
-   **user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update.params.user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user ID to read chat as.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelChatUserMessageUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatUserMessageUpdateEvent "twitchAPI.object.eventsub.ChannelChatUserMessageUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_shared\_chat\_begin(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_begin "Link to this definition")

A notification when a channel becomes active in an active shared chat session.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared\_chatbegin](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared_chatbegin)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_begin.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the channel to receive shared chat session begin events for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_begin.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSharedChatBeginEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSharedChatBeginEvent "twitchAPI.object.eventsub.ChannelSharedChatBeginEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_shared\_chat\_update(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_update "Link to this definition")

A notification when the active shared chat session the channel is in changes.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared\_chatupdate](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared_chatupdate)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_update.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the channel to receive shared chat session update events for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_update.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSharedChatUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSharedChatUpdateEvent "twitchAPI.object.eventsub.ChannelSharedChatUpdateEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription

_async_ listen\_channel\_shared\_chat\_end(_broadcaster\_user\_id_, _callback_)[#](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_end "Link to this definition")

A notification when a channel leaves a shared chat session or the session ends.

For more information see here: [https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared\_chatend](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared_chatend)

Parameters:

-   **broadcaster\_user\_id**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_end.params.broadcaster_user_id) ([`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The User ID of the channel to receive shared chat session end events for.
    
-   **callback**[¶](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_end.params.callback) ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[[`ChannelSharedChatEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSharedChatEndEvent "twitchAPI.object.eventsub.ChannelSharedChatEndEvent")\], [`Awaitable`](https://docs.python.org/3/library/typing.html#typing.Awaitable "(in Python v3.13)")\[[`None`](https://docs.python.org/3/library/constants.html#None "(in Python v3.13)")\]\]) – function for callback
    

Raises:

-   [**EventSubSubscriptionConflict**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionConflict "twitchAPI.type.EventSubSubscriptionConflict") – if a conflict was found with this subscription (e.g. already subscribed to this exact topic)
    
-   [**EventSubSubscriptionTimeout**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionTimeout "twitchAPI.type.EventSubSubscriptionTimeout") – if [`wait_for_subscription_confirm`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.webhook.html#twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm "twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm") is true and the subscription was not fully confirmed in time
    
-   [**EventSubSubscriptionError**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.EventSubSubscriptionError "twitchAPI.type.EventSubSubscriptionError") – if the subscription failed (see error message for details)
    
-   [**TwitchBackendException**](https://pytwitchapi.dev/en/stable/modules/twitchAPI.type.html#twitchAPI.type.TwitchBackendException "twitchAPI.type.TwitchBackendException") – if the subscription failed due to a twitch backend error
    

Return type:

[`str`](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Returns:

The id of the topic subscription