# Plan: real status reporting from the upload worker thread

> Status: **implemented 2026-08-18** (sections 1–3). Written 2026-08-10; the code below is
> the original plan and some of it is now out of date — read this note before trusting it.
> Touches `upload_control`, the Thread Manager callbacks, and the QR success path.
>
> Deviations from the plan as written, all deliberate:
>
> - **Line numbers in §1's table are stale.** The callbacks file grew from ~11 print sites
>   to 17 between writing and implementing. The conversion was done by matching print text.
> - **Two stages were added** that postdate the plan: `prepending`/`prepended`
>   (`_prepend_frame`, a second ffmpeg pass) and `publishing`/`published`
>   (`_publish_to_share`, three SMB copies to the kiosk PC). `STAGES` was reweighted around
>   them; the shipped table is the one in the code, not the one below.
> - **§3 was reduced.** The in-booth guest scenes are dead — the web kiosk owns the guest
>   flow — so `qrcode_scene`, `Showqrcode`, the `timeout_timer` pulse and
>   `photo_capture.Showerrormessage` were **not** wired. What was restored is the status
>   vocabulary: success sets `Status = "complete"`, the error branch now calls
>   `HandleFailedUpload`, and that method is no longer a stub. `HandleRetryExperience()` is
>   deliberately not called for the same reason.
> - **The `status_log` Table DAT was dropped**, along with `_ensureStatusLog` /
>   `_appendStatusLog` / `_clearStatusLog`. It was conceived as the replacement for the
>   textport prints, but `_applyProgress` already routes every event through
>   `self.Logger` and therefore through vvox_tdtools' rotating file handler, with a frame
>   number attached — so the DAT was a redundant second copy of the same history, costing
>   a node in the `.tox` and TD-object churn per event. Current state is covered
>   at-a-glance by the `Stage` / `Progress` / `StatusMessage` / `LastError` pars; history
>   lives in the log file. Ignore §2's `_ensureStatusLog` paragraph and verification
>   step 6.
> - **§4 (the `claude.md` Threading section) was skipped** and is still worth doing.
> - `operator_interface_bridge.py` and `comfyui_control`, both cited as sources to copy
>   from, were deleted in `b31b338`. Recover via
>   `git show b31b338^:TD/td-modules/...` if needed. The `comfyuiControlEXT.py:247`
>   citation was also wrong: it was `deleteRow(row_index)`, a targeted removal, not the
>   FIFO trim described here.

## Context

`upload_control` runs its whole takeaway pipeline on a background thread via the palette
Thread Manager Client ([../scripts/upload_control_thread_manager_callbacks.py](../scripts/upload_control_thread_manager_callbacks.py)):
ffmpeg transcode → screenshot extract → HTTP upload with retries → QR generation →
PostgREST playthrough completion. That's 5+ distinct steps and 20–60s of wall clock, and
the main thread learns **nothing** until it's over — the Thread Manager's contract is a
single terminal payload (`clientQueueManager.SetSuccessPayload` → `OnSuccess`/`OnExcept`).

Everything in between is a bare `print()` to the textport (lines 96, 99, 110, 124, 127,
133, 144, 154). Those can't be upgraded to `self.Logger` in place: `CustomFormatter.format`
in `vvox_td_py_env/Lib/site-packages/vvox_tdtools/log.py` reads `absTime.frame` on every
record, so logging is itself a TD API touch and is unsafe off the main thread. Nothing in
the network can react to a stage, nothing drives the loading bar, and a hang is
indistinguishable from slow.

Outcome: the worker emits structured stage events into a thread-safe queue; the main
thread drains it every frame and turns it into custom parameters, a rolling status table,
and proper logger output. While in there, restore the success wiring that went missing in
`90e2542` — `HandleUploadResult` no longer sets `Status = "complete"` or hands
`qr_code_path` to `qrcode_scene`, which is what `qrcodeEXT._onEnterscene` gates on.

Scope: TD-network destinations only (no new websocket traffic to the Operator app), stage
milestones rather than parsed ffmpeg/byte percentages, and yes to fixing the success path.

## Design

**The queue is owned by the extension, not the callbacks module.** `UploadControlEXT`
creates one `queue.Queue` in `__init__` and hands it out via `GetProgressQueue()`. A
module-level queue in the callbacks DAT would be swapped out whenever that DAT re-cooks
mid-upload, silently orphaning in-flight events; an extension attribute keeps one stable
identity.

**The worker touches nothing but that queue** — `Queue.put` is stdlib, no TD API. This is
the same main→thread / thread→main split the file already documents in its `RunInThread`
docstring, just with a second channel going the other way.

**The pump is `OnFrameStart`**, already wired: `BaseEXT._createExecuteDat`
(`vvox_tdtools/base.py:120-137`) creates `execute_ext` with `framestart = True` and routes
it to `parent().OnFrameStart`. `UploadControlEXT` doesn't override it yet. The palette's
`OnRefresh` stub is the other candidate, but its enable/rate parameters are inside the
opaque `.tox` and unverified — `OnFrameStart` has no unknowns. (If the Thread Manager's
refresh does turn out to be enabled, pointing `OnRefresh` at the same drain method is a
one-liner.)

## Changes

### 1. `scripts/upload_control_thread_manager_callbacks.py` — worker side

Add near the top:

```python
import queue  # noqa: F401  - documents what _PROGRESS is; the object itself comes from the EXT

# Set on the main thread by Setup(), read by the worker. The queue object lives on
# UploadControlEXT, so this only caches a pointer - a DAT re-cook can't orphan it.
_PROGRESS = None

STAGES = {                    # stage -> coarse progress, weighted by observed duration
    "queued":       0.00,
    "transcoding":  0.05,
    "transcoded":   0.45,
    "screenshot":   0.50,
    "uploading":    0.55,
    "uploaded":     0.85,
    "qrcode":       0.90,
    "completing":   0.95,
    "done":         1.00,
    "error":        None,     # None -> main thread holds the last value
}

def _report(stage, message="", level="info", **extra):
    """Thread-safe status hand-off. Touches ONLY a stdlib Queue - never a TD object,
    and never self.Logger, whose formatter reads absTime.frame."""
    if _PROGRESS is None:
        return
    _PROGRESS.put({
        "stage": stage,
        "progress": STAGES.get(stage),
        "message": str(message),
        "level": level,
        "t": time.time(),     # stamped at emit, so a delayed drain still reads in order
        **extra,
    })
```

`Setup()` caches the queue and emits the opening event (it's on the main thread, so the
`op.upload_control` access is fine):

```python
global _PROGRESS
_PROGRESS = op.upload_control.GetProgressQueue()
_report("queued", movie)
```

Replace each `print()` in `_extract_frame`, `_process_and_upload` and `_upload_video` with
the matching `_report(...)`, keeping the existing text as the `message`:

| Current line | Becomes |
|---|---|
| `print("Processing file to", …)` (110) | `_report("transcoding", output_file_name)` |
| `print("FFMPEG Process Successful")` (127) | `_report("transcoded", output_file_name)` |
| ffmpeg failure branch (124) | `_report("error", f"ffmpeg failed ({rc})", level="error", detail=log[-2000:])` |
| `print("Wrote screenshot", …)` (99) | `_report("screenshot", output_path)` |
| `_extract_frame` failure (96) | `_report("screenshot", "frame extract failed", level="warning")` |
| `print("Attempting Upload of ", …)` (133) | `_report("uploading", output_file_name, attempt=1)` |
| each retry in the `while` loop (136-139) | `_report("uploading", "retrying", attempt=3 - retries)` |
| `print("Successfully uploaded", …)` (144) | `_report("uploaded", takeaway_id)` |
| after `qrcode.save(...)` (148) | `_report("qrcode", qrcode_file_name)` |
| `print("Completing playthrough", id)` (154) | `_report("completing", id)` |
| final return (156) | `_report("done", takeaway_url)` |
| upload-failed return (142) | `_report("error", video_response["error"], level="error")` |

`_complete_playthrough`'s `raise_for_status()` still propagates to `OnExcept` — leave that
path alone, `HandleUploadException` covers it.

### 2. `td-modules/upload_control/uploadControlEXT.py` — main side

`__init__`: `self._progress = queue.Queue()`, then `self._ensureStatusLog()`.

```python
def GetProgressQueue(self):
    """Handed to the worker thread by the callbacks DAT's Setup()."""
    return self._progress

def OnFrameStart(self, frame: int):
    if self._progress.empty():        # fast path, this runs 60x/sec
        return
    while True:
        try:
            self._applyProgress(self._progress.get_nowait())
        except queue.Empty:
            break

def _applyProgress(self, event):
    stage = event["stage"]
    self.Me.par.Stage = stage
    if event.get("progress") is not None:
        self.Me.par.Progress = event["progress"]
    self.Me.par.Statusmessage = event.get("message", "")
    if event.get("level") == "error":
        self.Me.par.Lasterror = event.get("message", "")
    log = getattr(self.Logger, event.get("level", "info"), self.Logger.info)
    log(f"[{stage}] {event.get('message', '')}")
    self._appendStatusLog(event)
```

New read-only pars on the existing `Controls` page in `_createControlsPage`, built with
`ParTemplate` exactly like `Status` is today (note `createPar` title-cases the name, so
`StatusMessage` → `Statusmessage`, matching how `FilePath` → `Filepath` already behaves):

- `Stage` (Str) — fine-grained stage name
- `Progress` (Float, `normMin=0`, `normMax=1`) — for `loading_bar` / `status_view` to bind to
- `StatusMessage` (Str) — the detail line
- `LastError` (Str) — sticks after a failure for post-mortem

`Status` keeps its existing coarse vocabulary (`inactive` / `processing` / `complete` /
`error`) untouched — `qrcodeEXT.py:46` and `stateControlEXT.py:43,54` depend on it.

`_ensureStatusLog` / `_appendStatusLog`: create a `status_log` Table DAT inside the COMP if
absent, header `time | stage | progress | message`, `appendRow` per event, and trim from
the top past ~200 rows (`deleteRow(1)`, the same call `comfyuiControlEXT.py:247` uses on
its queue table). This is the replacement for the textport prints — it's visible in the
network and survives past the console buffer.

`_onUploadvideo`: before pulsing `Runinthread`, reset `Progress = 0`, `Stage = "queued"`,
`Lasterror = ""` and clear `status_log` so each run reads clean.

### 3. Restore the success / failure wiring (same file)

`HandleUploadResult`, success branch — mirror what `operator_interface_bridge.py:67-74`
does, since that's the path this replaced:

```python
qr_code_path = result.get("qr_code_path")
if qr_code_path:
    op.qrcode_scene.op("qrcode_file").par.file = qr_code_path
op.upload_control.par.Status = "complete"
if op.state_control.par.Scenename.eval() == "qrcode_scene":
    op.qrcode_scene.par.Showqrcode = 1
    op.qrcode_scene.op("timeout_timer").par.initialize.pulse()
```

Error branch: keep `Status = "error"` and add the missing `self.HandleFailedUpload()` call.

`HandleFailedUpload` is currently a stub with its one line commented out. Fill it in from
`operator_interface_bridge.py:40-47`, but only the operators the current network actually
has — `op.photo_capture`, `op.state_control` and `op.qrcode_scene` are all live (used by
`stateControlEXT.HandleExperienceComplete`), so:

```python
op.photo_capture.par.Showerrormessage = 1
op.state_control.HandleRetryExperience()
```

Skip the legacy `op.comfyui_control.par.Gotpromptid / Waitforcompletion` writes unless
`comfyui_control` is confirmed to still be in the running network — check before wiring.

### 4. `claude.md` — document the rule

The guide has 13 sections and zero mentions of threading; the only written statement of the
constraint is a docstring. Add a short **Threading** section: what may not be touched off
the main thread (any TD object — *including* `self.Logger`, because of the `absTime.frame`
read in the formatter), and the Setup-payload-in / queue-drained-in-`OnFrameStart`-out
pattern as the house convention.

## Verification

1. Open `cadi-robot-photobooth26.toe`, select `upload_control`, confirm the four new pars
   appear on the Controls page and `status_log` exists inside the COMP.
2. Set `Filepath` to one of the existing clips in `TD/` (e.g.
   `sharable_20260729_150214_processed.mp4`) and pulse `UploadVideo` with the parameter
   dialog open. `Stage` should step queued → transcoding → transcoded → screenshot →
   uploading → uploaded → qrcode → completing → done, `Progress` should climb 0 → 1, and
   `status_log` should accumulate a timestamped row per step — all while the timeline keeps
   cooking at full rate (the drain must not stall frames).
3. Check `logs/cadi-robot-photobooth26*.log` for the `[stage] message` lines at INFO,
   confirming they now carry frame numbers and go through the rotating file handler rather
   than the textport.
4. Force the error path — point `FFMPEG_PATH` at a bad path, or block
   `ingest.curatorlive.com` — and confirm `Stage` lands on `error`, `Lasterror` holds the
   message, `Status` becomes `error`, and `photo_capture.Showerrormessage` turns on.
5. Run a full booth cycle end-to-end and confirm the regression fix: on success
   `Status` reaches `complete`, `qrcode_file` points at the new PNG, and entering
   `qrcode_scene` shows the QR instead of falling through to `timeout_timer`.
6. Re-save the `upload_control.tox` so the new pars and `status_log` persist with the
   component.
