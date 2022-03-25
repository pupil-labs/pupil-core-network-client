1.0.0a3 (2020-03-25)
####################
- Add :py:meth:`pupil_labs.pupil_core_network_client.Device.request_plugin_start_eye_process`
  and accompanying example
- Remove ``setup.py``; requires pip 21.2+ for editable install
- Add :py:class:`pupil_labs.pupil_core_network_client.subscription.Subscription`,
  :py:class:`pupil_labs.pupil_core_network_client.subscription.BackgroundSubscription`,
  :py:meth:`pupil_labs.pupil_core_network_client.Device.subscribe`,
  :py:meth:`pupil_labs.pupil_core_network_client.Device.subscribe_in_background`,
  :py:class:`pupil_labs.pupil_core_network_client.subscription.Message`, and accompanying example

1.0.0a2 (2020-02-25)
####################

- Fix README badges
- tox: enable isolated builds

1.0.0a1 (2020-02-25)
####################

Initial functionality:

- Start/stop recordings
- Start/stop calibrations
- Request version
- Estimate clock offsets
- Send messages/notifications/annotations
- Start plugins
