from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
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

# Attempt to load trained BiLSTM model and TextVectorization layer from toxicity_app/ or project root
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
        print(f"✅ Loaded BiLSTM model ({model_path}) and vectorizer ({vec_path})")
    else:
        print("ℹ️ Pre-trained toxicity.h5 / vectorizer.pkl not found; using 25PEC4CS1 Hybrid Statistical NLP + WSD Engine.")
except Exception as e:
    print(f"⚠️ TensorFlow model load skipped ({e}); using 25PEC4CS1 Hybrid Statistical NLP + WSD Engine.")


def evaluate_comment(comment_text: str):
    neural_preds = None
    if model is not None and vectorizer is not None:
        try:
            X_vec = vectorizer([comment_text])
            raw_pred = model.predict(X_vec, verbose=0)[0]
            neural_preds = dict(zip(LABELS, map(float, raw_pred)))
        except Exception as e:
            print(f"BiLSTM inference warning: {e}")

    pipeline_out = run_full_nlp_pipeline(comment_text, neural_preds=neural_preds)
    response_payload = dict(pipeline_out["predictions"])
    response_payload["syllabus_analysis"] = pipeline_out["syllabus_analysis"]
    response_payload["engine_mode"] = (
        "BiLSTM + 25PEC4CS1 Hybrid NLP Pipeline"
        if neural_preds
        else "25PEC4CS1 Statistical & WSD NLP Pipeline"
    )
    return response_payload


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', comment="", results=None, syllabus=None)


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
    app.run(host='0.0.0.0', port=5000, debug=False)
