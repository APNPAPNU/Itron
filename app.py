from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
import whisper
import os
import uuid

app = Flask(__name__)
whisper_model = whisper.load_model("tiny")

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_text = None
    download_link = None

    if request.method == 'POST':
        video_url = request.form['video_url']
        filename = f"audio_{uuid.uuid4().hex}.mp4"
        txt_filename = f"transcription_{uuid.uuid4().hex}.txt"

        try:
            audio_file = YouTube(video_url).streams.filter(only_audio=True).first().download(filename=filename)
            transcription = whisper_model.transcribe(audio_file)
            transcript_text = transcription['text']

            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            download_link = txt_filename
            os.remove(filename)

        except Exception as e:
            transcript_text = f"Error: {str(e)}"

    return render_template('index.html', transcript=transcript_text, download_link=download_link)

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)