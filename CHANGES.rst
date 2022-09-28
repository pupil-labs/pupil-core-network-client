1.0.0a4 (2022-09-28)
####################
- Add :py:meth:`pupil_labs.pupil_core_network_client.Device.high_frequency_message_sending`,
  a context manager that makes :py:meth:`pupil_labs.pupil_core_network_client.Device.send_message`
  more efficient by connecting directly to the IPC backend't PUB port instead of relaying
  messages via Pupil Remote.
- Experimental: Add opt-in auto-reconnect functionality to
  :py:class:`pupil_labs.pupil_core_network_client.Device` via ``should_auto_reconnect``
  argument.

1.0.0a3 (2022-03-25)
####################
- Add :py:meth:`pupil_labs.pupil_core_network_client.Device.request_plugin_start_eye_process`
  and accompanying example
- Remove ``setup.py``; requires pip 21.2+ for editable install
- Add :py:class:`pupil_labs.pupil_core_network_client.subscription.Subscription`,
  :py:class:`pupil_labs.pupil_core_network_client.subscription.BackgroundSubscription`,
  :py:meth:`pupil_labs.pupil_core_network_client.Device.subscribe`,
  :py:meth:`pupil_labs.pupil_core_network_client.Device.subscribe_in_background`,
  :py:class:`pupil_labs.pupil_core_network_client.subscription.Message`, and accompanying example

1.0.0a2 (2022-02-25)
####################

- Fix README badges
- tox: enable isolated builds

1.0.0a1 (2022-02-25)
####################

Initial functionality:

- Start/stop recordings
- Start/stop calibrations
- Request version
- Estimate clock offsets
- Send messages/notifications/annotations
- Start plugins
