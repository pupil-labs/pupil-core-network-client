:tocdepth: 2

.. _api:

Module API
**********

The main entrypoint of the API is the
:py:class:`Device <pupil_labs.pupil_core_network_client.Device>` class. You can use it
to

- connect to a Pupil Capture or Pupil Service instance,
- start and stop `recordings`_
- start and stop `calibrations`_
- start `plugins`_
- send messages to the `IPC backend`_
- send `notifications`_
- send `annotations`_

.. _recordings: https://docs.pupil-labs.com/core/software/pupil-capture/#recording
.. _calibrations: https://docs.pupil-labs.com/core/software/pupil-capture/#calibration
.. _plugins: https://docs.pupil-labs.com/core/software/pupil-capture/#plugins
.. _IPC backend: https://docs.pupil-labs.com/developer/core/network-api/#ipc-backbone
.. _notifications: https://docs.pupil-labs.com/developer/core/network-api/#notification-message
.. _annotations: https://docs.pupil-labs.com/developer/core/network-api/#remote-annotations

.. autoclass:: pupil_labs.pupil_core_network_client.Device
    :members:
    :undoc-members:
    :show-inheritance:

The device class calculates the clock offset between the
:py:attr:`client clock <pupil_labs.pupil_core_network_client.Device.client_clock>` and
the pupil time base of the connected Pupil Core software. To account for varying network
delay, it performs multiple measurements. The resulting statistics are exposed via the
:py:attr:`clock_offset_statistics <pupil_labs.pupil_core_network_client.Device.clock_offset_statistics>`
attibute.

.. autoclass:: pupil_labs.pupil_core_network_client.ClockOffsetStatistics
    :members:
    :undoc-members:
    :show-inheritance:

Subscriptions are implemented in :py:mod:`pupil_labs.pupil_core_network_client.subscription`.
Use :py:meth:`pupil_labs.pupil_core_network_client.Device.subscribe` and
:py:meth:`pupil_labs.pupil_core_network_client.Device.subscribe_in_background` as entry
points.

.. automodule:: pupil_labs.pupil_core_network_client.subscription
    :members:
    :undoc-members:
    :show-inheritance:
