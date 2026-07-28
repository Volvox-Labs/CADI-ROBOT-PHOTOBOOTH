# pylint: disable=missing-docstring,logging-fstring-interpolation
from vvox_tdtools.base import BaseEXT
from vvox_tdtools.parhelper import ParTemplate
try:
    # import td
    from td import OP # type: ignore
    # TDJ = op.TDModules.mod.TDJSON
    # TDF = op.TDModules.mod.TDFunctions
except ModuleNotFoundError:
    from vvox_tdtools.td_mock import OP  #pylint: disable=ungrouped-imports 
    # from tdconfig import TDJSON as TDJ
    # from tdconfig import TDFunctions as TDF


class StateManagerEXT(BaseEXT):
    def __init__(self, myop: OP) -> None:
        BaseEXT.__init__(self, myop, par_callback_on=True)
        self._createControlsPage()
        self.Me.par.opshortcut = "state_manager"
        pass

    def OnInit(self):
        # return False if initialization fails
        return True

    # Below is an example of a parameter callback. Simply create a method that starts with "_on" and then the name of the parameter.

    def _onStartphotobooth(self, par):
        self.Logger.debug(f"_onExampleToggle - val: {par.eval()}")
        op.camera_control.par.Startcountdown.pulse()
        op.poster_control.par.Recordtakeaway.pulse()
        pass

    def StartRobot(self):
        self.Me.op("oscout1").sendOSC("/remote", ["op.animation_player.par.Play.pulse()"])
        pass

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
        pars = [
            ParTemplate('StartPhotobooth', par_type='Pulse', label='StartPhotobooth'),

        ]
        for par in pars:
            par.createPar(page)

        pass

