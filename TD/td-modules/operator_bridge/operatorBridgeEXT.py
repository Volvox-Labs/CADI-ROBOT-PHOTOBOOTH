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
        # No cached client here on purpose -- see _send(). This used to hold
        # self.Me.par.Currentclient, which is the *parameter object*, not the
        # client id string, and was captured once at init and never refreshed.
        self._send({"task": "startup", "message": "connected"})

        pass

    def OnInit(self):
        # return False if initialization fails
        return True

    def _send(self, payload, server_op=None):
        """Send a JSON message to the currently-connected operator client.

        Resolves the client id from the parameter on every call instead of
        caching one. A cached client goes stale the instant the app reconnects --
        and the app reconnects on every page refresh -- after which every send
        addresses a socket that no longer exists.

        Failures are logged and swallowed deliberately. HandleNewClient sends
        from inside the websocket *open* callback, so an exception raised here
        propagates out of onWebSocketOpen and TouchDesigner aborts the
        handshake: the client connects and disconnects in the same frame, which
        is exactly the symptom this fixes. A send failing is a normal race (the
        client can vanish between frames) and must never be able to drop a
        connection.

        Returns True if the message was handed to the DAT.
        """
        client = self.Me.par.Currentclient.eval()
        if not client:
            self.Logger.debug(f"No operator client connected; dropped {payload.get('task')!r}")
            return False

        server = server_op if server_op is not None else self.Me.op("webserver1")
        try:
            server.webSocketSendText(client, json.dumps(payload))
            return True
        except Exception as exc:  # pylint: disable=broad-except
            # Broad on purpose: whatever TD raises for an unknown/closed client,
            # the connection matters more than the message.
            self.Logger.debug(f"Send to {client} failed ({exc}); dropped {payload.get('task')!r}")
            return False

    def HandleNewClient(self,client):
        self.Logger.debug(f"Got a new Client!: {client}")
        self.Me.par.Currentclient = client
        self.UpdateState(op.state_manager.par.State.eval())
        pass
    
    def HandleDisconnect(self, client):
        self.Logger.debug(f"Client disconnected: {client}")
        # Only clear if the client that left is the one we're holding. On iOS a
        # refresh leaves the old socket half-open while the replacement is
        # already connecting, so disconnects routinely arrive AFTER the new
        # client has been registered -- an unconditional clear would wipe the
        # live client and leave us unable to send to anyone.
        if client == self.Me.par.Currentclient.eval():
            self.Me.par.Currentclient = ""
        pass

    def HandleOperatorHealthCheck(self):
        self.Me.par.Gotoperatorheartbeat = False
        self.Me.op("heartbeat_wait").par.start.pulse()
        self._send({"task": "heartbeat", "message": "connected"})
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
            # Showroom staff runs are excluded from analytics everywhere -- here,
            # in the kiosk, and on the microsite. Read with a plain get() so an
            # Operator app on an older build (no such key) falls back to False,
            # i.e. treated as a guest and tracked exactly as it is today.
            is_showroom_staff = bool(message.get("isShowroomStaff"))
            self.Me.par.Isshowroomstaff = is_showroom_staff
            op.state_manager.par.Startphotobooth.pulse()
            if not is_showroom_staff:
                op.analytics_control.Send_mixpanel_event("Photo Booth Start")
        elif message.get("type") == "estop":
            op.state_manager.par.Stopphotobooth.pulse()
        elif message.get("type") == "home_robot":
            op.state_manager.HomeRobot()
        elif message.get("type") == "complete_capture":
            # complete_capture carries no payload, so the flag has to come from the
            # par stashed at capture time rather than from the message.
            if not self.Me.par.Isshowroomstaff.eval():
                op.analytics_control.Send_mixpanel_event("Capture Complete")

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
        self._send({"task": "status", "message": "robot_cycle_completed"})


    def UpdateState(self,state_val):
        # Called from HandleNewClient, i.e. from inside the websocket open
        # callback -- which is why _send() must never raise. See _send().
        self._send({"task": "status", "message": state_val})


    def HandleUploaderHealthCheck(self):
        self.Me.par.Gotuploaderheartbeat = False
        # NOTE: shares heartbeat_wait with HandleOperatorHealthCheck, so the two
        # healthchecks overwrite each other's timeout window. Left as-is because
        # splitting them needs a second timer inside the .tox.
        self.Me.op("heartbeat_wait").par.start.pulse()
        # KNOWN BROKEN, now failing quietly instead of raising: this addresses
        # upload_control's webserver DAT but with the *operator's* client id, and
        # a client id from one Web Server DAT means nothing to another. It needs
        # upload_control to expose its own connected client before it can work.
        self._send({"task": "heartbeat", "message": "connected"},
                   server_op=op.upload_control.op("webserver1"))
        pass
    
    def HandleUploaderHealthcheckTimeout(self):
        if not self.Me.par.Gotuploaderheartbeat:
            self.Me.par.Uploaderconnected = False
        pass
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
        # Set from the Operator app's "Guest is showroom staff" checkbox. Read back
        # by upload_control_thread_manager_callbacks.Setup() so it reaches Postgres
        # and the QR URL. Same single-par-per-playthrough assumption as the id above.
        is_showroom_staff = ParTemplate("IsShowroomStaff", par_type='Toggle', label='Is Showroom Staff')
        is_showroom_staff.readOnly = True
        pars = [
            status_par,
            current_client_par,
            operator_connected,
            got_operator_heartbeat,
            current_playthrough_id,
            is_showroom_staff
        ]
        for par in pars:
            par.createPar(page)

        pass

