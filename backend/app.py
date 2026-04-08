"""
File: app.py

Description:
This Flask application loads a trained NVIDIA NeMo intent and slot classification model
and exposes a simple web interface/API for predicting a user's intent and token-level slot labels.
It is configured to run locally, serve the main HTML page, and accept POST requests containing
input text for inference.

Main Features:
- Forces CPU-only execution for improved stability on macOS environments.
- Configures the OpenCC library path for compatibility on macOS systems.
- Loads a saved NeMo intent/slot classification model from the local models folder.
- Serves the main frontend page at the root route (/).
- Provides a /predict endpoint that accepts JSON input and returns:
  - the predicted intent
  - token-to-slot label pairs
  - the original input text

Expected Input:
- POST /predict
- JSON body in the format: { "text": "user input here" }

Expected Output:
- JSON response containing the predicted intent, slot labels for each word, and original text.
"""

import os
import traceback

# Force the application to use CPU only.
# This helps avoid GPU-related issues and improves runtime stability on some Mac systems.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["NVIDIA_VISIBLE_DEVICES"] = ""

# Add the OpenCC dynamic library path for macOS if it is not already present.
# This is needed in some local environments so dependent libraries can load correctly.
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

# Create the Flask application and define where HTML templates and static files are located.
app = Flask(__name__, template_folder="templates", static_folder="static")

# Enable Cross-Origin Resource Sharing so the frontend can communicate with the API
# even if it is served from a different origin during development.
CORS(app)

# Build the absolute path to the saved NeMo model file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "specialist-matching.nemo")

# Load the trained intent/slot classification model once when the server starts.
# This avoids reloading the model on every request and improves performance.
print("Loading model...")
model = nemo_nlp.models.IntentSlotClassificationModel.restore_from(MODEL_PATH)
model.eval()  # Set the model to evaluation mode for inference.

# Adjust test dataset loader settings for safer local inference behavior.
# Setting num_workers to 0 and pin_memory to False can help avoid multiprocessing
# and memory issues in local/macOS environments.
if hasattr(model.cfg, "test_ds") and model.cfg.test_ds is not None:
    model.cfg.test_ds.num_workers = 0
    model.cfg.test_ds.pin_memory = False


@app.route("/", methods=["GET"])
def index():
    """
    Render the main frontend page.

    Returns:
        HTML page for the user interface.
    """
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Receive input text from the client, run model inference,
    and return the predicted intent and slot labels as JSON.

    Expected JSON input:
        {
            "text": "sample user input"
        }

    Returns:
        JSON response containing:
        - intent: predicted intent label
        - slots: list of word/slot pairs
        - original_text: original submitted text
    """
    # Safely read the JSON body without raising an exception if parsing fails.
    data = request.get_json(silent=True)

    # Reject the request if no JSON body was provided.
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    # Extract and clean the input text from the request payload.
    text = str(data.get("text", "")).strip()

    # Reject empty input after trimming whitespace.
    if not text:
        return jsonify({"error": "No input text provided"}), 400

    try:
        # Disable gradient tracking since this is inference only, not training.
        with torch.no_grad():
            predictions = model.predict_from_examples([text], model.cfg.test_ds)

        # Validate the returned prediction structure before trying to unpack it.
        # The model is expected to return both intent predictions and slot predictions.
        if not isinstance(predictions, (list, tuple)) or len(predictions) < 2:
            return jsonify({
                "error": "Unexpected prediction output format.",
                "details": str(predictions)
            }), 500

        # Separate the model output into intent predictions and slot predictions.
        pred_intents, pred_slots = predictions

        # Extract the first intent prediction since only one input sentence is being processed.
        intent = pred_intents[0] if isinstance(pred_intents, (list, tuple)) else pred_intents

        # Extract the corresponding slot predictions for the first input sentence.
        slots_raw = pred_slots[0] if isinstance(pred_slots, (list, tuple)) else pred_slots

        # Split the original text into words so each token can be paired with a slot label.
        words = text.split()

        # Normalize the slot output into a standard Python list.
        # The model output format may vary depending on runtime/model configuration.
        if isinstance(slots_raw, str):
            slot_list = slots_raw.split()
        elif hasattr(slots_raw, "tolist"):
            slot_list = slots_raw.tolist()
        else:
            slot_list = list(slots_raw)

        # Convert all slot values to strings to ensure safe JSON serialization.
        slot_list = [str(slot) for slot in slot_list]

        # Pair each input word with its predicted slot label.
        # If there are fewer slot labels than words, assign "O" as the default slot.
        slot_pairs = []
        for i, word in enumerate(words):
            slot_pairs.append({
                "word": word,
                "slot": slot_list[i] if i < len(slot_list) else "O"
            })

        # Return the final structured prediction response.
        return jsonify({
            "intent": str(intent),
            "slots": slot_pairs,
            "original_text": text
        })

    except Exception as e:
        # Print the full traceback to the server console for debugging.
        traceback.print_exc()

        # Return a user-facing error message with basic exception details.
        return jsonify({
            "error": "Prediction failed.",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    # Run the Flask app locally on localhost:5000.
    # Debug and reloader are disabled to avoid duplicate model loads.
    app.run(debug=False, use_reloader=False, host="127.0.0.1", port=5000)