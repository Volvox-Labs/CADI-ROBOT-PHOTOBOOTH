# pylint: disable=missing-docstring,logging-fstring-interpolation
from vvox_tdtools.base import BaseEXT
from vvox_tdtools.parhelper import ParTemplate
import json
try:
    # import td
    from td import OP # type: ignore
    # TDJ = op.TDModules.mod.TDJSON
    # TDF = op.TDModules.mod.TDFunctions
except ModuleNotFoundError:
    from vvox_tdtools.td_mock import OP  #pylint: disable=ungrouped-imports 
    # from tdconfig import TDJSON as TDJ
    # from tdconfig import TDFunctions as TDF


class OperatorBridgeEXT(BaseEXT):
    def __init__(self, myop: OP) -> None:
        BaseEXT.__init__(self, myop, par_callback_on=True)
        self._createControlsPage()
        self.Me.par.opshortcut = 'operator_bridge'
        self.ws_client = self.Me.par.Currentclient
        if self.ws_client:
            self.Me.op("webserver1").webSocketSendText(self.ws_client,json.dumps({"task":"startup","message": "connected"}))
        
        pass

    def OnInit(self):
        # return False if initialization fails
        return True

    def HandleNewClient(self,client):
        self.Me.par.Currentclient = client
        self.UpdateState(op.state_manager.par.State.eval())
        pass
    
    def HandleDisconnect(self, client):
        self.Logger.debug(f"Client disconnected: {client}")
        self.Me.par.Currentclient = ""
        pass

    def HandleOperatorHealthCheck(self):
        self.Me.par.Gotoperatorheartbeat = False
        self.Me.op("heartbeat_wait").par.start.pulse()
        self.Me.op("webserver1").webSocketSendText(self.ws_client,json.dumps({"task":"heartbeat", "message": "connected"}))
        pass
    
    def HandleOperatorHealthcheckTimeout(self):
        if not self.Me.par.Gotoperatorheartbeat:
            self.Me.par.Operatorconnected = False
        pass
    
    def HandleReceiveText(self,client, data):
        if not data or data == "null":
            return
        try:
            message = json.loads(data)
        except (TypeError, ValueError):
            self.Logger.debug(f"Received non-JSON text from {client}: {data}")
            return

        if message.get("type") == "set_height_mode":
            self._handleSetHeightMode(message.get("mode"))
        elif message.get("type") in ("capture_request", "retake_capture"):
            # Stashed here so upload_control_thread_manager_callbacks.Setup() can
            # read it later (on the main thread) and reuse it as the manifest's
            # takeaway id, instead of that script minting its own uuid. Single
            # par because only one playthrough is ever in flight at a time.
            self.Me.par.Currentplaythroughid = message.get("playthroughId") or ""
            op.state_manager.par.Startphotobooth.pulse()
        elif message.get("type") == "estop":
            op.state_manager.par.Stopphotobooth.pulse()
        elif message.get("type") == "home_robot":
            op.state_manager.HomeRobot()

        pass

    def _handleSetHeightMode(self, mode):
        height = {"normal": "Standard", "low": "Low"}.get(mode)
        if height is None:
            self.Logger.debug(f"Ignoring unknown height mode: {mode}")
            return
        # Triggers state_manager's existing _onHeight OSC logic. There's no
        # completion signal from the robot yet, so we don't reply with
        # movement_done here - the operator UI's 7s modal timeout covers it
        # until real completion detection is added.
        op.state_manager.par.Height = height
        pass
    
    def HandleRobotCycleComplete(self):
        self.Me.op("webserver1").webSocketSendText(self.ws_client,json.dumps({"task":"status", "message": "robot_cycle_completed"}))


    def UpdateState(self,state_val):
        self.Me.op("webserver1").webSocketSendText(self.ws_client,json.dumps({"task":"status", "message": state_val}))

    # Below is an example of a parameter callback. Simply create a method that starts with "_on" and then the name of the parameter.

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
        status_par = ParTemplate('Status', par_type='Str', label='Status')
        status_par.readOnly = True
        status_par.default = "inactive" 
        current_client_par = ParTemplate('CurrentClient', par_type='Str', label='Current Client')
        current_client_par.readOnly = True
        operator_connected = ParTemplate("OperatorConnected", par_type='Toggle', label='OperatorConnected')
        operator_connected.readOnly = True
        got_operator_heartbeat = ParTemplate("GotOperatorHeartbeat", par_type='Toggle', label='GotOperatorHeartbeat')
        got_operator_heartbeat.readOnly = True
        current_playthrough_id = ParTemplate("CurrentPlaythroughId", par_type='Str', label='Current Playthrough Id')
        current_playthrough_id.readOnly = True
        pars = [
            status_par,
            current_client_par,
            operator_connected,
            got_operator_heartbeat,
            current_playthrough_id
        ]
        for par in pars:
            par.createPar(page)

        pass

