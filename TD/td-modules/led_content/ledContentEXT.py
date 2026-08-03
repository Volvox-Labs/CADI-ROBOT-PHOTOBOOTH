# pylint: disable=missing-docstring,logging-fstring-interpolation
from vvox_tdtools.base import BaseEXT
from vvox_tdtools.parhelper import ParTemplate
from vvox_tdtools.preset_base import PresetBaseEXT

try:
    # import td
    from td import OP, op, parent # type: ignore
    # TDJ = op.TDModules.mod.TDJSON
    # TDF = op.TDModules.mod.TDFunctions
except ModuleNotFoundError:
    from vvox_tdtools.td_mock import OP, ParMode, op, parent  #pylint: disable=ungrouped-imports 
    # from tdconfig import TDJSON as TDJ
    # from tdconfig import TDFunctions as TDF
class LedContentEXT(PresetBaseEXT):
    def __init__(self, myop: OP) -> None:
        PresetBaseEXT.__init__(self, myop, par_mode=ParMode)
        self.num_pixels = 84
        self._createControlsPage()
        pass

    def OnInit(self):
        # return False if initialization fails
        return True

    # Below is an example of a parameter callback. Simply create a method that starts with "_on" and then the name of the parameter.

    # def _onExampletoggle(self, par):
    #     self.Logger.debug(f"_onExampleToggle - val: {par.eval()}")
    #     pass

    # Below is an example of creating an event loop by overriding the OnFrameStart method.

    # def OnFrameStart(self, frame: int):
    #     if frame % 60 == 0:
    #         self.OnEventLoop1()
    #     return 

    # def OnEventLoop1(self):
    #     self.Print('every second')
    #     pass


    def _createControlsPage(self) -> None:
        page = self.GetPage('Controls')
        
        num_pixels_par = ParTemplate("NumPixels", par_type="Int", label="NumPixels")
        num_pixels_par.val = self.num_pixels
        num_pixels_par.readOnly = True
        breath_options = ParTemplate("BreathingTypeOptions",par_type="Menu",label="BreathingTypeOptions")
        breath_options.menuLabels = ["Full Breath", "Double breath", "Hold Breath" ]
        breath_options.menuNames = ["breath1", "breath2", "breath3"]
        # pulse_options = ParTemplate("PulseTypeOptions",par_type="Menu",label="PulseTypeOptions")
        # pulse_options.menuLabels = ["Pulse1", "Pulse2", "Pulse3" ]
        # pulse_options.menuNames = ["pulse1", "pulse2", "pulse3"]

        zone_animation = ParTemplate("ZoneAnimation",par_type="Menu",label="Zone Animation")
        zone_animation.menuLabels = ["Breathing", "Sparkle", "Chase" ]
        zone_animation.menuNames = ["breathing", "sparkle", "chase"]


        pars = [
            num_pixels_par,
            zone_animation,
            ParTemplate("BreathingMix", par_type="Float", label="BreathingMix"),
            ParTemplate("SparkleMix", par_type="Float", label="SparkleMix"),
            ParTemplate("ChaseMix", par_type="Float", label="ChaseMix"),

            ParTemplate("color1", par_type="RGBA",label='Color1'),
            ParTemplate("Color2", par_type="RGBA",label='Color2'),
            ParTemplate("Color3", par_type="RGBA",label='Color3'),
            ParTemplate("Color4", par_type="RGBA",label='Color4'),
            ParTemplate("Color5", par_type="RGBA",label='Color5'),
            ParTemplate("ZoneColor1", par_type="RGBA",label='ZoneColor1'),
            ParTemplate("ZoneColor2", par_type="RGBA",label='ZoneColor2'),
            ParTemplate("BaseColor", par_type="RGBA",label='BaseColor'),

            # All Scenes 
            ParTemplate('Brightness', par_type='Float', label='Brightness'),
            #Breath & Earth
            ParTemplate("HighThreshold", par_type="Float",label="HighThreshold"),
            ParTemplate("LowThreshold", par_type="Float",label="LowThreshold"),
            ParTemplate("BreathSpeed", par_type="Float", label="BreathSpeed"),
            ParTemplate("MultiColorMode",par_type="Toggle",label="MultiColorMode"),
            breath_options,
            ParTemplate("SelectedBreath", par_type="Float", label="SelectedBreath"),

            #Pulse & Flow
            ParTemplate("CometHead", par_type="Float", label="CometHead"),
            ParTemplate("CometTail", par_type="Float", label="CometTail"),
            ParTemplate("Tempo", par_type="Float", label="Tempo"),
            ParTemplate("TempoOffset", par_type="Float", label="TempoOffset"),
            ParTemplate("Altsweep", par_type="Toggle", label="Altsweep"),
            ParTemplate("IsClockwise", par_type="Toggle", label="IsClockwise"),
            # pulse_options,
            # ParTemplate("PulseFreqeuncey", par_type="Float", label="PulseFrequency"),

            # ParTemplate("SelectedPulse", par_type="Float", label="SelectedPulse"),
            
            #Light & Air
            ParTemplate("NumBubbles", par_type="Int",label="NumBubbles"),
            ParTemplate("SparkleSpeed", par_type="Float", label="SparkleSpeed")

        ]

        for par in pars:
            par.createPar(page)

        pass