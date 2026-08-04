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
        self.Logger.debug("Starting Countdown and Photobooth")
        op.camera_control.par.Startcountdown.pulse()
        self.Me.par.State = "COUNTDOWN"
        op.poster_control.par.Recordtakeaway.pulse()
        pass

    def _onStopphotobooth(self, par):
        self.Logger.debug("E STOP HIT")
        self.Me.par.State = "E-STOP"
        self.Me.op("oscout1").sendOSC("/remote", ["op.animation_player.par.Stop.pulse()"])
        pass

    def StartRobot(self):
        #standard 3 
        
        # self.Me.op("oscout1").sendOSC("/remote", ["op.animation_player.par.Play.pulse()"])
        self.Me.op("oscout1").sendOSC("/remote", ["op.animation_player.par.Play.pulse()"])
        pass

    def _onHeight(self,par):
        if (par) == "Standard":
            val = 3
        elif par == "Low":
            val = 2
        else:
            val = 1
        print(val)
        self.Me.op("oscout1").sendOSC("/remote" , [f'setattr(op.animation_player.par,"Animationindex",{val})'])
        self.Me.op("oscout1").sendOSC("/remote", ["op.animation_player.par.Gotofirstframe.pulse()"])
        pass
    # Below is an example of creating an event loop by overriding the OnFrameStart method.

    def HandlevalueChange(self,channel, sampleIndex, val, prev):
        recording_state = self.Me.op("null2")["Recording"]
        show_state = self.Me.op("null2")["show_state"]
        progress_state = self.Me.op("oscin1")["Progress"]
        backend_state = self.Me.op("oscin1")["backend_state"]
        if self.Me.par.State == "E-STOP":
            if backend_state == 0.0:
                self.Me.par.State.val = "READY"
                return
        if progress_state == 1.0 and recording_state == 0.0 and show_state == 2.0:
            self.Me.par.State = "HOMING_ROBOT"
        elif recording_state == 1.0 and show_state == 1.0:
            self.Me.par.State = "ROBOT_RECORDING"
        elif recording_state == 0.0 and show_state == 3.0 and self.Me.par.State.val != "COUNTDOWN":
            self.Me.par.State = "CYCLE_COMPLETE"
            op.operator_bridge.HandleRobotCycleComplete()
        pass

    def _onState(self):
        op.operator_bridge.UpdateState(self.Me.par.State.eval())


    def HomeRobot(self):
        self.Me.op("oscout1").sendOSC("/remote", ["op.animation_player.par.Gotofirstframe.pulse()"])
    # def OnFrameStart(self, frame: int):
    #     if frame % 60 == 0:
    #         self.OnEventLoop1()
    #     return 

    # def OnEventLoop1(self):
    #     self.Print('every second')
    #     pass


    def _createControlsPage(self) -> None:
        page = self.GetPage('Controls')
        state = ParTemplate("State",par_type="Str",label="State")
        state.readOnly = True
        pars = [
            ParTemplate('StartPhotobooth', par_type='Pulse', label='StartPhotobooth'),
            ParTemplate('StopPhotobooth', par_type='Pulse', label='StopPhotobooth'),
            ParTemplate('HomeRobot', par_type='Pulse', label='HomeRobot'),
            state
        ]
        for par in pars:
            par.createPar(page)

        pass

