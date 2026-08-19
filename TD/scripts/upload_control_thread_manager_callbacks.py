import json
import os
import shutil
import subprocess
import time
import uuid
import requests
import segno
import json, os, datetime

BASE_URL = "https://ingest.curatorlive.com/upload"
# Same public endpoint the browsers use (Operator app, kiosk-app/frontend).
# PostgREST itself has no published port -- only cors-proxy does -- and TD
# runs as a native Windows process outside the compose network, so it has to
# go through the same published port everyone else does.
POSTGREST_URL = root.var("postgrest_url")
MICROSITE_URL = "https://share.curatorlive.com/"
EVENT_CODE = "QFSVY8"
FFMPEG_PATH = "C:/ProgramData/chocolatey/bin/ffmpeg.exe"
FFPROBE_PATH = FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe")
# AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzIiwianRpIjoiOTRlMjg5NWNhOGFmZWVjN2YyMjBkMWQ1ODI2OWU2YzY0YzVmNWEzN2RmOGZmZmZjN2MyYzk2ZjBkNDFlOTgwMTc4NjRjZDg0M2YwYzEwOWYiLCJpYXQiOjE3NTM0NzgxNDcuNjUxNDU5LCJuYmYiOjE3NTM0NzgxNDcuNjUxNDYsImV4cCI6MTc4NTAxNDE0Ny42MzI0OTksInN1YiI6IjE0MjQ1Iiwic2NvcGVzIjpbImFwaSIsInJlYWQtZXZlbnRzIiwidXBsb2FkIl19.OQ5-Fz_1q-npufiyaV76PboSt6R-o8YXDSG3Hj-1iw1Zfo16iBYBsaO8THDhMikQ4QXD5s3zTXMvl-lkAY_IJiSqfrPEYqItBKhskDD1d4fuWE6zotPDS51CizvnTuzapdoUow1ilEzbtPewoGjbAeBx8UpeIV_vjj25Hzns6V1yd68wCDoPLDX6t8BxH_l-Di9VBfVRiv3Fo8lx2ylAMs_EfyOGHDLToMqXvYgNoaNptUOh0JwtPdJyBrGanU2qic--kOsHA8eZszI2eIDspi61Rl8_PNuNCcSGbQvJ18GLNh1sm5T4STORKOtnNrgRun4Zt1yStsCrMvZBw7f7hOqsX4CvIc328BjzsHd1pZl7_dkpT1t-75xp9c_n-z9tVZN1ThNG2Vg0QEtAP9s-AUMBtYt2K-krYFLe1qU06y-ITH8aX1DR8bivMnDX70T9PSADggePKfN5OkK45FZSYnUYWtfkMuHdO04CRc7BepEvj2KsYPzJHDH7QX2OERO1mgIr1jkrn4YZx6hf6usqvWUK5nqToNxO6PiZNURS1gVCI7-WyeRBrdItZLs7UP_8LgpTEuLqDEe8YFFu4pzZPk-9fgyJ4kFpnfs3PKIJQD83HVlKP3wSDmfek1TZHH_c38k_69YBchMzElZ67Ty2A_W_Nnahc5_IQp4Nt2DL7FE"
AUTH_TOKEN= "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzIiwianRpIjoiYWU2MmIwNzA2OWZmNmJiYzFmYjZjMmZmZmQ2ZTNkZTdlMzc2OWQzZjc1M2I0ODBlMjkwYjJiM2IxNzBhNGFlNzE3ZDliNTRjOTY2NjRiNWMiLCJpYXQiOjE3ODUxODc2NjguMzEwMjc1LCJuYmYiOjE3ODUxODc2NjguMzEwMjgyLCJleHAiOjE4MTY3MjM2NjguMTE2MDkxLCJzdWIiOiIxNDI0NSIsInNjb3BlcyI6WyJhcGkiLCJyZWFkLWV2ZW50cyIsInVwbG9hZCJdfQ.wfF5qeMLJTeisHncu_slpadwnR5IF8NYR5tazMiu0wqL5i-V-AsNbeZRR5mXiOng4IteW5z66bQOuuTogZtWi4i5rEglrPKgcX01kVizIjIaoukZl4VlxB-uEo0gnK4V5hd15wK7rJa2v_3iOkkD0T7-HdW5S083DVILt8uqjMllhZqO81_apT1OI7-xtJtjh9Gg_2QP4Q7fRRccrIY5HuKzzp-fJgRJOoJavv4XEp4NjgqzUnnT2jFummQm0gKB0POfK6bjnV1XnMzBFJ7rdiRCAqE47EQ08FnPyuMykt1pGpJboHHee8Igf1T_3Qw_OjkHwYI9gq1JH622YZuDlNoL-Wk3L2cZFabDguV0VSri0FjWrbTrLpgjbgzxzCKkbXZH2YWYKI-bOSzOJVavXBmNqkSm0Zz0TD6U89P5qDJYuVe_uDh-UPrWFbja4cW6U2nBieehN9RydUup6R5pN41F2opHtb6OED8bKDxDwy6hmqF2VlzImgO_F0vC8K0tU3OQXTqidFJWt-YXi6ZDPYaMANt6Syw31RdikwSXttP2MR-kjUpbksNUMUtXri2gTH--RPLArPOSypAIYdvEM2-JsgCsDVf9A02aUj6SQhT_UIekjWym_RVv5LlxY5RQDO02ZD0zPZP-jC_g-L7Gz13EWhRJY0Ja7BWKeu8lYkU"
DATA_DIR = root.var("data_dir")
QR_CODE_DIR = os.path.join(DATA_DIR, "qr_code")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")
SCREENSHOT_FRAME = 230

# How many frames the extracted still is held at the head of the processed video,
# so a phone's camera roll thumbnail shows the guest instead of whatever the
# render opens on. One frame is invisible on playback and enough for any
# thumbnail generator that decodes frame 0 -- raise it if some platform seeks
# past the very start and picks a later frame instead.
#
# NOTE: this shifts all video content later by this many frames. The kiosk's
# TakeawayScreen.jsx (CADI-2026-WEBAPPS) loops a hardcoded frame range tuned to
# the arrival beat -- at 1 frame the drift is irrelevant, but if you raise this
# meaningfully, shift LOOP_START/LOOP_END there by the same amount.
INTRO_HOLD_FRAMES = 1

# The kiosk streams media straight off the absolute paths recorded in Postgres,
# so every file it serves has to exist on that machine too. This copies them
# there directly instead of waiting for Syncthing to notice a 20MB+ video.
#
# The whole takeaway folder is exposed as a single share that resolves to the
# same C:\Cadi26\takeaway path on the kiosk PC, so a local file maps to it by
# swapping DATA_DIR for SHARE_ROOT and keeping the rest of the path intact --
# which is exactly what keeps the absolute path written to the DB valid on both
# machines. New media subdirectories need no share of their own.
SHARE_ROOT = r"\\DESKTOP-N42F08I\takeaway"
SHARE_COPY_ATTEMPTS = 3

# Set on the main thread by Setup(), read by the worker. The queue.Queue itself lives on
# UploadControlEXT rather than here, so this only caches a pointer -- a module-level queue
# would be swapped out whenever this DAT re-cooks mid-upload, silently orphaning every
# event still in flight.
_PROGRESS = None

# stage -> coarse progress, weighted by observed duration (~3s encode, ~10-12s upload).
#
# "ready" at 0.45 is the one that matters: that's the point the guest can already be
# served their takeaway, and everything past it is the curatorlive upload finishing in
# the background. So the back half of this bar is work nobody is waiting on -- don't
# read it as "the guest is still waiting".
#
# "error" is None so the main thread holds whatever progress it had rather than snapping
# the bar back to zero.
STAGES = {
	"queued":      0.00,
	"transcoding": 0.05,
	"transcoded":  0.30,
	"screenshot":  0.35,
	"publishing":  0.38,
	"published":   0.43,
	"ready":       0.45,
	"uploading":   0.50,
	"uploaded":    0.90,
	"qrcode":      0.93,
	"completing":  0.98,
	"done":        1.00,
	"error":       None,
}


def _report(stage, message="", level="info", **extra):
	"""Thread-safe status hand-off to the main thread.

	Touches ONLY a stdlib Queue -- never a TD object, and in particular never self.Logger,
	whose formatter reads absTime.frame (vvox_tdtools/log.py) and is therefore a TD API
	call in disguise. Everything in this module runs off the main thread except Setup().

	Silently no-ops if the queue was never handed over, so the pipeline still runs if the
	extension didn't initialise -- progress reporting must never be the thing that breaks
	a takeaway.
	"""
	if _PROGRESS is None:
		return
	_PROGRESS.put({
		"stage": stage,
		"progress": STAGES.get(stage),
		"message": str(message),
		"level": level,
		# Stamped at emit rather than at drain, so a frame hitch doesn't reorder events.
		"t": time.time(),
		**extra,
	})


def _upload_video(video_file, timestamp):
	headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
	url = f"{BASE_URL}/{EVENT_CODE}"
	files = {"image": video_file}
	data = {"image_type": "video", "timestamp": timestamp, "faces": 0}
	try:
		response = requests.post(url, headers=headers, data=data, files=files, timeout=15)
		response.raise_for_status()
		return response.json()
	except requests.exceptions.RequestException as e:
		return {
			"result": "error",
			"error": str(e),
			"statusCode": e.response.status_code if e.response is not None else None,
			"data": None,
			"response_body": e.response.text if e.response is not None else None,
		}
	except json.JSONDecodeError:
		return {"result": "error", "error": "Invalid JSON response", "statusCode": response.status_code, "data": None, "response_body": response.text}

def _upsert_playthrough(playthrough_id, **fields):
    """Merge fields into the playthroughs row the Operator app already created.

    An upsert rather than a plain PATCH: fills in the normal case (row already
    exists) but still creates one if playthrough_id was somehow missing and
    _process_and_upload fell back to a brand-new uuid. created_at is deliberately
    never sent, so it's untouched on the merge path but still gets its DEFAULT
    now() if this ends up creating a fresh row.

    Only ever send fields this pipeline owns. participant_id and
    share_to_big_screen belong to the kiosk's email step and must never appear
    here -- a guest can submit their email between our two writes, and including
    those keys would null out the link they just made.
    """
    response = requests.post(
        f"{POSTGREST_URL}/playthroughs?on_conflict=id",
        json={"id": playthrough_id, **fields},
        headers={"Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"},
        timeout=15,
    )
    # raise_for_status() alone gives you "400 Client Error: Bad Request for url:
    # ..." and throws the body away -- but the body is where PostgREST actually
    # says what it objected to (a column missing from its schema cache, a type
    # mismatch, an FK violation). Report it before re-raising, so a failure here
    # is diagnosable from the log instead of needing a reproduction.
    if not response.ok:
        _report("error", f"playthrough upsert failed ({response.status_code})", level="error",
            detail=response.text[:1000], sent=sorted(fields))
    response.raise_for_status()


def _mark_media_ready(playthrough_id, video_path, screenshot_path=None, is_showroom_staff=False):
    """EARLY write -- the moment the kiosk may show this takeaway to a guest.

    Deliberately lands before the curatorlive upload, which is ~60% of the total
    pipeline time and which the guest doesn't need in order to watch their own
    video. video_path being non-NULL is the kiosk's readiness signal, so this
    must only run AFTER the file is fully published to the share.

    ingested_at is set here rather than at completion, and that matters more than
    it looks: the kiosk's approval timeout is measured from
    COALESCE(ingested_at, created_at). Left NULL until completion, the review
    window would be measured from capture start instead -- so any capture whose
    robot cycle plus processing exceeded the window would become servable with no
    operator review at all. Setting it here also keeps servability monotonic; a
    later ingested_at would make an already-released row un-servable again.
    """
    fields = {
        "video_path": video_path.replace("\\", "/"),
        "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        # Written here rather than at completion so it's set the moment the row
        # becomes servable -- the kiosk reads it to decide whether to send this
        # guest's email step to Mixpanel, which happens well before the late
        # write lands. TD is the only writer of this column.
        "is_showroom_staff": bool(is_showroom_staff),
    }
    if screenshot_path:
        fields["screenshot_path"] = screenshot_path.replace("\\", "/")
    _upsert_playthrough(playthrough_id, **fields)


def _complete_playthrough(playthrough_id, qrcode_path, microsite_url):
    """LATE write -- everything that depends on the upload having finished.

    Must NOT touch ingested_at; see _mark_media_ready for why.
    """
    _upsert_playthrough(
        playthrough_id,
        qrcode_path=qrcode_path.replace("\\", "/"),
        microsite_url=microsite_url,
    )

def _extract_frame(video_path, output_path, frame_number=SCREENSHOT_FRAME):
	"""Grab a single frame as a PNG for the kiosk's operator gallery.

	Returns the path, or None if it couldn't be written - a missing thumbnail
	isn't worth failing an upload over, and the kiosk falls back to the video's
	first frame when screenshot_path is absent from the manifest.
	"""
	os.makedirs(SCREENSHOT_DIR, exist_ok=True)
	result = subprocess.run([
		FFMPEG_PATH,
		"-y",
		"-i", video_path,
		"-vf", f"select=eq(n\\,{frame_number})",
		"-frames:v", "1",
		"-vsync", "0",
		output_path,
	], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)

	# A clip shorter than frame_number matches nothing, and ffmpeg still exits 0
	# without writing a file - so the file existing, not the return code, is the
	# real success check here.
	if result.returncode != 0 or not os.path.isfile(output_path):
		ffmpeg_log = result.stdout.decode(errors="replace")
		# Warning, not error: the run continues without a screenshot.
		_report("screenshot", f"frame {frame_number} extraction failed ({result.returncode})",
			level="warning", detail=ffmpeg_log[-2000:])
		return None

	_report("screenshot", output_path)
	return output_path


def _probe_stream(video_path, stream, entries):
	"""Read ffprobe stream fields as a stripped string, or "" if unavailable."""
	result = subprocess.run([
		FFPROBE_PATH,
		"-v", "error",
		"-select_streams", stream,
		"-show_entries", f"stream={entries}",
		"-of", "default=nw=1:nk=1",
		video_path,
	], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
	if result.returncode != 0:
		return ""
	return result.stdout.decode(errors="replace").strip()


def _publish_to_share(local_path):
	"""Copy a finished artifact to the matching share on the kiosk machine.

	Copies to a temp name and renames, so the kiosk can never read a half-copied
	file -- the rename is atomic within the share, unlike the copy itself, which
	for a 20MB video is very much not instantaneous.

	Returns True on success. Retries a couple of times first, since the common
	failure here is a momentary network blip rather than anything permanent.
	"""
	if not local_path or not os.path.isfile(local_path):
		_report("publishing", f"nothing to publish, missing: {local_path}", level="warning")
		return False

	# Mirror the path under the share: DATA_DIR/processed/x.mp4 becomes
	# SHARE_ROOT/processed/x.mp4, so it lands at the identical absolute path the
	# kiosk will look it up by.
	relative = os.path.relpath(local_path, DATA_DIR)
	# relpath will happily climb out with "..", which would write somewhere
	# unrelated -- anything not under DATA_DIR is a caller bug, not a copy to make.
	if relative.startswith(".."):
		_report("publishing", f"refusing to publish {local_path}: not inside {DATA_DIR}",
			level="error")
		return False

	destination = os.path.join(SHARE_ROOT, relative)
	# Not the final name, so an in-flight copy never shows up in the kiosk's
	# directory listings or gets picked up by anything scanning the share.
	temp_destination = f"{destination}.part"

	# Reported per file rather than once for the batch: this is the slowest remaining step
	# (a 12-23MB video over SMB) and the one most likely to fail, so it's worth being able
	# to see which of the three is in flight.
	_report("publishing", destination)

	for attempt in range(1, SHARE_COPY_ATTEMPTS + 1):
		try:
			# Cheap insurance for a media subdirectory that exists locally but
			# hasn't been created on the share side yet.
			os.makedirs(os.path.dirname(destination), exist_ok=True)
			shutil.copyfile(local_path, temp_destination)
			os.replace(temp_destination, destination)
			_report("published", destination)
			return True
		except OSError as e:
			_report("publishing", f"attempt {attempt}/{SHARE_COPY_ATTEMPTS} failed for {destination}: {e}",
				level="warning", attempt=attempt)
			try:
				if os.path.isfile(temp_destination):
					os.remove(temp_destination)
			except OSError:
				pass
			if attempt < SHARE_COPY_ATTEMPTS:
				time.sleep(1)

	return False


def _process_and_upload(file_name, audio_file_name, playthrough_id=None, is_showroom_staff=False):
	if not file_name or not os.path.isfile(file_name):
		return {"status": "video_upload_error", "message": f"File not found: {file_name}"}

	base_name = file_name.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0]
	qrcode_file_name = os.path.join(QR_CODE_DIR, f"{base_name}_qrcode.png")
	output_file_name = os.path.join(PROCESSED_DIR, f"{base_name}_processed.mp4")
	_report("transcoding", output_file_name)

	# One pass does everything: transcode, mux the shareable audio track, and put
	# the intro frame at the head of the video. That last part used to be a second
	# full re-encode afterwards; folding it in here saves ~2s off the time before
	# the guest can see their takeaway, and drops a generation of re-encode.
	has_audio = os.path.isfile(audio_file_name)
	if not has_audio:
		_report("transcoding", f"audio file not found at {audio_file_name}, processing without it",
			level="warning")

	# Frame rate and duration of the SOURCE. Both are needed to place the intro
	# frame and bound the audio; read rather than assumed, since the render
	# settings have changed before (an older render was 60fps, current ones 30).
	raw_fps = _probe_stream(file_name, "v:0", "r_frame_rate")
	source_duration = _probe_stream(file_name, "v:0", "duration")
	try:
		numerator, _, denominator = raw_fps.partition("/")
		fps = float(numerator) / float(denominator or 1)
		duration = float(source_duration)
	except ValueError:
		fps, duration = 0, 0

	# No usable timing means no intro frame -- fall back to a plain transcode
	# rather than failing the run over a cosmetic first frame.
	intro = fps > 0 and duration > 0 and INTRO_HOLD_FRAMES > 0
	if not intro:
		_report("transcoding", f"no usable source timing (fps={raw_fps!r}, dur={source_duration!r}), "
			"transcoding without the intro frame", level="warning")

	ffmpeg_cmd = [FFMPEG_PATH, "-y", "-i", file_name]
	if has_audio:
		ffmpeg_cmd += ["-i", audio_file_name]

	if intro:
		hold_seconds = INTRO_HOLD_FRAMES / fps
		# fps= is load-bearing, not redundant: a single trimmed frame carries no
		# duration, so concat computes a zero-length first segment and stacks the
		# body on top of it at the same timestamp instead of after it. tpad only
		# applies for a multi-frame hold; trim alone already yields exactly one.
		pad = f",tpad=stop={INTRO_HOLD_FRAMES - 1}:stop_mode=clone" if INTRO_HOLD_FRAMES > 1 else ""
		chains = [
			f"[0:v]split=2[sel][main]",
			f"[sel]trim=start_frame={SCREENSHOT_FRAME}:end_frame={SCREENSHOT_FRAME + 1},"
			f"setpts=PTS-STARTPTS,fps={fps}{pad},setsar=1[still]",
			f"[main]setsar=1[body]",
			f"[still][body]concat=n=2:v=1:a=0[v]",
		]
		if has_audio:
			# Delayed so the music bed still lands on the motion, then bounded to
			# the video's new length. -shortest can't do this job any more: it
			# measures the raw input, not the filtered output, so it would trim
			# the final frame back off the video we just lengthened.
			chains.append(
				f"[1:a]adelay={int(round(hold_seconds * 1000))}:all=1,"
				f"atrim=end={duration + hold_seconds:.6f}[a]"
			)
		ffmpeg_cmd += ["-filter_complex", ";".join(chains), "-map", "[v]"]
		if has_audio:
			ffmpeg_cmd += ["-map", "[a]"]
	else:
		ffmpeg_cmd += ["-map", "0:v:0"]
		if has_audio:
			ffmpeg_cmd += ["-map", "1:a:0", "-shortest"]

	ffmpeg_cmd += [
		"-c:v", "libx264",
		"-movflags", "+faststart",
		"-pix_fmt", "yuv420p",
		"-preset", "fast",
		"-crf", "20",
	]
	if has_audio:
		ffmpeg_cmd += ["-c:a", "aac", "-b:a", "192k"]
	ffmpeg_cmd.append(output_file_name)

	ffmpeg_result = subprocess.run(ffmpeg_cmd,
		stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW, check=True)
	if ffmpeg_result.returncode != 0:
		ffmpeg_log = ffmpeg_result.stdout.decode(errors="replace")
		_report("error", f"ffmpeg failed ({ffmpeg_result.returncode})",
			level="error", detail=ffmpeg_log[-4000:])
		return {"status": "video_upload_error", "message": f"ffmpeg failed with code {ffmpeg_result.returncode}"}
	else:
		_report("transcoded", output_file_name)

	# Read from the SOURCE, not the output: the output now carries the intro frame,
	# so its frame SCREENSHOT_FRAME is no longer the same moment. Taking both from
	# the source keeps the gallery thumbnail and the intro frame the same frame,
	# which is the whole point of picking one representative moment.
	screenshot_file_name = os.path.join(SCREENSHOT_DIR, f"{base_name}_screenshot.png")
	screenshot_path = _extract_frame(file_name, screenshot_file_name)

	# --- everything the guest needs is ready; hand it over before uploading ----
	# The curatorlive upload below is ~60% of this pipeline and the guest doesn't
	# need it to watch their own video, so the kiosk is told about the takeaway
	# now and the upload finishes while they walk screens 1-3.
	#
	# Publish BEFORE the DB write, never after: video_path appearing is the
	# kiosk's signal that the file is readable, and _publish_to_share only renames
	# into place once the copy is complete.
	if not _publish_to_share(output_file_name):
		_report("error", "failed copying the video to the kiosk share", level="error")
		return {"status": "video_upload_error", "message": "Failed copying the video to the kiosk share"}

	# Best-effort: without it the gallery just falls back to the video's first
	# frame, so drop the path rather than fail the run.
	if screenshot_path and not _publish_to_share(screenshot_path):
		_report("publishing", "continuing without a screenshot -- the gallery will use the video's first frame",
			level="warning")
		screenshot_path = None

	# Reuse the id the Operator app minted at capture time (threaded through via
	# Setup()'s payload) so both writes land on the SAME row the operator already
	# created, rather than an orphaned second one. Only falls back to a fresh uuid
	# if that id is missing.
	id = playthrough_id or uuid.uuid4()
	_mark_media_ready(str(id), output_file_name, screenshot_path, is_showroom_staff)
	_report("ready", f"{id} -- guest can now be served")

	with open(output_file_name, "rb") as video_file:
		_report("uploading", output_file_name, attempt=1)
		video_response = _upload_video(video_file, int(time.time()))
		retries = 2
		while video_response["result"] == "error" and retries > 0:
			video_file.seek(0)
			_report("uploading", f"retrying after: {video_response.get('error')}",
				level="warning", attempt=3 - retries + 1)
			video_response = _upload_video(video_file, int(time.time()))
			retries -= 1

	if video_response["result"] == "error":
		_report("error", f"upload failed: {video_response['error']}", level="error")
		return {"status": "video_upload_error", "message": f"Upload failed: {video_response['error']}"}
	takeaway_id = video_response["data"]["id"]
	_report("uploaded", takeaway_id)
	takeaway_url = f"{MICROSITE_URL}/{EVENT_CODE}/{takeaway_id}"
	# The microsite has no access to our database, so the staff flag rides in the
	# URL itself: cadi-curator-app.js reads ?staff=1 and skips Mixpanel entirely.
	# Appended here rather than at either use site because this one string feeds
	# BOTH the QR image below and microsite_url in the late write -- so the code
	# the guest scans and the link we store can never disagree.
	if is_showroom_staff:
		takeaway_url = f"{takeaway_url}?staff=1"
	qrcode = segno.make_qr(takeaway_url)
	qrcode.save(qrcode_file_name, scale=20, border=2)
	_report("qrcode", qrcode_file_name)

	# The guest may already be watching their video and walking toward screen 4,
	# so this is the one the QR screen is waiting on. Same ordering rule as the
	# video: on the share before it's in the DB.
	if not _publish_to_share(qrcode_file_name):
		_report("error", "failed copying the QR code to the kiosk share", level="error")
		return {"status": "video_upload_error", "message": "Failed copying the QR code to the kiosk share"}

	_report("completing", str(id))
	_complete_playthrough(str(id), qrcode_file_name, takeaway_url)
	_report("done", takeaway_url)
	return {"status": "video_upload_success", "qr_code_path": qrcode_file_name}


def Setup(tmClientExt: object) -> object:
	"""
	Runs on the main thread. Reads the file path off the upload_control COMP
	(a plain TD object access) and returns it as a plain-data payload for RunInThread.
	Also reads the current playthrough id off operator_bridge - set there from the
	Operator app's capture_request/retake_capture websocket message - so RunInThread
	can reuse it instead of minting a fresh, disconnected id.
	"""
	movie = op.upload_control.par.Filepath.eval()
	playthrough_id = op.operator_bridge.par.Currentplaythroughid.eval()
	audio_file = op.upload_control.par.Audiofilepath.eval()
	# Stashed by operator_bridge from the Operator app's checkbox. Rides the same
	# main-thread-read / plain-data-out path as the playthrough id.
	is_showroom_staff = bool(op.operator_bridge.par.Isshowroomstaff.eval())

	# Main thread, so touching op.upload_control here is fine -- and it's the only place
	# the worker can be handed the queue, since RunInThread must not resolve operators.
	global _PROGRESS
	_PROGRESS = op.upload_control.GetProgressQueue()
	_report("queued", movie)

	return {
		"file_name": movie,
		"audio_file_name": audio_file,
		"playthrough_id": playthrough_id or None,
		"is_showroom_staff": is_showroom_staff,
	}


def RunInThread(tmClientExt: object, payload: object) -> None:
	"""
	Runs off the main thread. Must not touch any TD object - only plain Python
	(ffmpeg subprocess, HTTP upload, QR generation). Any raised exception is
	caught by the ThreadManager and routed to OnExcept below.
	"""
	result = _process_and_upload(
		payload["file_name"],
		payload.get("audio_file_name"),
		payload.get("playthrough_id"),
		payload.get("is_showroom_staff", False),
	)
	tmClientExt.clientQueueManager.SetSuccessPayload(result)


def OnRefresh(tmClientExt: object, refreshPayload: object|None):
	pass


def OnSuccess(tmClientExt: object, successPayload: object):
	op.upload_control.HandleUploadResult(successPayload)


def OnExcept(tmClientExt: object, args):
	op.upload_control.HandleUploadException(args)
