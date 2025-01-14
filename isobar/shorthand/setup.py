from ..io.midi import MidiOutputDevice
from ..timeline import Timeline
from ..exceptions import DeviceNotFoundException
from .. import ALL_EVENT_PARAMETERS

try:
    from signalflow import *
    from ..io.signalflow import SignalFlowOutputDevice

    midi_output_device = MidiOutputDevice()
    timeline = Timeline(120, midi_output_device)
    timeline.add_output_device(midi_output_device)
    graph = AudioGraph()
    signalflow_output_device = SignalFlowOutputDevice(graph)
    signalflow_output_device.added_latency_seconds = 0.05
    timeline.ignore_exceptions = True
    timeline.background()

except (ModuleNotFoundError, DeviceNotFoundException):
    graph = None
    timeline = None


def track(name, **kwargs):
    global timeline

    #--------------------------------------------------------------------------------
    # Unflatten the params list.
    # This has some perils (e.g. 'amp' is used as an Event keyword but is 
    # also often used as a Patch parameter).
    #--------------------------------------------------------------------------------
    params = {}
    for key in list(kwargs.keys()):
        if key not in ALL_EVENT_PARAMETERS:
            params[key] = kwargs[key]
            del kwargs[key]
    
    if params:
        #--------------------------------------------------------------------------------
        # This caused the track to not generate any events when params was null,
        # not sure why
        #--------------------------------------------------------------------------------
        kwargs["params"] = params

    #--------------------------------------------------------------------------------
    # Automatically select the appropriate output device based on the event type.
    #--------------------------------------------------------------------------------
    if "patch" in kwargs:
        output_device = signalflow_output_device
    else:
        output_device = midi_output_device

    track = timeline.schedule(params=kwargs,
                              name=name,
                              replace=True,
                              quantize=1,
                              output_device=output_device)
    #--------------------------------------------------------------------------------
    # Evaluating a cell with a track() command with mute() appended to it causes
    # the track to be silenced.
    #
    # Re-evaluating the cell without mute() should then unmute the track.
    #--------------------------------------------------------------------------------
    track.is_muted = False

    return track
