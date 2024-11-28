from flask import Flask, render_template, request, jsonify
import analyze_top_10_words  # 분석 모듈을 가져옵니다.

app = Flask(__name__)

@app.route('/')
def index():
    # index.html 템플릿을 렌더링합니다.
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # 클라이언트로부터 데이터 받기
    data = request.json
    aspect_keyword = data.get('aspect')
    selected_files = data.get('files')
    
    # analyze_top_10_words 모듈을 사용하여 분석 수행
    response = analyze_top_10_words.perform_analysis(aspect_keyword, selected_files)
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
