""" Unit tests for Track """

import isobar as iso
import pytest
from . import dummy_timeline

@pytest.fixture()
def dummy_track():
    return iso.Track(output_device=iso.io.DummyOutputDevice())

def test_track(dummy_timeline):
    track = iso.Track(dummy_timeline, {
        iso.EVENT_NOTE: iso.PSequence([], 0)
    })
    track.tick()
    assert track.is_finished

def test_track_update(dummy_timeline):
    #--------------------------------------------------------------------------------
    # Test that a track can be updated properly.
    #  - Track should continue playing its current events until precisely the
    #    quantized time of the update.
    #  - Should also catch the case in which the current event stream finishes
    #    at exactly the scheduled time, to ensure that the track does not mistakenly
    #    set its `is_finished` flag and terminate.
    #  - Should also catch the case in which two updates are scheduled for the same
    #    tick, in which the last update takes precedence
    #--------------------------------------------------------------------------------
    track = dummy_timeline.schedule({
        iso.EVENT_NOTE: iso.PSequence([50], 4),
    }, count=20)
    dummy_timeline.tick()

    # This update is later obsoleted
    track.update({
        iso.EVENT_NOTE: iso.PSequence([70], 4),
    }, quantize=4)
    dummy_timeline.tick()

    # This update takes precedence over the previous update
    track.update({
        iso.EVENT_NOTE: iso.PSequence([60], 4),
    }, quantize=4)

    dummy_timeline.run()
    assert dummy_timeline.output_device.events == [
        [0, 'note_on', 50, 64, 0], [1, 'note_off', 50, 0],
        [1, 'note_on', 50, 64, 0], [2, 'note_off', 50, 0],
        [2, 'note_on', 50, 64, 0], [3, 'note_off', 50, 0],
        [3, 'note_on', 50, 64, 0], [4, 'note_off', 50, 0],
        [4, 'note_on', 60, 64, 0], [5, 'note_off', 60, 0],
        [5, 'note_on', 60, 64, 0], [6, 'note_off', 60, 0],
        [6, 'note_on', 60, 64, 0], [7, 'note_off', 60, 0],
        [7, 'note_on', 60, 64, 0], [8, 'note_off', 60, 0],

    ]
    assert track.is_finished