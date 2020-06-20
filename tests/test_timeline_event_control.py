""" Unit tests for events """

import isobar as iso
import pytest
from . import dummy_timeline

def test_event_control_no_interpolation(dummy_timeline):
    """
    Simple case: schedule a series of regularly-spaced control points.
    Output device should receive discrete control events.
    """
    control_series = iso.PSeries(start=1, step=2, length=3)
    dummy_timeline.schedule({
        iso.EVENT_CONTROL: 0,
        iso.EVENT_VALUE: control_series,
        iso.EVENT_DURATION: 1,
        iso.EVENT_CHANNEL: 9
    })
    dummy_timeline.run()
    assert dummy_timeline.output_device.events == [
        [0, "control", 0, 1, 9],
        [1, "control", 0, 3, 9],
        [2, "control", 0, 5, 9]
    ]

@pytest.mark.skip
def test_event_control_linear_interpolation(dummy_timeline):
    """
    Linear interpolation between control points.
    """
    control_series = iso.PSequence([1, 3, 2], 1)
    dummy_timeline.schedule({
        iso.EVENT_CONTROL: 0,
        iso.EVENT_VALUE: control_series,
        iso.EVENT_DURATION: iso.PSequence([1, 0.5]),
        iso.EVENT_CHANNEL: 9
    }, interpolation=iso.INTERPOLATION_LINEAR)
    dummy_timeline.run()
    assert len(dummy_timeline.output_device.events) == dummy_timeline.ticks_per_beat * 1.5

@pytest.mark.skip
def test_event_control_cosine_interpolation(dummy_timeline):
    """
    Linear interpolation between control points.
    """
    alternator = iso.PAlternator()
    dummy_timeline.schedule({
        iso.EVENT_CONTROL: 0,
        iso.EVENT_VALUE: alternator,
        iso.EVENT_CHANNEL: 9
    }, interpolation=iso.INTERPOLATION_COSINE, stop_after=5)
    dummy_timeline.run()
