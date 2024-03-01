from flask import Flask, request, redirect, render_template, session, url_for
from flask_wtf import CSRFProtect
import requests
import uuid
import json
import os

app = Flask(__name__, static_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Change this key for secure deployment

csrf = CSRFProtect(app)

# Following config necessary for iFrame (For ex, HuggingFace App)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "None"

SESSION_DICT = {}

def delete_session(key):
    if key in session:
        if session[key] in SESSION_DICT:
            del SESSION_DICT[session[key]]
        session.pop(key, None)

def add_to_session(key, value):
    delete_session(key)
    uid = uuid.uuid4()
    SESSION_DICT[uid] = value
    session[key] = uid

def get_session_data(key):
    if key not in session or session[key] not in SESSION_DICT:
        return None
    return SESSION_DICT[session[key]]

def send_rapidapi(url, payload):
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.environ.get("API_KEY")
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def id_recognition(id_payload):
    url = 'https://id-document-recognition2.p.rapidapi.com/api/iddoc_base64'
    resp = send_rapidapi(url, id_payload)
    return resp

def face_liveness(face_payload):
    url = 'https://face-liveness-detection3.p.rapidapi.com/api/liveness_base64'
    resp = send_rapidapi(url, face_payload)
    return resp

def face_recognition(face_payload):
    url = 'https://face-recognition26.p.rapidapi.com/api/face_compare_base64'
    resp = send_rapidapi(url, face_payload)
    return resp

@app.route("/", methods=['GET'])
def index():
    return render_template('intro.html')

@app.route("/id_type/", methods=['GET'])
def id_type():
    delete_session('id_type')
    delete_session('id_file')
    delete_session('id_res')
    delete_session('fr_selfie')
    delete_session('liveness_res')
    return render_template('id_type.html')

@app.route("/id_type/", methods=['POST'])
def id_type_done():
    add_to_session('id_type', request.values['ocr_type'])
    return redirect(url_for('id_file'))

@app.route("/id_file/", methods=['GET'])
def id_file():
    id_type = get_session_data('id_type')
    if id_type is None:
        return redirect(url_for('id_type'))
    
    if request.headers.get("Referer").endswith("/id_detail"):
        delete_session('id_file')

    id_file = get_session_data('id_file')      

    if id_type == 'ic':
        if id_file is not None and id_file['image2'] == "":
            return render_template('id_file.html', id_type = 'ic_back', error_model = False)
        else:
            return render_template('id_file.html', id_type = 'ic_front', error_model = False)
    else:
        return render_template('id_file.html', id_type = 'passport', error_model = False)    

@app.route("/id_file/", methods=['POST'])
def id_file_done():
    id_type = get_session_data('id_type')
    id_file = get_session_data('id_file')
    id_base64 = request.values['ocr_file']

    if id_type == 'ic':
        if id_file is not None and id_file['image2'] == "":
            id_file['image2'] = id_base64
            add_to_session('id_file', id_file)
        else:
            add_to_session('id_file', {
                "image": id_base64,
                "image2": ""
            })
            return render_template('id_file.html', id_type = 'ic_back', error_model = False)
    else:
        id_file = {
            "image": id_base64,
            "image2": ""
        }
        add_to_session('id_file', id_file)

    res = id_recognition(id_file)
    if not ('data' in res and 'ocr' in res['data'] and 'name' in res['data']['ocr'] and 'data' in res and 'image' in res['data'] and 'portrait' in res['data']['image'] and 'documentFrontSide' in res['data']['image']):
        delete_session('id_file')
        if id_type == 'ic':
            return render_template('id_file.html', id_type = 'ic_front', error_model = True)
        else:
            return render_template('id_file.html', id_type = 'passport', error_model = True)

    add_to_session('id_res', res)
    return redirect(url_for('id_detail'))

@app.route("/id_detail/", methods=['GET'])
def id_detail():
    sess_id_res = get_session_data('id_res')
    if sess_id_res is not None:       
        return render_template('id_detail.html', ocr_result = json.dumps(sess_id_res))
    else:
        return redirect(url_for('id_type'))

@app.route("/id_detail/", methods=['POST'])
def id_detail_done():
    return redirect(url_for('fr_file'))

@app.route("/fr_file/", methods=['GET'])
def fr_file():
    delete_session('fr_selfie')
    delete_session('liveness_res')
    return render_template('fr_file.html', error_model = False)

@app.route("/fr_file/", methods=['POST'])
def fr_file_done():
    fr_base64 = request.values['fr_file']
    add_to_session('fr_selfie', fr_base64)

    liveness_api_resp = face_liveness({
    "image": fr_base64
    })

    print("Liveness Result:", liveness_api_resp) 

    if 'data' in liveness_api_resp and 'result' in liveness_api_resp['data']:
        liveness_res = liveness_api_resp['data']['result']        
        if liveness_res not in ["genuine", "spoof"]:
            return render_template('fr_file.html', error_model = True)
    
        add_to_session('liveness_res', liveness_res)
    else:
        return render_template('fr_file.html', error_model = True)

    return redirect(url_for('fr_detail'))

@app.route("/fr_detail/", methods=['GET'])
def fr_detail():
    sess_id_res = get_session_data('id_res')
    if sess_id_res is None:
        return redirect(url_for('id_type'))
    
    sess_fr_selfie = get_session_data('fr_selfie')
    if sess_fr_selfie is not None:

        liveness_res = get_session_data('liveness_res')
        
        sess_id_face = sess_id_res['data']['image']['portrait']
        if sess_id_face is not None:
            payload = {
                "image1": sess_id_face,
                "image2": sess_fr_selfie
            }
            recog_api_resp = face_recognition(payload)

            if 'data' in recog_api_resp and 'result' in recog_api_resp['data']:
                recog_res = recog_api_resp['data']['result']
                recog_similarity = recog_api_resp['data']['similarity']
                recog_api_resp['data']['liveness'] = liveness_res

            print("Matching Result", recog_api_resp)
        return render_template('fr_detail.html', 
                               id_name = sess_id_res['data']['ocr']['name'], 
                               id_liveness = sess_id_res['authenticity_liveness'].upper(), 
                               id_forge = sess_id_res['authenticity_meta'].upper(), 
                               id_front = 'data:image/png;base64,' + sess_id_res['data']['image']['documentFrontSide'], 
                               id_face = 'data:image/png;base64,' + sess_id_face, 
                               selfie = 'data:image/png;base64,' + sess_fr_selfie, 
                               liveness_res = liveness_res.upper(), 
                               recog_res = recog_res.upper(), 
                               recog_similarity = recog_similarity * 100, 
                               ocr_result = json.dumps(sess_id_res), 
                               fr_result = json.dumps(recog_api_resp))
    else:
        return redirect(url_for('fr_file'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)