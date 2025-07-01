---

## 🧠 Gimpinator EX – AI Art Plug-in for GIMP 3

> **⚠️ Rated R for Recursive Refactoring, Rogue TypeErrors, and Graphic Procedural Violence. Viewer discretion advised.**

**Gimpinator EX** is a next-generation **AI image generation plug-in for GIMP 3.x**. It connects your canvas to AI art models like **Stable Diffusion**, giving you the power to create stunning visuals directly inside GIMP—no web browser, no separate tools, just raw creative force.

---

### ✨ What Is It?

Gimpinator EX is a free, open-source **AI plug-in for GIMP** that brings:

- 🎨 Direct **text-to-image AI generation**
- 🧬 Built-in support for popular models like `sdxl`, `dreamshaper`, and more
- 🛠️ Configurable resolution, prompt strength (CFG), and generation steps
- 🔄 Smart timeouts and request handling
- 🎛️ Seamless integration with Stable Horde or your own AI backend

This plug-in turns GIMP into your personal AI image lab.

---

### 🤖 Use It Free — or Plug In Your Own AI Key

By default, Gimpinator connects to **Stable Horde**, a free and distributed AI generation network, meaning:

- ✅ Use it out of the box—no API key required  
- 🔐 Or enter **your own API keys or backends** to add models or faster queues  
- 💸 No tokens, credits, or paywalls—unless you opt into custom infrastructure

Want simple? It's ready. Want powerful and personalized? It's ready for that too.

---

### 🚀 Installation

1. Download this repo or clone it with Git:
   ```bash
   git clone https://github.com/yourname/gimpinator.git
   ```
2. Place `gimpinator_ex.py` into your GIMP plug-ins folder:
   - **Windows**:  
     `C:\Users\<YOU>\AppData\Roaming\GIMP\3.0\plug-ins\`
   - **Linux/macOS**:  
     `~/.config/GIMP/3.0/plug-ins/`
3. (Linux/macOS only): Make it executable:
   ```bash
   chmod +x gimpinator_ex.py
   ```
4. Restart GIMP → Look under `Filters` → `Gimpinator EX 🧠`

---

### 🧪 How to Generate AI Images

- Write a creative prompt like _"a cat piloting a mech suit over Tokyo at sunrise"
- Choose a model, resolution, and sampler
- Click OK—and your AI artwork will appear directly on your active canvas layer  

Want to generate variants? Just adjust the seed or prompt and repeat!

---

### 🔧 Backend Settings

You can configure custom AI sources by adding parameters to the plug-in’s backend list or patching the default to accept:
- Stable Diffusion APIs
- Personal Horde worker URLs
- Private model endpoints (with API key authentication)

---

### 🧙‍♂️ Troubleshooting

- If the plug-in doesn't appear in GIMP, run GIMP from a terminal to view logs.
- Many errors are due to API quirks or binding mismatches in GIMP 3—*we’ve danced with them all*.
- Gimpinator ships with dropdown parsing guards to help protect you from the darkest exceptions.

---

### 🧭 Keywords for Discoverability

> gimp ai plugin, gimp plugin ai, ai art plugin for gimp, gimp plug-in for stable diffusion, gimp ai image generation, gimp ai art, gimp ai tool, gimp text to image plug-in, gimpinator ai

---

### 🧾 License

MIT License. Use it. Remix it. Ship it with your own models. Just don’t blame us if GIMP eats your canvas mid-prompt.

---