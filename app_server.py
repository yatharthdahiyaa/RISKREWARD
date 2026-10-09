"""
app_server.py
=============
Enterprise Production Web Server & AI Decision API
Platform: SAS Viya Visual Analytics Portal & AavishkarHacks Decision Engine
Serves static dashboard files and provides live REST API endpoints:
  - POST /api/analyze-resume
  - POST /api/skill-card
  - POST /api/ai-analytic
"""

import os
import sys
import json
import urllib.request
from flask import Flask, request, jsonify, send_from_directory
from resume_decision_engine import (
    parse_resume,
    generate_skill_investment_card,
    run_ai_analytic_critique
)
from predict_candidate import predict_candidate

app = Flask(__name__, static_folder=".", static_url_path="")

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from google import genai
    from google.genai.errors import ClientError, APIError
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

def build_gemini_prompt(parsed_resume, card_result):
    """
    Constructs a scientifically grounded prompt for Google Gemini based on the Approach Note.
    """
    scores = parsed_resume.get('scores', {})
    exp = parsed_resume.get('experience_yrs', 1.0)
    role = parsed_resume.get('target_role', 'Data Analyst/Analytics')
    city = parsed_resume.get('primary_city', 'Bengaluru')
    dec = card_result.get('card_decision', {})

    prompt = f"""
You are an expert Chief Talent Scientist & Labor Economist evaluating a data science candidate resume according to the empirical findings of the AavishkarHacks study ("Listed, Paid, Rewarded: The Forensic Reality of Analytics Careers").

CANDIDATE PROFILE:
- Target Role: {role}
- Experience: {exp} years
- Primary City: {city}
- Extracted Skill Domain Scores (1.0 to 5.0 scale):
  * Big Data: {scores.get('big_data', 3.0)}/5.0
  * Mathematics & Statistics: {scores.get('maths_stats', 3.0)}/5.0
  * Core Coding: {scores.get('core_coding', 3.0)}/5.0
  * AI/ML: {scores.get('ai_ml', 3.0)}/5.0
  * Dashboards & Storytelling: {scores.get('dashboards', 3.0)}/5.0

EMPIRICAL BENCHMARK CONSTRAINTS & PRINCIPLES:
1. Principle 1 (Compare Like with Like): Market premiums must be reported after controlling for experience and role family. In entry roles, Core Coding gives a +12.5% salary premium (OR 1.48 within-role) and Big Data gives +11.0% (OR 1.37). AI/ML is at market parity (OR 0.99 [0.74, 1.33]) at entry level once experience is controlled.
2. Principle 2 (Show Uncertainty Everywhere): Estimates carry 95% BCa bootstrap intervals over 2,000 resamples.
3. Principle 4 (Abstain Rather than Guess): If Core Coding or Maths rating is < 2.2, abstain from niche models and mandate foundational remediation.
4. Internal Reward Asymmetry: While the market lists coding/big data, internal promotions and high hikes are heavily driven by Maths & Statistics (OR 4.62, #1 in 65% of bootstrap draws) and Dashboards/Storytelling (OR 3.52).
5. Current Decision Engine Output:
   - Status: {dec.get('status')}
   - Headline: {dec.get('headline')}
   - Recommended Skill: {dec.get('recommended_skill')} (Win share: {dec.get('win_share')}%)
   - Directive: {dec.get('directive')}

TASK:
Write a rigorous, 3-paragraph executive diagnostic critique of this candidate's resume:
1. Paragraph 1: Career-Stage Reality Check (Compare Like with Like) - Analyze their technical balance against actual market entry pricing vs edtech hype.
2. Paragraph 2: Internal Reward vs Market Asymmetry - Address the gap between what job descriptions list and what internally wins promotion hikes (Maths & Stats OR 4.62, Storytelling OR 3.52).
3. Paragraph 3: Strategic 6-Month Action Plan - Provide concrete, actionable directive based on the verified recommendation and mention top fresher-friendly employers (Accenture, Genpact, TCS, Cognizant) if applicable.

Maintain a professional, forensic, and encouraging tone. Use markdown formatting with bold headings.
"""
    return prompt.strip()


def call_gemini_api(prompt, api_key=None, model="gemini-3.5-flash-lite"):
    """
    Calls Google Gemini using the official google-genai 2.29.0 SDK.
    Supports gemini-3.5-flash-lite, gemini-3.8-flash, and gemini-flash-latest.
    """
    key = api_key or DEFAULT_GEMINI_KEY
    if not key:
        return {"success": False, "error": "No API key provided", "reason": "NO_KEY", "status": "ERROR"}

    # Try list of active production models
    candidate_models = [model, "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]
    tried_models = set()

    for m in candidate_models:
        if m in tried_models:
            continue
        tried_models.add(m)

        if HAS_GENAI_SDK:
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if response and response.text:
                    return {
                        "success": True,
                        "text": response.text,
                        "provider": f"Google Gemini ({m} • Live Cloud API)",
                        "model": m,
                        "status": "SUCCESS"
                    }
            except Exception as e:
                err_str = str(e)
                if "404" in err_str or "NOT_FOUND" in err_str:
                    continue  # Try next candidate model
                reason = "CONSUMER_SUSPENDED" if "CONSUMER_SUSPENDED" in err_str else "API_ERROR"
                return {
                    "success": False,
                    "error": err_str,
                    "reason": reason,
                    "status": "ERROR"
                }

    return {"success": False, "error": "No active Gemini model responded", "reason": "MODEL_UNAVAILABLE", "status": "ERROR"}

    # 2. Secondary: Direct HTTP REST
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            text = res_body["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "success": True,
                "text": text,
                "provider": f"Google Gemini 2.0 Flash (REST API)",
                "model": model,
                "status": "SUCCESS"
            }
    except urllib.error.HTTPError as e:
        err_msg = ""
        err_reason = f"HTTP_{e.code}"
        try:
            err_json = json.loads(e.read().decode("utf-8"))
            err_msg = err_json.get("error", {}).get("message", str(e))
            details = err_json.get("error", {}).get("details", [])
            if details and isinstance(details, list) and len(details) > 0:
                err_reason = details[0].get("reason", err_reason)
        except Exception:
            err_msg = f"HTTP {e.code}: {e.reason}"

        return {
            "success": False,
            "error": err_msg,
            "reason": err_reason,
            "http_code": e.code,
            "status": "ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "reason": "NETWORK_OR_TIMEOUT",
            "status": "ERROR"
        }


# -----------------------------------------------------------------------------
# 1. STATIC FILE ROUTES
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(WORKSPACE_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    if os.path.exists(os.path.join(WORKSPACE_DIR, path)):
        return send_from_directory(WORKSPACE_DIR, path)
    return jsonify({"error": "File not found"}), 404

# -----------------------------------------------------------------------------
# 2. REST API ENDPOINTS
# -----------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "engine": "AavishkarHacks Tri-Axial Empirical Decision Engine",
        "version": "2.0_enterprise",
        "gemini_api_configured": bool(DEFAULT_GEMINI_KEY),
        "models_loaded": [
            "ordinal_salary_model.joblib",
            "jds_hike_logistic.joblib",
            "sds_logit_ocean.joblib",
            "sds_rf_leakage_audit.joblib"
        ]
    })

@app.route("/api/test-gemini-key", methods=["POST"])
def api_test_gemini_key():
    """
    Test connectivity of a provided Google Gemini API key.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        key = data.get("gemini_api_key") or DEFAULT_GEMINI_KEY
        result = call_gemini_api("Please reply with: 'Google Gemini Connected'", api_key=key)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/upload-resume", methods=["POST"])
def api_upload_resume():
    """
    Accepts uploaded resume file (.pdf, .docx, .txt, .json), extracts clean text,
    and returns extracted text for analysis.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file part in request"}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400

        filename = file.filename.lower()
        content_bytes = file.read()
        extracted_text = ""

        if filename.endswith(".pdf"):
            try:
                import fitz
                doc = fitz.open(stream=content_bytes, filetype="pdf")
                pages_text = [page.get_text() for page in doc]
                extracted_text = "\n".join(pages_text).strip()
            except Exception as pdf_err:
                return jsonify({"success": False, "error": f"Failed to extract PDF text: {str(pdf_err)}"}), 400
        elif filename.endswith(".docx"):
            try:
                import docx
                import io
                doc = docx.Document(io.BytesIO(content_bytes))
                paras = [p.text for p in doc.paragraphs if p.text]
                extracted_text = "\n".join(paras).strip()
            except Exception as docx_err:
                return jsonify({"success": False, "error": f"Failed to extract DOCX text: {str(docx_err)}"}), 400
        else:
            try:
                extracted_text = content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                extracted_text = content_bytes.decode('latin-1', errors='ignore')

        if not extracted_text.strip():
            return jsonify({"success": False, "error": "Extracted resume content is empty"}), 400

        return jsonify({
            "success": True,
            "filename": file.filename,
            "text": extracted_text,
            "character_count": len(extracted_text),
            "word_count": len(extracted_text.split())
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/analyze-resume", methods=["POST"])
def api_analyze_resume():
    """
    Parses resume text, evaluates the 4 Design Principles, runs 2,000 bootstrap draws,
    and returns the verified Skill Investment Card and AI Critique.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        resume_text = data.get("resume_text", "").strip()

        if not resume_text:
            return jsonify({"error": "Empty resume text provided"}), 400

        # Step 1: NLP Parsing of Resume
        parsed = parse_resume(resume_text)

        # Allow user overrides if sent in payload
        if "experience_yrs" in data:
            parsed["experience_yrs"] = float(data["experience_yrs"])
        if "target_role" in data:
            parsed["target_role"] = data["target_role"]
        if "primary_city" in data:
            parsed["primary_city"] = data["primary_city"]
        if "scores_override" in data and isinstance(data["scores_override"], dict):
            for k, v in data["scores_override"].items():
                if k in parsed["scores"]:
                    parsed["scores"][k] = float(v)

        # Step 2: Generate Skill Investment Card (Section 4.5 & Design Principles)
        card_result = generate_skill_investment_card(
            scores=parsed["scores"],
            experience_yrs=parsed["experience_yrs"],
            role_family=parsed["target_role"],
            city=parsed["primary_city"]
        )

        # Step 3: Run Multi-Model Predictions from Joblib
        joblib_preds = predict_candidate(
            big_data=parsed["scores"]["big_data"],
            maths=parsed["scores"]["maths_stats"],
            coding=parsed["scores"]["core_coding"],
            ai_ml=parsed["scores"]["ai_ml"],
            dashboards=parsed["scores"]["dashboards"],
            experience_yrs=parsed["experience_yrs"],
            metro=parsed["primary_city"],
            ocean=parsed.get("ocean_traits")
        )

        # Step 4: AI Analytic Critique (Attempt Google Gemini API, fallback to Empirical Engine)
        gemini_key = data.get("gemini_api_key") or data.get("api_key") or DEFAULT_GEMINI_KEY
        gemini_prompt = build_gemini_prompt(parsed, card_result)
        gemini_result = call_gemini_api(gemini_prompt, api_key=gemini_key)

        if gemini_result["success"]:
            ai_critique = gemini_result["text"]
            ai_provider = gemini_result["provider"]
            gemini_details = {
                "status": "LIVE_API_SUCCESS",
                "provider": ai_provider,
                "model": gemini_result.get("model", "gemini-2.0-flash")
            }
        else:
            # High-fidelity empirical synthesis grounded in Section 2.2 principles
            ai_critique = run_ai_analytic_critique(parsed, card_result)
            ai_provider = "SAS Viya Empirical AI Decision Engine (Section 2.2 Forensic)"
            gemini_details = {
                "status": "AUTONOMOUS_ENGINE_ACTIVE",
                "engine": "Tri-Axial Empirical Multi-Model Synthesizer",
                "key_preview": gemini_key[:8] + "..." + gemini_key[-4:] if len(gemini_key) > 12 else "NONE"
            }

        return jsonify({
            "success": True,
            "parsed_profile": parsed,
            "skill_investment_card": card_result,
            "model_predictions": joblib_preds,
            "ai_critique": ai_critique,
            "ai_provider": ai_provider,
            "gemini_details": gemini_details
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/skill-card", methods=["POST"])
def api_skill_card():
    """
    Direct endpoint for numeric scores to generate Skill Investment Card.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        scores = data.get("scores", {
            "big_data": 3.2,
            "maths_stats": 3.0,
            "core_coding": 4.6,
            "ai_ml": 4.2,
            "dashboards": 3.0
        })
        exp_yrs = float(data.get("experience_yrs", 1.0))
        role = data.get("target_role", "Data Analyst/Analytics")
        city = data.get("primary_city", "Bengaluru")

        card_result = generate_skill_investment_card(scores, exp_yrs, role, city)
        return jsonify({"success": True, "card": card_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai-analytic", methods=["POST"])
def api_ai_analytic():
    """
    Calls Google Gemini or local analytical synthesizer to generate custom predictive advice.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        resume_text = data.get("resume_text", "")
        gemini_key = data.get("gemini_api_key") or data.get("api_key") or DEFAULT_GEMINI_KEY

        parsed = parse_resume(resume_text) if resume_text else {
            "scores": data.get("scores", {}),
            "experience_yrs": float(data.get("experience_yrs", 1.0)),
            "target_role": data.get("target_role", "Data Analyst/Analytics"),
            "primary_city": data.get("primary_city", "Bengaluru")
        }
        card_result = generate_skill_investment_card(
            parsed["scores"],
            parsed.get("experience_yrs", 1.0),
            parsed.get("target_role", "Data Analyst/Analytics")
        )

        gemini_prompt = build_gemini_prompt(parsed, card_result)
        gemini_result = call_gemini_api(gemini_prompt, api_key=gemini_key)

        if gemini_result["success"]:
            ai_critique = gemini_result["text"]
            ai_provider = gemini_result["provider"]
        else:
            ai_critique = run_ai_analytic_critique(parsed, card_result)
            ai_provider = "Tri-Axial Empirical AI Engine (Local Grounded)"

        return jsonify({
            "success": True,
            "ai_critique": ai_critique,
            "ai_provider": ai_provider,
            "card_status": card_result["card_decision"]["status"],
            "recommended_skill": card_result["card_decision"].get("recommended_skill")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# 3. RUN SERVER
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
    print("=" * 70)
    print(f"  STARTING AAVISHKAR HACKS ENTERPRISE SERVER ON PORT {port}")
    print(f"  Live at http://localhost:{port}/index.html")
    print("=" * 70)
    app.run(host="0.0.0.0", port=port, debug=False)
