from flask import Flask,render_template,request,jsonify,send_from_directory
from policyai.core import answer,DATA
app=Flask(__name__)
@app.get('/')
def home():return render_template('index.html')
@app.get('/health')
def health():return jsonify(status='ok')
@app.post('/chat')
def chat():
    data=request.get_json(silent=True) or {}
    body,status=answer(data.get('question'))
    return jsonify(body),status
@app.get('/sources/<path:filename>')
def source(filename):return send_from_directory(DATA,filename,as_attachment=False)
if __name__=='__main__':app.run(debug=True)
