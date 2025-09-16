
import gi
gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")

import sys, os, time, json, base64
from gi.repository import Gimp, GimpUi, Gegl, GObject, GLib, Gio, Gtk

#Top of File Definitions
sys.path.append(r"C:\Users\OlafW\AppData\Local\Programs\Python\Python313\Lib\site-packages")


def log_event(msg): #Log File initialized
    path = os.path.join(os.path.dirname(__file__), "gimpinator_log.txt")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

log_event("Log File Locked and Loaded")
log_event("🐍 Global scope executing...")
log_event(f"🐍 Python executable: {sys.executable}")


# allow a bundled 'requests' under ./vendor/
vendor = os.path.join(os.path.dirname(__file__), "vendor")
if vendor not in sys.path:
   sys.path.append(vendor)
try:
    import requests
    from datetime import datetime
    log_event(f"🧪 Requests and datetime Imported From: {vendor}")
except ImportError:
        requests = None

def read_config(config):
    log_event("🧪 Reading config")

    return {
    "backend": config.get_property("backend").lower(),
    "prompt": config.get_property("prompt"),
    "model": config.get_property("model"),
    "width": int(config.get_property("width")),
    "height": int(config.get_property("height")),
    "steps": int(config.get_property("steps")),
    "guidance": float(config.get_property("guidance")),
    "seed": int(config.get_property("seed")),
    "timeout": int(config.get_property("timeout")),
    "splash": bool(config.get_property("splash"))
    }
    log_event("🧪 Done Reading config")
    log_event("🐍 Global scope executing... just before gimpinate def")


def validate_mandatory_params(params):
    mandatory_keys = ["backend", "prompt", "model"]
    for key in mandatory_keys:
        if not params.get(key):
            log_event(f"❌ Missing mandatory value for {key}")
            raise ValueError(f"Mandatory parameter {key} is missing.")

def debug_config_properties(params):
    log_event("🔍 Debugging config properties:")
    for key, value in params.items():
        log_event(f"🔑 {key}: {value}")

def gimpinate(proc, run_mode, image, drawables, config, data):
    log_event(f"🧪 Invoked — run_mode={run_mode}")

# Interactive dialog
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init("python-fu-gimpinator")
        dlg = GimpUi.ProcedureDialog(procedure=proc, config=config)
        dlg.fill(None)
        if not dlg.run():
            dlg.destroy()
            log_event("❌ Dialog canceled")
            return proc.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
        dlg.destroy()

# ✅ Dialog completed — now grab config safely
    params = read_config(config)
    log_event(f"🧾 Loaded params: Dialog Completed {params}")
    validate_mandatory_params(params)
    debug_config_properties(params)
    #run_horde_backend(params, image)

#Backend Routing
    try:
        backend = config.get_property("backend")
        log_event(f"🧪 Routing to backend: {backend}")
        if backend == "horde": run_horde_backend(params, image)
        elif backend == "aiml": run_aiml_backend(params, image)
        elif backend == "local": run_local_backend(params, image)
        elif backend == "recraft": run_recraft_backend(params, image)
        else:
            log_event(f"❌ Unknown backend: {backend}")
    except Exception as e:
        log_event(f"❌ Routing failed: {str(e)}")

    # params = read_config(config)
    # log_event(f"🧾 Loaded params: Backend routing {params}")
    # validate_mandatory_params(params)
    # debug_config_properties(params)

    # backend = backend.lower() if backend else ""
    # log_event(f"🧪 Routing to backend: {backend}")
    # if backend == "local": run_local_backend(params, image)
    # elif backend == "recraft": run_recraft_backend(params, image)
    # elif backend == "huggingface": run_hf_backend(params, image)
    # elif backend == "aiml": run_aiml_backend(params, image)
    # elif backend == "horde": run_horde_backend(params, image)

def build_payload(params):
    try: 
        log_event("🧪 Start building payload")
        payload = {
        "prompt": params["prompt"],
        "params": {
            "width": params["width"],
            "height": params["height"],
            "steps": params["steps"],
            "cfg_scale": params["guidance"],
            "seed": str(params["seed"]),
            "sampler_name": "k_euler_a",
            "timeout": params["timeout"]
            }
        }
        log_event(f" Payload built: {payload}")
        return payload
    except KeyError as e:
        log_event(f" Missing parameter: {e}")
        raise

def send_request(endpoint, payload, headers):
    log_event("🧪 Start sending request")

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
            log_event(f"❌ Request failed: {e}")
            return None

def insert_image(image, img_data, prompt):
    try:
        log_event("🧪 start insert image")

        out = os.path.join(os.path.dirname(__file__), "ai", "output.png")
        with open(out, "wb") as f:
            f.write(img_data)

        gfile = Gio.File.new_for_path(out)
        layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile)
        layer.set_name(prompt[:20])
        image.insert_layer(layer, None, 0)

        log_event("✅ Image inserted")
    except Exception as e:
        log_event(f"❌ Failed to insert image: {e}")

    # ─── STABLE HORDE ────────────────────────────────────────────────────────
def run_horde_backend(params, image):

    log_event("🏇 Running Horde backend logic...")

    api_key = os.environ.get("HORDE_API_KEY", "")
    log_event(f"📤 Horde API Key retrieved: {api_key}")
    if not api_key:
        log_event("❌ API key for Horde not found")
        raise ValueError("Missing Horde API key")

    # Extract required parameters
    prompt   = params["prompt"]
    model    = params["model"]
    width    = params["width"]
    height   = params["height"]
    steps    = params["steps"]
    guidance = params["guidance"]
    seed     = str(params["seed"])     # Horde expects this as a string
    timeout  = params["timeout"]
    api_key  = params.get("api_key") or os.environ.get("HORDE_API_KEY", "")
    if not api_key:
        log_event("❌ API key for Horde not found")
        raise ValueError("Missing Horde API key")


    endpoint = "https://stablehorde.net/api/v2/generate/async"
    status_url = "https://stablehorde.net/api/v2/generate/status"

# Build payload for Horde API
    payload = {
        "prompt": prompt,
        "params": {
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": guidance,
            "seed": seed,
            "sampler_name": "k_euler_a",
            "timeout": timeout
        }
    }

    log_event(f"📤 Horde queue request: {payload}")

    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        log_event(f"📥 Horde response: {json_data}")

        job = json_data.get("id")
        if job:
            log_event(f"🆔 Job submitted — ID: {job}")
        else:
            log_event("⚠️ Horde response missing job ID")

#        except Exception as e:
#            log_event(f"❌ Horde request failed: {e}")

        img_data = None
        for _ in range(timeout):
            time.sleep(5)
            s = requests.get(f"{status_url}/{job}", headers=headers, timeout=timeout)
            js = s.json()
            log_event(f"⏳ Horde job {job} queue_position={js.get('queue_position')} done={js.get('done')}")

            if js.get("done") and js.get("generations"):
                gen = js["generations"][0]
                image_field = gen.get("img")

                if not image_field:
                    raise ValueError("No image found in Horde generation")

                if image_field.startswith("http"):
                    log_event("🔗 Detected image URL — downloading...")
                    img_data = requests.get(image_field, timeout=timeout).content
                else:
                    log_event(f"📎 First 12 chars of base64: {image_field[:12]}")
                    img_data = base64.b64decode(image_field)
                break

        if not img_data:
            s = requests.get(f"{status_url}/{job}", headers=headers, timeout=timeout)
            js = s.json()
            log_event("🧵 Final job state:" + json.dumps(js, indent=2))
            raise TimeoutError(f"Horde job {job} didn’t finish or returned no image")

        out = os.path.join(os.path.dirname(__file__), "ai", "horde.png")
        with open(out, "wb") as f:
            f.write(img_data)

            gfile = Gio.File.new_for_path(out)
            layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile)
            layer.set_name(prompt[:20])
            image.insert_layer(layer, None, 0)
            log_event("✅ Inserted Horde image")

    except Exception as e:
        log_event(f"❌ Horde error: {str(e)}")

        out_fb = os.path.join(os.path.dirname(__file__), "ai", "hordefb.png")
        gfile_fb = Gio.File.new_for_path(out_fb)
        layer_fb = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile_fb)
        layer_fb.set_name("Horde Fallback")
        image.insert_layer(layer_fb, None, 0)
        log_event("✅ Inserted Horde fallback image")

    # ─── LOCAL ──────────────────────────────────────────────────────────────
def run_local_backend(params, image):

    log_event("🏇 Running Local backend logic...")

    if not requests:
        log_event("❌ Missing requests for local")
            #return proc.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error
            
    # Extract required parameters
    prompt   = params["prompt"]
    model    = params["model"]
    width    = params["width"]
    height   = params["height"]
    steps    = params["steps"]
    guidance = params["guidance"]
    seed     = str(params["seed"])     # Horde expects this as a string
    timeout  = params["timeout"]
    api_key  = params.get("api_key") or os.environ.get("HORDE_API_KEY", "")
    try:
        payload = {"prompt":prompt,"model":model,
                   "width":width,"height":height,
                   "steps":steps,"guidance":guidance,
                   "seed":seed,"timeout":timeout}
        log_event("📤 Local payload:\n" + json.dumps(payload, indent=2))
        r = requests.post("http://127.0.0.1:8000/generate",
                          json=payload, timeout=timeout)
        log_event("📥 Local response: " + r.text)
        d = r.json()
        img = d.get("image_path") or d.get("image") or d.get("path")
        if not img or not os.path.exists(img):
            raise FileNotFoundError(img)
        gfile = Gio.File.new_for_path(img)
        layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile)
        image.insert_layer(layer, None, 0)
        log_event("🖼️ Inserted local image")
    except Exception as e:
        log_event("❌ Local error: " + str(e))
        fb = os.path.join(os.path.dirname(__file__), "ai", "local_fallback.png")
        if os.path.exists(fb):
            gfile = Gio.File.new_for_path(fb)
            ly = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile)
            image.insert_layer(ly, None, 0)
            log_event("🪂 Inserted local fallback")

    # ─── AI/ML ────────────────────────────────────────────────────────────
def run_aiml_backend(params, image):
    try:
        log_event("🤖 Running AIML backend logic...")
        endpoint = "https://api.aimlapi.com/v1/images/generations"
        api_key = os.getenv("AIML_API_KEY")
        log_event(f"📤 AIML API Key retrieved: {api_key}")
        payload = {
        "model": "flux/schnell",
        "prompt": "A jellyfish in the ocean",
        "guidance_scale": 7.5,
        "safety_tolerance": "2",
        "output_format": "jpeg",
        "aspect_ratio": "1:1",
        "num_images": 1,
        "seed": 1661789076
        }
        log_event(f"📦 AIML payload: {payload}")
        headers = {
        "Authorization": f"Bearer {os.getenv("AIML_API_KEY")}",
        "Content-Type": "application/json"
        }
        log_event(f"✅ Modules available: os={type(os)}, requests={type(requests)}")
        response = requests.post(endpoint, json=payload, headers=headers)
        log_event(f"📎 AIML response status: {response.status_code}") 
        data = response.json()
        log_event(f"📎 AIML image field preview: {data}")
        if "images" in data and len(data["images"]) > 0:
            image_url = data["images"][0]["url"].strip()
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type")
            ext = "jpg"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    except Exception as e:
        log_event(f"❌ AIML error: {str(e)}")
        log_event("✅ Inserted AIML fallback image")


    # ─── HUGGING FACE ────────────────────────────────────────────────────────
def run_hf_backend(params, image):

    log_event("🏇 Running Hugging Face backend logic...")

    api_key = os.environ.get("HORDE_API_KEY", "")
    log_event(f"📤 Horde API Key retrieved: {api_key}")
    if not api_key:
        log_event("❌ API key for Horde not found")
        raise ValueError("Missing Horde API key")

    # Extract required parameters
    prompt   = params["prompt"]
    model    = params["model"]
    width    = params["width"]
    height   = params["height"]
    steps    = params["steps"]
    guidance = params["guidance"]
    seed     = str(params["seed"])     # Horde expects this as a string
    timeout  = params["timeout"]
    api_key  = params.get("api_key") or os.environ.get("HORDE_API_KEY", "")
    if not api_key:
        log_event("❌ API key for Horde not found")
        raise ValueError("Missing Horde API key")


    endpoint = "https://stablehorde.net/api/v2/generate/async"
    status_url = "https://stablehorde.net/api/v2/generate/status"

# Build payload for Horde API
    payload = {
        "prompt": prompt,
        "params": {
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": guidance,
            "seed": seed,
            "sampler_name": "k_euler_a",
            "timeout": timeout
        }
    }

    log_event(f"📤 Horde queue request: {payload}")

    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        log_event(f"📥 Horde response: {json_data}")

        job = json_data.get("id")
        if job:
            log_event(f"🆔 Job submitted — ID: {job}")
        else:
            log_event("⚠️ Horde response missing job ID")

#        except Exception as e:
#            log_event(f"❌ Horde request failed: {e}")

        img_data = None
        for _ in range(timeout):
            time.sleep(5)
            s = requests.get(f"{status_url}/{job}", headers=headers, timeout=timeout)
            js = s.json()
            log_event(f"⏳ Horde job {job} queue_position={js.get('queue_position')} done={js.get('done')}")

            if js.get("done") and js.get("generations"):
                gen = js["generations"][0]
                image_field = gen.get("img")

                if not image_field:
                    raise ValueError("No image found in Horde generation")

                if image_field.startswith("http"):
                    log_event("🔗 Detected image URL — downloading...")
                    img_data = requests.get(image_field, timeout=timeout).content
                else:
                    log_event(f"📎 First 12 chars of base64: {image_field[:12]}")
                    img_data = base64.b64decode(image_field)
                break

        if not img_data:
            s = requests.get(f"{status_url}/{job}", headers=headers, timeout=timeout)
            js = s.json()
            log_event("🧵 Final job state:" + json.dumps(js, indent=2))
            raise TimeoutError(f"Horde job {job} didn’t finish or returned no image")

        out = os.path.join(os.path.dirname(__file__), "ai", "horde.png")
        with open(out, "wb") as f:
            f.write(img_data)

            gfile = Gio.File.new_for_path(out)
            layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile)
            layer.set_name(prompt[:20])
            image.insert_layer(layer, None, 0)
            log_event("✅ Inserted Horde image")

    except Exception as e:
        log_event(f"❌ Horde error: {str(e)}")

        out_fb = os.path.join(os.path.dirname(__file__), "ai", "hordefb.png")
        gfile_fb = Gio.File.new_for_path(out_fb)
        layer_fb = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile_fb)
        layer_fb.set_name("Horde Fallback")
        image.insert_layer(layer_fb, None, 0)
        log_event("✅ Inserted Horde fallback image")

    # ─── RECRAFT ─────────────────────────────────────────────────────────────

def wire_image_to_gimp_layer(image_path):
    try:
        from gi.repository import Gimp, GLib
        import os

        log_event(f"🔗 Wiring image into GIMP layer: {image_path}")

        ext = os.path.splitext(image_path)[1].lower()
        if ext == ".png":
            proc_name = "file-png-load"
        elif ext == ".webp":
            proc_name = "file-webp-load"
        elif ext in [".jpg", ".jpeg"]:
            proc_name = "file-jpeg-load"
        else:
            log_event(f"❌ Unsupported file extension: {ext}")
            return

        pdb = Gimp.get_pdb()
        args = [
            GLib.Variant('i', Gimp.RunMode.NONINTERACTIVE),
            GLib.Variant('s', image_path),
            GLib.Variant('s', image_path)
        ]

        result = pdb.run_procedure(proc_name, args)
        image = result.index(1)  # Gimp.Image object
        layer = image.get_active_layer()
        image.insert_layer(layer, None, -1)

        log_event("✅ Image successfully wired into GIMP layer.")
    except Exception as e:
        log_event(f"❌ Failed to wire image into GIMP layer: {str(e)}")


def run_subprocess_logic(params, image):
    import subprocess, os, json
    from datetime import datetime

    try:
        log_event("🚀 Launching Recraft subprocess via Python 3.13...")

        base_dir = os.path.abspath(os.path.dirname(__file__))
        script_path = os.path.join(base_dir, "recraft_script.py")
        log_event(f"🎨 base_dir received: {base_dir}")
        log_event(f"🎨 script_path received: {script_path}")

        serialized_params = json.dumps(params)
        python_exe = r"C:\Users\Olafw\AppData\Local\Programs\Python\Python313\python.exe"
        result = subprocess.run( [python_exe, script_path, "--params", serialized_params], capture_output=True, text=True )
        log_event(f"🎨 Result: {result}")

        if result.returncode != 0:
            log_event(f"❌ Subprocess failed — stderr:{result.stderr.strip()}")
        else:
            log_event("✅ Subprocess completed successfully.")
            log_event(f"📤 Subprocess output: {result.stdout.strip()}")

        if result.returncode == 0:
            log_event("✅ Subprocess completed successfully.")
            try:
                response_data = json.loads(result.stdout.strip())
                image_url = response_data.get("image")

                if image_url:
                    log_event(f"🎨 Image URL received: {image_url}")
                    image_path = run_python_ex(image_url, image)
                    return image_path
                else:
                    log_event("⚠️ No image URL found in subprocess output.")
                    return None
            except Exception as e:
                log_event(f"❌ Failed to parse subprocess output: {str(e)}")
        else:
            log_event(f"❌ Subprocess error — stderr: {result.stderr.strip()}")

    except Exception as e:
        log_event(f"❌ Subprocess execution crashed: {str(e)}")

        log_event(f"✅ Confirmed subprocess completion and logged entries.")

        if os.path.exists(image_path):
            wire_image_to_gimp_layer(image_path)

def run_recraft_backend(params, image):
    log_event("🔧 Entering Recraft backend logic...")
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        image_path = run_subprocess_logic(params, image)
        fallback_path = os.path.join(base_dir, "ai", "recraftfb.png")

        if image_path and os.path.exists(image_path):
            wire_image_to_gimp_layer(image_path)
        else:
            log_event("⚠️ Falling back to Recraft placeholder image.")
            wire_image_to_gimp_layer(fallback_path)
    except Exception as e:
        log_event(f"❌ Subprocess Recraft error: {str(e)}")
        fallback_path = os.path.join(base_dir, "ai", "recraftfb.png")
        gfile_fb = Gio.File.new_for_path(fallback_path)
        layer_fb = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile_fb)
        layer_fb.set_name("Recraft Fallback")
        image.insert_layer(layer_fb, None, 0)
        log_event("✅ Inserted Recraft fallback image")


def run_python_ex(image_url, image):
    try:
        import requests, os
        from datetime import datetime

        # Download image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Safely detect file extension from MIME type
        content_type = response.headers.get("Content-Type", "")
        ext = "jpg"  # Fallback default
        log_event(f"🧪 Detected MIME type: {content_type}")

        content_type = response.headers.get("Content-Type", "")
        ext = "webp"  # default fallback

        if "image/png" in content_type:
            ext = "png"
        elif "image/jpeg" in content_type:
            ext = "jpg"
        elif "image/webp" in content_type:
            ext = "webp"
        elif "image/" in content_type:
            ext = content_type.split("/")[-1]  # catch-all fallback for valid MIME types

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = os.path.abspath(os.path.dirname(__file__))
        image_path = os.path.join(base_dir, "ai", f"recraft_{timestamp}.{ext}")

        # Save image locally
        with open(image_path, "wb") as f:
            f.write(response.content)
        #    wire_image_to_gimp_layer(image_path)
            log_event(f"✅ Recraft image downloaded to: {image_path}")
        return image_path

    except Exception as e:
        log_event(f"❌ run_python_ex failed: {str(e)}")


    #Automatically wire image into GIMP layer after download
def auto_wire_image_to_gimp_layer():
    try:
        image_path = "path_to_downloaded_image"
        wire_image_to_gimp_layer(image_path)
        log_event("✅ Automatically wired image into GIMP layer.")
    except Exception as e:
        log_event(f"❌ Failed to auto-wire image into GIMP layer: {str(e)}")


# def run_recraft_backend(params, image):
    # try:
        # from openai import OpenAI
        # log_event("🎨 Running Recraft backend logic...")
        # client = OpenAI(base_url="https://external.api.recraft.ai/v1",
        # api_key=os.getenv("RECRAFT_API_TOKEN"))
        # api_token = os.getenv("RECRAFT_API_TOKEN")
        # masked_token = f"{api_token[:6]}******" if api_token else "None"
        # log_event(f"🔐 Using Recraft API Token: {masked_token}")
        # prompt = params.get("prompt", "a staggering horse")
        # style = params.get("style", "realistic_image")
        # size = f"{params.get("width",1024)}x{params.get("height",1024)}"
        # log_event(f"📦 Recraft payload: prompt='{prompt}', style='{style}', size='{size}'")
        # response = client.images.generate(prompt=prompt,style=style,size=size)
        # image_url = response.data[0].url
        # log_event(f"🎨 Recraft image URL: {image_url}")
    # except ImportError:
        # log_event("❌ Missing openai module — try installing it manually.")
    
        # img_data = None
        # for _ in range(timeout):
            # time.sleep(5)
            # s = requests.get(f"{status_url}/{job}", headers=headers, timeout=timeout)
            # js = s.json()
            # log_event(f"⏳ Horde job {job} queue_position={js.get('queue_position')} done={js.get('done')}")

            # if js.get("done") and js.get("generations"):
                # gen = js["generations"][0]
                # image_field = gen.get("img")

                # if not image_field:
                    # raise ValueError("No image found in Horde generation")

                # if image_field.startswith("http"):
                    # log_event("🔗 Detected image URL — downloading...")
                    # img_data = requests.get(image_field, timeout=timeout).content
                # else:
                    # log_event(f"📎 First 12 chars of base64: {image_field[:12]}")
                    # img_data = base64.b64decode(image_field)
                # break

        # if not img_data:
            # s = requests.get(f"{status_url}/{job}", headers=headers, timeout=timeout)
            # js = s.json()
            # log_event("🧵 Final job state:" + json.dumps(js, indent=2))
            # raise TimeoutError(f"Horde job {job} didn’t finish or returned no image")

        # out = os.path.join(os.path.dirname(__file__), "ai", "horde.png")
        # with open(out, "wb") as f:
            # f.write(img_data)

            # gfile = Gio.File.new_for_path(out)
            # layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile)
            # layer.set_name(prompt[:20])
            # image.insert_layer(layer, None, 0)
            # log_event("✅ Inserted Horde image")

    # except Exception as e:
        # log_event(f"❌ Horde error: {str(e)}")

        # out_fb = os.path.join(os.path.dirname(__file__), "ai", "hordefb.png")
        # gfile_fb = Gio.File.new_for_path(out_fb)
        # layer_fb = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, gfile_fb)
        # layer_fb.set_name("Horde Fallback")
        # image.insert_layer(layer_fb, None, 0)
        # log_event("✅ Inserted Horde fallback image")


class Gimpinator(Gimp.PlugIn):
    def do_query_procedures(self):
        return ["python-fu-gimpinator"]

    def do_create_procedure(self, name):
        log_event("🚀 Registering Gimpinator EX")
        Gegl.init(None)
        proc = Gimp.ImageProcedure.new(self, name,
            Gimp.PDBProcType.PLUGIN, gimpinate, None)
        proc.set_image_types("*")
        proc.set_menu_label("Gimpinator EX")
        proc.add_menu_path("<Image>/Filters/Gimpinator")
        proc.set_documentation(
            "Generate an AI image from prompt",
            "Multi-backend AI image generation",
            "https://github.com/yourname/gimpinator-ex"
        )
        proc.set_attribution("Olaf & Copilot","Distributed Bananas Inc.","2025")

        proc.add_string_argument(
            "prompt","_Prompt","Describe the image","",GObject.ParamFlags.READWRITE
        )
        proc.add_string_argument(
            "backend","_Backend",
            "Type 'local','aiml','hf','recraft' or 'horde'",
            "local",GObject.ParamFlags.READWRITE
        )
        proc.add_string_argument(
            "model","_Model","AI model name","DreamShaper v8",GObject.ParamFlags.READWRITE
        )
        proc.add_int_argument("width","_Width (px)","Image width",1024,1024,1024,GObject.ParamFlags.READWRITE)
        proc.add_int_argument("height","_Height (px)","Image height",1024,1024,1024,GObject.ParamFlags.READWRITE)
        proc.add_int_argument("steps","Steps","Inference steps",30,30,30,GObject.ParamFlags.READWRITE)
        proc.add_double_argument("guidance","Guidance","Prompt guidance",7.5,7.5,7.5,GObject.ParamFlags.READWRITE)
        proc.add_int_argument("seed", "Seed", "Random seed",0,0,0, GObject.ParamFlags.READWRITE)
        #proc.add_int_argument("seed","Seed","Random seed",1111,1111,1111,GObject.ParamFlags.READWRITE)
        proc.add_int_argument("timeout","Timeout (s)","Request timeout",30,30,30,GObject.ParamFlags.READWRITE)
        proc.add_boolean_argument("splash","Splash","Add splash layer",True,GObject.ParamFlags.READWRITE)

        return proc

Gimp.main(Gimpinator.__gtype__, sys.argv)
