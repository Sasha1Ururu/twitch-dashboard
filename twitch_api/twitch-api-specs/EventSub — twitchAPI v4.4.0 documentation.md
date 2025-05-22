**Channel Update** v1

Function: [`listen_channel_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update "twitchAPI.eventsub.base.EventSubBase.listen_channel_update")  
Payload: [`ChannelUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUpdateEvent "twitchAPI.object.eventsub.ChannelUpdateEvent")

A broadcaster updates their channel properties e.g., category, title, mature flag, broadcast, or language.

**Channel Update** v2

Function: [`listen_channel_update_v2()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_update_v2 "twitchAPI.eventsub.base.EventSubBase.listen_channel_update_v2")  
Payload: [`ChannelUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUpdateEvent "twitchAPI.object.eventsub.ChannelUpdateEvent")

A broadcaster updates their channel properties e.g., category, title, content classification labels, broadcast, or language.

**Channel Follow** v2

Function: [`listen_channel_follow_v2()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2 "twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2")  
Payload: [`ChannelFollowEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelFollowEvent "twitchAPI.object.eventsub.ChannelFollowEvent")

A specified channel receives a follow.

**Channel Subscribe**

Function: [`listen_channel_subscribe()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscribe "twitchAPI.eventsub.base.EventSubBase.listen_channel_subscribe")  
Payload: [`ChannelSubscribeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscribeEvent "twitchAPI.object.eventsub.ChannelSubscribeEvent")

A notification when a specified channel receives a subscriber. This does not include resubscribes.

**Channel Subscription End**

Function: [`listen_channel_subscription_end()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_end "twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_end")  
Payload: [`ChannelSubscriptionEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscriptionEndEvent "twitchAPI.object.eventsub.ChannelSubscriptionEndEvent")

A notification when a subscription to the specified channel ends.

**Channel Subscription Gift**

Function: [`listen_channel_subscription_gift()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_gift "twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_gift")  
Payload: [`ChannelSubscriptionGiftEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscriptionGiftEvent "twitchAPI.object.eventsub.ChannelSubscriptionGiftEvent")

A notification when a viewer gives a gift subscription to one or more users in the specified channel.

**Channel Subscription Message**

Function: [`listen_channel_subscription_message()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_message "twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_message")  
Payload: [`ChannelSubscriptionMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSubscriptionMessageEvent "twitchAPI.object.eventsub.ChannelSubscriptionMessageEvent")

A notification when a user sends a resubscription chat message in a specific channel.

**Channel Cheer**

Function: [`listen_channel_cheer()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_cheer "twitchAPI.eventsub.base.EventSubBase.listen_channel_cheer")  
Payload: [`ChannelCheerEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelCheerEvent "twitchAPI.object.eventsub.ChannelCheerEvent")

A user cheers on the specified channel.

**Channel Raid**

Function: [`listen_channel_raid()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_raid "twitchAPI.eventsub.base.EventSubBase.listen_channel_raid")  
Payload: [`ChannelRaidEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelRaidEvent "twitchAPI.object.eventsub.ChannelRaidEvent")

A broadcaster raids another broadcaster’s channel.

**Channel Ban**

Function: [`listen_channel_ban()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ban "twitchAPI.eventsub.base.EventSubBase.listen_channel_ban")  
Payload: [`ChannelBanEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelBanEvent "twitchAPI.object.eventsub.ChannelBanEvent")

A viewer is banned from the specified channel.

**Channel Unban**

Function: [`listen_channel_unban()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban "twitchAPI.eventsub.base.EventSubBase.listen_channel_unban")  
Payload: [`ChannelUnbanEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUnbanEvent "twitchAPI.object.eventsub.ChannelUnbanEvent")

A viewer is unbanned from the specified channel.

**Channel Moderator Add**

Function: [`listen_channel_moderator_add()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_add "twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_add")  
Payload: [`ChannelModeratorAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelModeratorAddEvent "twitchAPI.object.eventsub.ChannelModeratorAddEvent")

Moderator privileges were added to a user on a specified channel.

**Channel Moderator Remove**

Function: [`listen_channel_moderator_remove()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_remove "twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_remove")  
Payload: [`ChannelModeratorRemoveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelModeratorRemoveEvent "twitchAPI.object.eventsub.ChannelModeratorRemoveEvent")

Moderator privileges were removed from a user on a specified channel.

**Channel Points Custom Reward Add**

Function: [`listen_channel_points_custom_reward_add()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add "twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add")  
Payload: [`ChannelPointsCustomRewardAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardAddEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardAddEvent")

A custom channel points reward has been created for the specified channel.

**Channel Points Custom Reward Update**

Function: [`listen_channel_points_custom_reward_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update "twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update")  
Payload: [`ChannelPointsCustomRewardUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardUpdateEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardUpdateEvent")

A custom channel points reward has been updated for the specified channel.

**Channel Points Custom Reward Remove**

Function: [`listen_channel_points_custom_reward_remove()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove "twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove")  
Payload: [`ChannelPointsCustomRewardRemoveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardRemoveEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardRemoveEvent")

A custom channel points reward has been removed from the specified channel.

**Channel Points Custom Reward Redemption Add**

Function: [`listen_channel_points_custom_reward_redemption_add()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add "twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add")  
Payload: [`ChannelPointsCustomRewardRedemptionAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionAddEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionAddEvent")

A viewer has redeemed a custom channel points reward on the specified channel.

**Channel Points Custom Reward Redemption Update**

Function: [`listen_channel_points_custom_reward_redemption_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update "twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update")  
Payload: [`ChannelPointsCustomRewardRedemptionUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionUpdateEvent "twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionUpdateEvent")

A redemption of a channel points custom reward has been updated for the specified channel.

**Channel Poll Begin**

Function: [`listen_channel_poll_begin()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin "twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin")  
Payload: [`ChannelPollBeginEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPollBeginEvent "twitchAPI.object.eventsub.ChannelPollBeginEvent")

A poll started on a specified channel.

**Channel Poll Progress**

Function: [`listen_channel_poll_progress()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress "twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress")  
Payload: [`ChannelPollProgressEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPollProgressEvent "twitchAPI.object.eventsub.ChannelPollProgressEvent")

Users respond to a poll on a specified channel.

**Channel Poll End**

Function: [`listen_channel_poll_end()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end "twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end")  
Payload: [`ChannelPollEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPollEndEvent "twitchAPI.object.eventsub.ChannelPollEndEvent")

A poll ended on a specified channel.

**Channel Prediction Begin**

Function: [`listen_channel_prediction_begin()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin "twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin")  
Payload: [`ChannelPredictionEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEvent "twitchAPI.object.eventsub.ChannelPredictionEvent")

A Prediction started on a specified channel.

**Channel Prediction Progress**

Function: [`listen_channel_prediction_progress()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress "twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress")  
Payload: [`ChannelPredictionEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEvent "twitchAPI.object.eventsub.ChannelPredictionEvent")

Users participated in a Prediction on a specified channel.

**Channel Prediction Lock**

Function: [`listen_channel_prediction_lock()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock "twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock")  
Payload: [`ChannelPredictionEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEvent "twitchAPI.object.eventsub.ChannelPredictionEvent")

A Prediction was locked on a specified channel.

**Channel Prediction End**

Function: [`listen_channel_prediction_end()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end "twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end")  
Payload: [`ChannelPredictionEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPredictionEndEvent "twitchAPI.object.eventsub.ChannelPredictionEndEvent")

A Prediction ended on a specified channel.

**Drop Entitlement Grant**

Function: [`listen_drop_entitlement_grant()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant "twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant")  
Payload: [`DropEntitlementGrantEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.DropEntitlementGrantEvent "twitchAPI.object.eventsub.DropEntitlementGrantEvent")

An entitlement for a Drop is granted to a user.

**Extension Bits Transaction Create**

Function: [`listen_extension_bits_transaction_create()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_extension_bits_transaction_create "twitchAPI.eventsub.base.EventSubBase.listen_extension_bits_transaction_create")  
Payload: [`ExtensionBitsTransactionCreateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ExtensionBitsTransactionCreateEvent "twitchAPI.object.eventsub.ExtensionBitsTransactionCreateEvent")

A Bits transaction occurred for a specified Twitch Extension.

**Goal Begin**

Function: [`listen_goal_begin()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_begin "twitchAPI.eventsub.base.EventSubBase.listen_goal_begin")  
Payload: [`GoalEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.GoalEvent "twitchAPI.object.eventsub.GoalEvent")

A goal begins on the specified channel.

**Goal Progress**

Function: [`listen_goal_progress()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_progress "twitchAPI.eventsub.base.EventSubBase.listen_goal_progress")  
Payload: [`GoalEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.GoalEvent "twitchAPI.object.eventsub.GoalEvent")

A goal makes progress on the specified channel.

**Goal End**

Function: [`listen_goal_end()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_goal_end "twitchAPI.eventsub.base.EventSubBase.listen_goal_end")  
Payload: [`GoalEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.GoalEvent "twitchAPI.object.eventsub.GoalEvent")

A goal ends on the specified channel.

**Hype Train Begin**

Function: [`listen_hype_train_begin()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_begin "twitchAPI.eventsub.base.EventSubBase.listen_hype_train_begin")  
Payload: [`HypeTrainEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.HypeTrainEvent "twitchAPI.object.eventsub.HypeTrainEvent")

A Hype Train begins on the specified channel.

**Hype Train Progress**

Function: [`listen_hype_train_progress()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_progress "twitchAPI.eventsub.base.EventSubBase.listen_hype_train_progress")  
Payload: [`HypeTrainEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.HypeTrainEvent "twitchAPI.object.eventsub.HypeTrainEvent")

A Hype Train makes progress on the specified channel.

**Hype Train End**

Function: [`listen_hype_train_end()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_hype_train_end "twitchAPI.eventsub.base.EventSubBase.listen_hype_train_end")  
Payload: [`HypeTrainEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.HypeTrainEvent "twitchAPI.object.eventsub.HypeTrainEvent")

A Hype Train ends on the specified channel.

**Stream Online**

Function: [`listen_stream_online()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_online "twitchAPI.eventsub.base.EventSubBase.listen_stream_online")  
Payload: [`StreamOnlineEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.StreamOnlineEvent "twitchAPI.object.eventsub.StreamOnlineEvent")

The specified broadcaster starts a stream.

**Stream Offline**

Function: [`listen_stream_offline()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_stream_offline "twitchAPI.eventsub.base.EventSubBase.listen_stream_offline")  
Payload: [`StreamOfflineEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.StreamOfflineEvent "twitchAPI.object.eventsub.StreamOfflineEvent")

The specified broadcaster stops a stream.

**User Authorization Grant**

Function: [`listen_user_authorization_grant()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_grant "twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_grant")  
Payload: [`UserAuthorizationGrantEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserAuthorizationGrantEvent "twitchAPI.object.eventsub.UserAuthorizationGrantEvent")

A user’s authorization has been granted to your client id.

**User Authorization Revoke**

Function: [`listen_user_authorization_revoke()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_revoke "twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_revoke")  
Payload: [`UserAuthorizationRevokeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserAuthorizationRevokeEvent "twitchAPI.object.eventsub.UserAuthorizationRevokeEvent")

A user’s authorization has been revoked for your client id.

**User Update**

Function: [`listen_user_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_update "twitchAPI.eventsub.base.EventSubBase.listen_user_update")  
Payload: [`UserUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserUpdateEvent "twitchAPI.object.eventsub.UserUpdateEvent")

A user has updated their account.

**Channel Shield Mode Begin**

Function: [`listen_channel_shield_mode_begin()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin "twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin")  
Payload: [`ShieldModeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ShieldModeEvent "twitchAPI.object.eventsub.ShieldModeEvent")

Sends a notification when the broadcaster activates Shield Mode.

**Channel Shield Mode End**

Function: [`listen_channel_shield_mode_end()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end "twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end")  
Payload: [`ShieldModeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ShieldModeEvent "twitchAPI.object.eventsub.ShieldModeEvent")

Sends a notification when the broadcaster deactivates Shield Mode.

**Channel Charity Campaign Start**

Function: [`listen_channel_charity_campaign_start()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_start "twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_start")  
Payload: [`CharityCampaignStartEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityCampaignStartEvent "twitchAPI.object.eventsub.CharityCampaignStartEvent")

Sends a notification when the broadcaster starts a charity campaign.

**Channel Charity Campaign Progress**

Function: [`listen_channel_charity_campaign_progress()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_progress "twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_progress")  
Payload: [`CharityCampaignProgressEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityCampaignProgressEvent "twitchAPI.object.eventsub.CharityCampaignProgressEvent")

Sends notifications when progress is made towards the campaign’s goal or when the broadcaster changes the fundraising goal.

**Channel Charity Campaign Stop**

Function: [`listen_channel_charity_campaign_stop()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_stop "twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_stop")  
Payload: [`CharityCampaignStopEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityCampaignStopEvent "twitchAPI.object.eventsub.CharityCampaignStopEvent")

Sends a notification when the broadcaster stops a charity campaign.

**Channel Charity Campaign Donate**

Function: [`listen_channel_charity_campaign_donate()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_donate "twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_donate")  
Payload: [`CharityDonationEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.CharityDonationEvent "twitchAPI.object.eventsub.CharityDonationEvent")

Sends a notification when a user donates to the broadcaster’s charity campaign.

**Channel Shoutout Create**

Function: [`listen_channel_shoutout_create()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create "twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create")  
Payload: [`ChannelShoutoutCreateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelShoutoutCreateEvent "twitchAPI.object.eventsub.ChannelShoutoutCreateEvent")

Sends a notification when the specified broadcaster sends a Shoutout.

**Channel Shoutout Receive**

Function: [`listen_channel_shoutout_receive()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive "twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive")  
Payload: [`ChannelShoutoutReceiveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelShoutoutReceiveEvent "twitchAPI.object.eventsub.ChannelShoutoutReceiveEvent")

Sends a notification when the specified broadcaster receives a Shoutout.

**Channel Chat Clear**

Function: [`listen_channel_chat_clear()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear")  
Payload: [`ChannelChatClearEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatClearEvent "twitchAPI.object.eventsub.ChannelChatClearEvent")

A moderator or bot has cleared all messages from the chat room.

**Channel Chat Clear User Messages**

Function: [`listen_channel_chat_clear_user_messages()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages")  
Payload: [`ChannelChatClearUserMessagesEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatClearUserMessagesEvent "twitchAPI.object.eventsub.ChannelChatClearUserMessagesEvent")

A moderator or bot has cleared all messages from a specific user.

**Channel Chat Message Delete**

Function: [`listen_channel_chat_message_delete()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete")  
Payload: [`ChannelChatMessageDeleteEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatMessageDeleteEvent "twitchAPI.object.eventsub.ChannelChatMessageDeleteEvent")

A moderator has removed a specific message.

**Channel Chat Notification**

Function: [`listen_channel_chat_notification()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification")  
Payload: [`ChannelChatNotificationEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatNotificationEvent "twitchAPI.object.eventsub.ChannelChatNotificationEvent")

A notification for when an event that appears in chat has occurred.

**Channel Chat Message**

Function: [`listen_channel_chat_message()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message")  
Payload: [`ChannelChatMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatMessageEvent "twitchAPI.object.eventsub.ChannelChatMessageEvent")

Any user sends a message to a specific chat room.

**Channel Ad Break Begin**

Function: [`listen_channel_ad_break_begin()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_ad_break_begin "twitchAPI.eventsub.base.EventSubBase.listen_channel_ad_break_begin")  
Payload: [`ChannelAdBreakBeginEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelAdBreakBeginEvent "twitchAPI.object.eventsub.ChannelAdBreakBeginEvent")

A midroll commercial break has started running.

**Channel Chat Settings Update**

Function: [`listen_channel_chat_settings_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update")  
Payload: [`ChannelChatSettingsUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatSettingsUpdateEvent "twitchAPI.object.eventsub.ChannelChatSettingsUpdateEvent")

A notification for when a broadcaster’s chat settings are updated.

**Whisper Received**

Function: [`listen_user_whisper_message()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message "twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message")  
Payload: [`UserWhisperMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.UserWhisperMessageEvent "twitchAPI.object.eventsub.UserWhisperMessageEvent")

A user receives a whisper.

**Channel Points Automatic Reward Redemption**

Function: [`listen_channel_points_automatic_reward_redemption_add()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add "twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add")  
Payload: [`ChannelPointsAutomaticRewardRedemptionAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelPointsAutomaticRewardRedemptionAddEvent "twitchAPI.object.eventsub.ChannelPointsAutomaticRewardRedemptionAddEvent")

A viewer has redeemed an automatic channel points reward on the specified channel.

**Channel VIP Add**

Function: [`listen_channel_vip_add()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add "twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add")  
Payload: [`ChannelVIPAddEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelVIPAddEvent "twitchAPI.object.eventsub.ChannelVIPAddEvent")

A VIP is added to the channel.

**Channel VIP Remove**

Function: [`listen_channel_vip_remove()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove "twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove")  
Payload: [`ChannelVIPRemoveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelVIPRemoveEvent "twitchAPI.object.eventsub.ChannelVIPRemoveEvent")

A VIP is removed from the channel.

**Channel Unban Request Create**

Function: [`listen_channel_unban_request_create()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create "twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create")  
Payload: [`ChannelUnbanRequestCreateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUnbanRequestCreateEvent "twitchAPI.object.eventsub.ChannelUnbanRequestCreateEvent")

A user creates an unban request.

**Channel Unban Request Resolve**

Function: [`listen_channel_unban_request_resolve()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve "twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve")  
Payload: [`ChannelUnbanRequestResolveEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelUnbanRequestResolveEvent "twitchAPI.object.eventsub.ChannelUnbanRequestResolveEvent")

An unban request has been resolved.

**Channel Suspicious User Message**

Function: [`listen_channel_suspicious_user_message()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message "twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message")  
Payload: [`ChannelSuspiciousUserMessageEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSuspiciousUserMessageEvent "twitchAPI.object.eventsub.ChannelSuspiciousUserMessageEvent")

A chat message has been sent by a suspicious user.

**Channel Suspicious User Update**

Function: [`listen_channel_suspicious_user_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update "twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update")  
Payload: [`ChannelSuspiciousUserUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSuspiciousUserUpdateEvent "twitchAPI.object.eventsub.ChannelSuspiciousUserUpdateEvent")

A suspicious user has been updated.

**Channel Moderate** v2

Function: [`listen_channel_moderate()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate "twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate")  
Payload: [`ChannelModerateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelModerateEvent "twitchAPI.object.eventsub.ChannelModerateEvent")

A moderator performs a moderation action in a channel. Includes warnings.

**Channel Warning Acknowledgement**

Function: [`listen_channel_warning_acknowledge()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge "twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge")  
Payload: [`ChannelWarningAcknowledgeEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelWarningAcknowledgeEvent "twitchAPI.object.eventsub.ChannelWarningAcknowledgeEvent")

A user awknowledges a warning. Broadcasters and moderators can see the warning’s details.

**Channel Warning Send**

Function: [`listen_channel_warning_send()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send "twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send")  
Payload: [`ChannelWarningSendEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelWarningSendEvent "twitchAPI.object.eventsub.ChannelWarningSendEvent")

A user is sent a warning. Broadcasters and moderators can see the warning’s details.

**Automod Message Hold**

Function: [`listen_automod_message_hold()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold "twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold")  
Payload: [`AutomodMessageHoldEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodMessageHoldEvent "twitchAPI.object.eventsub.AutomodMessageHoldEvent")

A user is notified if a message is caught by automod for review.

**Automod Message Update**

Function: [`listen_automod_message_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update "twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update")  
Payload: [`AutomodMessageUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodMessageUpdateEvent "twitchAPI.object.eventsub.AutomodMessageUpdateEvent")

A message in the automod queue had its status changed.

**Automod Settings Update**

Function: [`listen_automod_settings_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update "twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update")  
Payload: [`AutomodSettingsUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodSettingsUpdateEvent "twitchAPI.object.eventsub.AutomodSettingsUpdateEvent")

A notification is sent when a broadcaster’s automod settings are updated.

**Automod Terms Update**

Function: [`listen_automod_terms_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update "twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update")  
Payload: [`AutomodTermsUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.AutomodTermsUpdateEvent "twitchAPI.object.eventsub.AutomodTermsUpdateEvent")

A notification is sent when a broadcaster’s automod terms are updated. Changes to private terms are not sent.

**Channel Chat User Message Hold**

Function: [`listen_channel_chat_user_message_hold()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold")  
Payload: [`ChannelChatUserMessageHoldEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatUserMessageHoldEvent "twitchAPI.object.eventsub.ChannelChatUserMessageHoldEvent")

A user is notified if their message is caught by automod.

**Channel Chat User Message Update**

Function: [`listen_channel_chat_user_message_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update "twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update")  
Payload: [`ChannelChatUserMessageUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelChatUserMessageUpdateEvent "twitchAPI.object.eventsub.ChannelChatUserMessageUpdateEvent")

A user is notified if their message’s automod status is updated.

**Channel Shared Chat Session Begin**

Function: [`listen_channel_shared_chat_begin()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_begin "twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_begin")  
Payload: [`ChannelSharedChatBeginEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSharedChatBeginEvent "twitchAPI.object.eventsub.ChannelSharedChatBeginEvent")

A notification when a channel becomes active in an active shared chat session.

**Channel Shared Chat Session Update**

Function: [`listen_channel_shared_chat_update()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_update "twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_update")  
Payload: [`ChannelSharedChatUpdateEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSharedChatUpdateEvent "twitchAPI.object.eventsub.ChannelSharedChatUpdateEvent")

A notification when the active shared chat session the channel is in changes.

**Channel Shared Chat Session End**

Function: [`listen_channel_shared_chat_end()`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.eventsub.base.html#twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_end "twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_end")  
Payload: [`ChannelSharedChatEndEvent`](https://pytwitchapi.dev/en/stable/modules/twitchAPI.object.eventsub.html#twitchAPI.object.eventsub.ChannelSharedChatEndEvent "twitchAPI.object.eventsub.ChannelSharedChatEndEvent")

A notification when a channel leaves a shared chat session or the session ends.