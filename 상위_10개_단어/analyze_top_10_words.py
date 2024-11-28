from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib import font_manager, rc
import os
import base64
from io import BytesIO

app = Flask(__name__)

# 한글 폰트 설정
font_path = "C:/Windows/Fonts/malgun.ttf"  # 윈도우의 경우
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

# 불용어 로드 및 추가 정의
with open(r"\Users\kyn03\OneDrive\바탕 화면\project_file\상위_10개_단어\stopwords-ko(한국어불용어).txt", encoding='utf-8') as f:
    stopwords = f.read().splitlines()

stopwords += ['좀', '것', '달바', '미스트', '스프레이', '1으로', '1이라', '1에', '너무', '느낌', '잘', '그냥', '많이', '있어서', '같아요', '스프레이가', '미스트가', '미스트는', '약간의',
              '생각보다', '있으며', '살짝', '같아서', '느낌이', '저는', '진짜', '엄청', '합니다', '더', '안', '느낌은', '효과는', '조금', '분들은', '크림미스트라서',
              '크림미스트라', '미스트라', '미스트라서', '그런지', '못', '이거', '완전', '아벤느', '다', '거', '수', '줄']

# 긍정/부정 단어 전처리 함수 정의
def preprocess_text(text_list):
    cleaned_text = ' '.join([re.sub(r"[^가-힣0-9\+\s]", "", text) for text in text_list])
    return cleaned_text

# 데이터 로드
data_dalba = pd.read_excel(r"\Users\kyn03\OneDrive\바탕 화면\project_file\상위_10개_단어\sorted_merged_dalba.xlsx").reset_index()
data_boh = pd.read_excel(r"\Users\kyn03\OneDrive\바탕 화면\project_file\상위_10개_단어\sorted_merged_boh.xlsx").reset_index()
data_avene = pd.read_excel(r"\Users\kyn03\OneDrive\바탕 화면\project_file\상위_10개_단어\sorted_merged_avene.xlsx").reset_index()

datasets = {
    '달바': data_dalba,
    '바이오힐보': data_boh,
    '아벤느': data_avene
}

# 단어 빈도수 계산 함수 정의
def get_top_n_words(text, n=10):
    words = text.split()
    word_counts = Counter(words)
    return word_counts.most_common(n)

# 막대 차트 그리기 및 base64 인코딩 함수 정의
def plot_individual_words(word_freqs, title, labels, colors):
    fig, axes = plt.subplots(1, len(word_freqs), figsize=(20, 8))
    if len(word_freqs) == 1:
        axes = [axes]

    for ax, word_freq, label, color in zip(axes, word_freqs, labels, colors):
        if word_freq:
            words, counts = zip(*word_freq)
            ax.bar(words, counts, color=color)
            ax.set_title(label, fontsize=30)
            ax.set_xlabel('단어', fontsize=25)
            ax.set_ylabel('빈도수', fontsize=25)
            ax.tick_params(axis='x', rotation=45, labelsize=20)

    plt.suptitle(title)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # 이미지를 base64로 인코딩하여 HTML에 임베드 가능하게 만듭니다
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return image_base64

def perform_analysis(aspect_keyword, selected_files):
        all_positive_b_words = []
        all_negative_b_words = []
        all_positive_i_words = []
        all_negative_i_words = []
        labels_positive_b = []
        labels_negative_b = []
        labels_positive_i = []
        labels_negative_i = []

        for file_name in selected_files:
            data = datasets[file_name]
            filtered_data = data.iloc[[i for i in range(len(data)) if (i - 2) % 7 == 0]]

            if filtered_data.apply(lambda row: row.astype(str).str.contains(aspect_keyword, na=False).any(), axis=1).any():
                aspect_row_data = filtered_data[filtered_data.apply(lambda row: row.astype(str).str.contains(aspect_keyword, na=False).any(), axis=1)]

                # 긍정/부정 감정 및 토큰화된 텍스트 추출
                positive_b_words = []
                negative_b_words = []
                positive_i_words = []
                negative_i_words = []

                for idx, row in aspect_row_data.iterrows():
                    original_idx = data[data['index'] == row['index']].index[0]
                    sentiment_row_index = original_idx - 2
                    sentiment = data.iloc[sentiment_row_index]
                    tokenized_text_index = original_idx + 3

                    if tokenized_text_index < len(data):
                        for col in data.columns[1:]:
                            if aspect_keyword in str(data.at[original_idx, col]):
                                sentiment_value = data.at[sentiment_row_index, col]
                                tokenized_text = str(data.at[tokenized_text_index, col])
                                if pd.notna(sentiment_value) and pd.notna(tokenized_text):
                                    cleaned_text = preprocess_text([word for word in tokenized_text.split() if not word.startswith('#') and word not in stopwords])
                                    if cleaned_text.strip():
                                        if 'B-긍정' in sentiment_value:
                                            positive_b_words.append(cleaned_text)
                                        elif 'B-부정' in sentiment_value:
                                            negative_b_words.append(cleaned_text)
                                        elif 'I-긍정' in sentiment_value:
                                            positive_i_words.append(cleaned_text)
                                        elif 'I-부정' in sentiment_value:
                                            negative_i_words.append(cleaned_text)

                if positive_b_words:
                    all_positive_b_words.append(get_top_n_words(' '.join(positive_b_words)))
                    labels_positive_b.append(f'{file_name} - B-긍정')
                if negative_b_words:
                    all_negative_b_words.append(get_top_n_words(' '.join(negative_b_words)))
                    labels_negative_b.append(f'{file_name} - B-부정')
                if positive_i_words:
                    all_positive_i_words.append(get_top_n_words(' '.join(positive_i_words)))
                    labels_positive_i.append(f'{file_name} - I-긍정')
                if negative_i_words:
                    all_negative_i_words.append(get_top_n_words(' '.join(negative_i_words)))
                    labels_negative_i.append(f'{file_name} - I-부정')

        # 각 감정별 차트 생성
        response = {}
        if all_positive_b_words:
            response['positive_b_chart'] = plot_individual_words(all_positive_b_words, f"{aspect_keyword} - B-긍정 상위 10개 단어 (제품별 비교)", labels_positive_b, colors=['#4a90e2'] * len(all_positive_b_words))
        if all_negative_b_words:
            response['negative_b_chart'] = plot_individual_words(all_negative_b_words, f"{aspect_keyword} - B-부정 상위 10개 단어 (제품별 비교)", labels_negative_b, colors=['#f5a623'] * len(all_negative_b_words))
        if all_positive_i_words:
            response['positive_i_chart'] = plot_individual_words(all_positive_i_words, f"{aspect_keyword} - I-긍정 상위 10개 단어 (제품별 비교)", labels_positive_i, colors=['#76b7b2'] * len(all_positive_i_words))
        if all_negative_i_words:
            response['negative_i_chart'] = plot_individual_words(all_negative_i_words, f"{aspect_keyword} - I-부정 상위 10개 단어 (제품별 비교)", labels_negative_i, colors=['#e15759'] * len(all_negative_i_words))

        return response
