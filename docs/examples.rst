:tocdepth: 2

.. _examples:

Example usage
*************

To run the examples, install the package using the ``examples`` extras requirement::

   pip install -e pupil-core-network-client[examples]

Connect, and start and stop a recording
"""""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/basic.py
   :language: python
   :linenos:
   :emphasize-lines: 8,10,11,14

Print the estimated clock offset and current Pupil time
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/estimated_clock_offset.py
   :language: python
   :linenos:
   :emphasize-lines: 10,11,14

Start the Annotation Plugin and send custom annotions
"""""""""""""""""""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/send_annotations.py
   :language: python
   :linenos:
   :emphasize-lines: 12,19,26-28,35-37

Stream Video From Pupil Capture
"""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/receive_scene_video_frames.py
   :language: python
   :linenos:
   :emphasize-lines: 10,11-13,16,18,20-21


Stream Video to Pupil Capture
"""""""""""""""""""""""""""""

This example shows how start world and eye plugins and streaming BGR data to Pupil
Capture's HMD Streaming backend.

.. literalinclude:: ../examples/hmd_streaming.py
   :language: python
   :linenos:
   :emphasize-lines: 12,16,18-20,38
