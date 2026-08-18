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

# stage -> coarse progress, weighted by observed duration. Both ffmpeg passes and the share
# copy are seconds-scale, so they get real spans rather than instants; anything that lands
# in under a second is a marker between them. "error" is None so the main thread holds
# whatever progress it had rather than snapping the bar back to zero.
STAGES = {
	"queued":      0.00,
	"transcoding": 0.05,
	"transcoded":  0.40,
	"screenshot":  0.45,
	"prepending":  0.50,
	"prepended":   0.60,
	"uploading":   0.62,
	"uploaded":    0.85,
	"qrcode":      0.88,
	"publishing":  0.90,
	"published":   0.97,
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

def _complete_playthrough(playthrough_id, video_path, qrcode_path, microsite_url, screenshot_path=None):
    """Fills in the playthroughs row the Operator app already created (id +
    created_at only) once processing/upload finishes. An upsert rather than a
    plain PATCH: fills in the normal (Operator app already created the row)
    case, but still creates a fresh row if playthrough_id was somehow missing
    and _process_and_upload fell back to a brand-new uuid. created_at is
    deliberately omitted so it's untouched on the merge path but still gets
    its DEFAULT now() if this ends up creating a fresh row.
    """
    payload = {
        "id": playthrough_id,
        "video_path": video_path.replace("\\", "/"),
        "qrcode_path": qrcode_path.replace("\\", "/"),
        "microsite_url": microsite_url,
        "ingested_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if screenshot_path:
        payload["screenshot_path"] = screenshot_path.replace("\\", "/")

    response = requests.post(
        f"{POSTGREST_URL}/playthroughs?on_conflict=id",
        json=payload,
        headers={"Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"},
        timeout=15,
    )
    response.raise_for_status()

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


def _prepend_frame(video_path, still_path, hold_frames=INTRO_HOLD_FRAMES):
	"""Put the already-extracted still at the head of the video, in place.

	The point is the camera roll: a saved takeaway gets its thumbnail from the
	start of the file, so without this the guest's tile is whatever the render
	opens on rather than a shot of them.

	Returns True on success. Failure is logged and non-fatal -- same stance as
	_extract_frame, a cosmetic first frame isn't worth losing a takeaway over.
	"""
	# r_frame_rate comes back as a rational ("30/1"), not a float.
	raw_fps = _probe_stream(video_path, "v:0", "r_frame_rate")
	try:
		numerator, _, denominator = raw_fps.partition("/")
		fps = float(numerator) / float(denominator or 1)
	except ValueError:
		fps = 0
	if fps <= 0:
		_report("prepending", f"could not read frame rate (got {raw_fps!r}), skipping intro frame",
			level="warning")
		return False

	_report("prepending", video_path)

	hold_seconds = hold_frames / fps
	# Pass 1 skips the audio mux entirely when the shareable track is missing, so
	# don't assume there's an audio stream to delay.
	has_audio = bool(_probe_stream(video_path, "a:0", "codec_type"))

	# fps= here is load-bearing rather than redundant: a lone still carries no
	# frame duration, so concat computes a zero-length first segment and stacks
	# the video on top of the still at the same timestamp instead of after it --
	# leaving a 1-microsecond frame that no player or thumbnailer would use.
	# Setting the rate gives that frame a real duration. trim= pins the count
	# exactly, independent of how -t rounds.
	video_chain = (
		f"[0:v]trim=end_frame={hold_frames},setpts=PTS-STARTPTS,fps={fps},setsar=1[still];"
		f"[1:v]setsar=1[main];"
		f"[still][main]concat=n=2:v=1:a=0[v]"
	)
	# Delaying the audio by exactly the hold keeps the music bed landing on the
	# motion, and grows both streams equally so the output needs no -shortest.
	if has_audio:
		filtergraph = f"{video_chain};[1:a]adelay={int(round(hold_seconds * 1000))}:all=1[a]"
	else:
		filtergraph = video_chain

	temp_path = f"{video_path}.intro.mp4"
	command = [
		FFMPEG_PATH,
		"-y",
		"-loop", "1", "-framerate", str(fps), "-t", f"{hold_seconds:.6f}", "-i", still_path,
		"-i", video_path,
		"-filter_complex", filtergraph,
		"-map", "[v]",
	]
	if has_audio:
		command += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
	command += [
		"-c:v", "libx264",
		"-movflags", "+faststart",
		"-pix_fmt", "yuv420p",
		"-preset", "fast",
		# A notch better than pass 1's crf 20, to limit the generation loss from
		# encoding this clip a second time.
		"-crf", "18",
		temp_path,
	]

	result = subprocess.run(command,
		stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)

	if result.returncode != 0 or not os.path.isfile(temp_path):
		ffmpeg_log = result.stdout.decode(errors="replace")
		# Warning, not error: the takeaway is still fine, just without the intro frame.
		_report("prepending", f"intro frame prepend failed ({result.returncode})",
			level="warning", detail=ffmpeg_log[-2000:])
		if os.path.isfile(temp_path):
			os.remove(temp_path)
		return False

	# Swap in place, so the uploaded file and the path recorded in Postgres are
	# both unchanged and a half-written encode can never replace a good video.
	os.replace(temp_path, video_path)
	_report("prepended", f"{hold_frames} intro frame(s) -> {video_path}")
	return True


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


def _process_and_upload(file_name, audio_file_name, playthrough_id=None):
	if not file_name or not os.path.isfile(file_name):
		return {"status": "video_upload_error", "message": f"File not found: {file_name}"}

	base_name = file_name.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0]
	qrcode_file_name = os.path.join(QR_CODE_DIR, f"{base_name}_qrcode.png")
	output_file_name = os.path.join(PROCESSED_DIR, f"{base_name}_processed.mp4")
	_report("transcoding", output_file_name)

	# Muxes the shareable audio track in on the same pass rather than a second
	# ffmpeg call: a second -i for the audio, explicit -map so the output gets
	# video from input 0 and audio from input 1 (drops whatever audio, if any,
	# came in on the source clip), plus an audio codec since raw WAV doesn't
	# belong in an MP4 - AAC does. -shortest caps the output at whichever of
	# the two is shorter, so a length mismatch doesn't leave a silent tail or a
	# frozen frame; drop it if you'd rather always keep the full video length.
	has_audio = os.path.isfile(audio_file_name)
	if not has_audio:
		_report("transcoding", f"audio file not found at {audio_file_name}, processing without it",
			level="warning")

	ffmpeg_cmd = [FFMPEG_PATH, "-y", "-i", file_name]
	if has_audio:
		ffmpeg_cmd += ["-i", audio_file_name, "-map", "0:v:0", "-map", "1:a:0"]
	ffmpeg_cmd += [
		"-c:v", "libx264",
		"-movflags", "+faststart",
		"-pix_fmt", "yuv420p",
		"-preset", "fast",
		"-crf", "20",
	]
	if has_audio:
		ffmpeg_cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
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

	screenshot_file_name = os.path.join(SCREENSHOT_DIR, f"{base_name}_screenshot.png")
	screenshot_path = _extract_frame(output_file_name, screenshot_file_name)

	# Order is load-bearing: the still has to be extracted BEFORE the prepend
	# (afterwards SCREENSHOT_FRAME would point at a different moment, since every
	# frame shifts later), and the prepend has to happen BEFORE the upload, since
	# the file that gets shared is the one whose thumbnail we're fixing.
	if screenshot_path:
		_prepend_frame(output_file_name, screenshot_path)

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
	qrcode = segno.make_qr(takeaway_url)
	qrcode.save(qrcode_file_name, scale=20, border=2)
	_report("qrcode", qrcode_file_name)
	# Get the media onto the kiosk machine BEFORE completing the row below. The
	# kiosk treats a row with video_path set as ready to hand to a guest, so
	# writing that first would advertise media it can't actually read yet.
	# Video and QR are both load-bearing for the guest flow (screens 1 and 4),
	# so failing to publish either is a failed run -- leaving the row incomplete
	# keeps the takeaway out of the queue rather than serving a broken one.
	video_published = _publish_to_share(output_file_name)
	qrcode_published = _publish_to_share(qrcode_file_name)
	if not (video_published and qrcode_published):
		_report("error", "failed copying media to the kiosk share", level="error",
			video_published=video_published, qrcode_published=qrcode_published)
		return {"status": "video_upload_error", "message": "Failed copying media to the kiosk share"}

	# Best-effort by comparison: without it the operator gallery just falls back
	# to the video's first frame, so drop the path rather than fail the run.
	if screenshot_path and not _publish_to_share(screenshot_path):
		_report("publishing", "continuing without a screenshot -- the gallery will use the video's first frame",
			level="warning")
		screenshot_path = None

	# Reuse the id the Operator app minted at capture time (threaded through via
	# Setup()'s payload) so the Postgres `playthroughs` row this completes is the
	# SAME row the operator already created, rather than an orphaned second row.
	# Only falls back to a fresh uuid if that id is missing.
	id = playthrough_id or uuid.uuid4()
	_report("completing", str(id))
	_complete_playthrough(str(id), output_file_name, qrcode_file_name, takeaway_url, screenshot_path)
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

	# Main thread, so touching op.upload_control here is fine -- and it's the only place
	# the worker can be handed the queue, since RunInThread must not resolve operators.
	global _PROGRESS
	_PROGRESS = op.upload_control.GetProgressQueue()
	_report("queued", movie)

	return {"file_name": movie, "audio_file_name": audio_file, "playthrough_id": playthrough_id or None}


def RunInThread(tmClientExt: object, payload: object) -> None:
	"""
	Runs off the main thread. Must not touch any TD object - only plain Python
	(ffmpeg subprocess, HTTP upload, QR generation). Any raised exception is
	caught by the ThreadManager and routed to OnExcept below.
	"""
	result = _process_and_upload(payload["file_name"], payload.get("audio_file_name"), payload.get("playthrough_id"))
	tmClientExt.clientQueueManager.SetSuccessPayload(result)


def OnRefresh(tmClientExt: object, refreshPayload: object|None):
	pass


def OnSuccess(tmClientExt: object, successPayload: object):
	op.upload_control.HandleUploadResult(successPayload)


def OnExcept(tmClientExt: object, args):
	op.upload_control.HandleUploadException(args)
