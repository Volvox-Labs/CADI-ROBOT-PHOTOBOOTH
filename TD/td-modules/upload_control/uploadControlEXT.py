# pylint: disable=missing-docstring,logging-fstring-interpolation
import queue

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


class UploadControlEXT(BaseEXT):
    def __init__(self, myop: OP) -> None:
        BaseEXT.__init__(self, myop, par_callback_on=True)
        # Owned here rather than in the callbacks DAT: a module-level queue would be
        # swapped out whenever that DAT re-cooks mid-upload, orphaning in-flight events.
        # The worker gets a reference via GetProgressQueue() in Setup().
        self._progress = queue.Queue()
        self._createControlsPage()
        self.Me.par.opshortcut = 'upload_control'
        #TODO this should just be set via state control
        pass

    def OnInit(self):
        # return False if initialization fails
        return True

    def HandleFailedUpload(self, message: str = "") -> None:
        """Terminal failure handling for a run.

        Deliberately does NOT touch the in-booth guest scenes any more. The version
        this replaces (operator_interface_bridge.py, deleted in b31b338) drove
        photo_capture.Showerrormessage and state_control.HandleRetryExperience(), but
        the guest flow now lives in the web kiosk -- retrying a TD scene on a failed
        upload would be reacting to something no guest is looking at.
        """
        self.Logger.error(f"Handling failed upload: {message}")
        self.Me.par.Stage = "error"
        if message:
            self.Me.par.Lasterror = message

    def HandleUploadResult(self, result):
        if not result:
            self.Logger.debug("HandleUploadResult called with no result")
            return
        status = result.get("status")
        if status == "video_upload_success":
            self.Logger.debug("Video Upload Successful")
            # Restores what 90e2542 dropped. The qr_code_path wiring from that same
            # commit is intentionally not restored -- qrcode_scene is no longer part
            # of the guest flow -- but the coarse status vocabulary still needs to
            # reach "complete", since that's what stateControlEXT resets from.
            op.upload_control.par.Status = "complete"
        elif status == "video_upload_error":
            op.upload_control.par.Status = "error"
            self.Logger.debug(f"Video upload failed: {result.get('message')}")
            self.HandleFailedUpload(result.get("message", ""))
        else:
            self.Logger.debug(f"Received unknown upload result: {result}")

    def HandleUploadException(self, args):
        # The worker died before it could report anything -- most likely
        # _complete_playthrough's raise_for_status(), which has no _report() around it.
        self.Logger.error(f"Upload thread raised an exception: {args}")
        op.upload_control.par.Status = "error"
        self.HandleFailedUpload(str(args))

    def GetTakeawayFileName(self):
        colors = ["blue","red","white","yellow"]
        selected_poster_index = int(op.photo_select.par.Selectedphoto.eval()) - 1
        return op.poster_control.par.Takeawayoutputpath + colors[selected_poster_index] + "_" + op.poster_control.par.Filename

    def _onUploadvideo(self):
        movie = self.Me.par.Filepath.eval()
        self.Logger.debug(f"uploading movie: {movie}")
        # Reset per run so the pars and log describe this takeaway, not the last one.
        # Lasterror included: it only sticks for the duration of a run.
        self.Me.par.Stage = "queued"
        self.Me.par.Progress = 0
        self.Me.par.Statusmessage = ""
        self.Me.par.Lasterror = ""
        op.upload_control.par.Status = "processing"
        self.Me.op("threadManagerClient").par.Runinthread.pulse()
        self.Logger.debug("started upload thread")
        pass

    # Below is an example of a parameter callback. Simply create a method that starts with "_on" and then the name of the parameter.

    # def _onExampletoggle(self, par):
    #     self.Logger.debug(f"_onExampleToggle - val: {par.eval()}")
    #     pass

    # --- progress reporting ------------------------------------------------
    # The upload runs on a background thread, which may not touch ANY TD object --
    # including self.Logger, whose formatter reads absTime.frame. So the worker only
    # ever puts plain dicts on this queue, and everything that touches the network or
    # the log happens here, on the main thread.

    def GetProgressQueue(self):
        """Handed to the worker thread by the callbacks DAT's Setup()."""
        return self._progress

    def OnFrameStart(self, frame: int):
        # Runs 60x/sec, so the empty check matters -- it's the common case by far.
        if self._progress.empty():
            return
        while True:
            try:
                self._applyProgress(self._progress.get_nowait())
            except queue.Empty:
                break

    def _applyProgress(self, event) -> None:
        stage = event.get("stage", "")
        message = event.get("message", "")
        level = event.get("level", "info")

        self.Me.par.Stage = stage
        # None means "hold whatever we had" -- an error shouldn't snap the bar to zero.
        if event.get("progress") is not None:
            self.Me.par.Progress = event["progress"]
        self.Me.par.Statusmessage = message
        if level == "error":
            self.Me.par.Lasterror = message

        # The durable record: this goes through vvox_tdtools' rotating file handler,
        # frame number attached. The pars above cover at-a-glance current state, so
        # there's deliberately no on-network table duplicating this.
        log = getattr(self.Logger, level, self.Logger.info)
        log(f"[{stage}] {message}")


    def _createControlsPage(self) -> None:
        page = self.GetPage('Controls')
        status_par = ParTemplate('Status', par_type='Str', label='Status')
        status_par.readOnly = True
        status_par.default = "inactive"

        # Fine-grained companions to Status, driven by the worker's stage events.
        # Status keeps its coarse inactive/processing/complete/error vocabulary --
        # stateControlEXT.py:43,54 depend on it.
        stage_par = ParTemplate('Stage', par_type='Str', label='Stage')
        stage_par.readOnly = True
        stage_par.default = ""

        progress_par = ParTemplate('Progress', par_type='Float', label='Progress')
        progress_par.readOnly = True
        progress_par.normMin = 0
        progress_par.normMax = 1
        progress_par.default = 0

        message_par = ParTemplate('StatusMessage', par_type='Str', label='StatusMessage')
        message_par.readOnly = True
        message_par.default = ""

        # Deliberately NOT cleared on success, so a failure is still readable afterwards.
        error_par = ParTemplate('LastError', par_type='Str', label='LastError')
        error_par.readOnly = True
        error_par.default = ""

        pars = [
            ParTemplate('UploadVideo', par_type='Pulse', label='UploadVideo'),
            status_par,
            stage_par,
            progress_par,
            message_par,
            error_par,
            ParTemplate("FilePath",par_type="File",label="FilePath"),
            ParTemplate("AudioFilePath",par_type="File", label="AudioFilePath")

        ]
        for par in pars:
            par.createPar(page)

        pass

