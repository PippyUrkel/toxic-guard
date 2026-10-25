from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
REACT_DIST = os.path.join(PROJECT_ROOT, 'frontend', 'react', 'dist')

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from nlp_pipeline import run_full_nlp_pipeline

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
CORS(app)

LABELS = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

# Attempt to load trained BiLSTM model and TextVectorization layer
model = None
vectorizer = None
try:
    import tensorflow as tf
    candidate_models = [
        os.path.join(BASE_DIR, 'toxicity.h5'),
        os.path.join(BASE_DIR, 'best_model.h5'),
        os.path.join(PROJECT_ROOT, 'toxicity.h5'),
        os.path.join(PROJECT_ROOT, 'best_model.h5'),
    ]
    candidate_vecs = [
        os.path.join(BASE_DIR, 'vectorizer.pkl'),
        os.path.join(PROJECT_ROOT, 'vectorizer.pkl'),
    ]
    model_path = next((p for p in candidate_models if os.path.exists(p)), None)
    vec_path = next((p for p in candidate_vecs if os.path.exists(p)), None)

    if model_path and vec_path:
        model = tf.keras.models.load_model(model_path)
        with open(vec_path, 'rb') as f:
            vectorizer = pickle.load(f)
        print(f"[OK] Loaded BiLSTM model ({model_path}) and vectorizer ({vec_path})")
    else:
        print("[INFO] Pre-trained toxicity.h5 not detected; running 25PEC4CS1 Hybrid Statistical NLP & WSD Engine.")
except Exception as e:
    print(f"[INFO] TensorFlow model load skipped ({e}); running 25PEC4CS1 Hybrid Statistical NLP & WSD Engine.")


def evaluate_comment(comment_text: str):
    neural_preds = None
    if model is not None and vectorizer is not None:
        try:
            X_vec = vectorizer([comment_text])
            raw_pred = model.predict(X_vec, verbose=0)[0]
            neural_preds = dict(zip(LABELS, map(float, raw_pred)))
        except Exception as e:
            print(f"[WARN] BiLSTM inference warning: {e}")

    pipeline_out = run_full_nlp_pipeline(comment_text, neural_preds=neural_preds)
    response_payload = dict(pipeline_out["predictions"])
    response_payload["syllabus_analysis"] = pipeline_out["syllabus_analysis"]
    response_payload["engine_mode"] = (
        "BiLSTM + 25PEC4CS1 Hybrid NLP Pipeline"
        if neural_preds
        else "25PEC4CS1 Statistical & WSD NLP Pipeline"
    )
    return response_payload


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "engine": "BiLSTM + 25PEC4CS1 Classical Pipeline" if model is not None else "25PEC4CS1 Classical Pipeline",
        "labels": LABELS,
        "react_dist_available": os.path.exists(os.path.join(REACT_DIST, 'index.html'))
    })


@app.route('/', methods=['GET'])
def index():
    # If React frontend has been built into dist/ and classic view is not explicitly requested, serve the unified React app
    if os.path.exists(os.path.join(REACT_DIST, 'index.html')) and request.args.get('classic') != '1':
        return send_from_directory(REACT_DIST, 'index.html')
    return render_template('index.html', comment="", results=None, syllabus=None)


@app.route('/assets/<path:path>', methods=['GET'])
def serve_react_assets(path):
    assets_dir = os.path.join(REACT_DIST, 'assets')
    if os.path.exists(os.path.join(assets_dir, path)):
        return send_from_directory(assets_dir, path)
    return jsonify({"error": "Asset not found"}), 404


@app.route('/vite.svg', methods=['GET'])
def serve_vite_icon():
    if os.path.exists(os.path.join(REACT_DIST, 'vite.svg')):
        return send_from_directory(REACT_DIST, 'vite.svg')
    return ('', 204)


@app.route('/predict', methods=['POST'])
def predict():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        comment = data.get('comment', '')
        payload = evaluate_comment(comment)
        return jsonify(payload)
    else:
        comment = request.form.get('comment', '')
        payload = evaluate_comment(comment)
        results_only = {k: payload[k] for k in LABELS}
        return render_template(
            'index.html',
            comment=comment,
            results=results_only,
            syllabus=payload["syllabus_analysis"],
            engine_mode=payload["engine_mode"]
        )


if __name__ == '__main__':
    print("[START] ToxiGuard Flask API server running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
