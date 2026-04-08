import os
import traceback

# Force CPU only for Mac stability
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["NVIDIA_VISIBLE_DEVICES"] = ""

# OpenCC path for macOS
opencc_lib_path = "/opt/homebrew/opt/opencc/lib"
existing_dyld = os.environ.get("DYLD_LIBRARY_PATH", "")
if opencc_lib_path not in existing_dyld:
    os.environ["DYLD_LIBRARY_PATH"] = (
        f"{opencc_lib_path}:{existing_dyld}" if existing_dyld else opencc_lib_path
    )

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from nemo.collections import nlp as nemo_nlp
import torch

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "specialist-matching.nemo")

print("Loading model...")
model = nemo_nlp.models.IntentSlotClassificationModel.restore_from(MODEL_PATH)
model.eval()

if hasattr(model.cfg, "test_ds") and model.cfg.test_ds is not None:
    model.cfg.test_ds.num_workers = 0
    model.cfg.test_ds.pin_memory = False

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify({"error": "No input text provided"}), 400

    try:
        with torch.no_grad():
            predictions = model.predict_from_examples([text], model.cfg.test_ds)

        if not isinstance(predictions, (list, tuple)) or len(predictions) < 2:
            return jsonify({
                "error": "Unexpected prediction output format.",
                "details": str(predictions)
            }), 500

        pred_intents, pred_slots = predictions

        intent = pred_intents[0] if isinstance(pred_intents, (list, tuple)) else pred_intents
        slots_raw = pred_slots[0] if isinstance(pred_slots, (list, tuple)) else pred_slots

        words = text.split()

        if isinstance(slots_raw, str):
            slot_list = slots_raw.split()
        elif hasattr(slots_raw, "tolist"):
            slot_list = slots_raw.tolist()
        else:
            slot_list = list(slots_raw)

        slot_list = [str(slot) for slot in slot_list]

        slot_pairs = []
        for i, word in enumerate(words):
            slot_pairs.append({
                "word": word,
                "slot": slot_list[i] if i < len(slot_list) else "O"
            })

        return jsonify({
            "intent": str(intent),
            "slots": slot_pairs,
            "original_text": text
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Prediction failed.",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, host="127.0.0.1", port=5000)