from flask import Flask, jsonify, request
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, InvalidVideoId
from config import API_KEY
from flask_cors import CORS
#import boto3
#import json


app = Flask(__name__)
CORS(app)

# Create Lambda client
#lambda_client = boto3.client('lambda', region_name='your-region')

#response = lambda_client.invoke(
#    FunctionName="YOUTUBE_SUMMARIZER",
#    InvocationType="RequestResponse",
#    Payload=json.dumps({ "video_id": "w8rYQ40C9xo"})
#)

# Read the response
#response_payload = json.load(response['Payload'])

@app.route('/summary', methods=['GET'])
def youtube_summarizer():
    video_id = request.args.get('v')
    try:
        transcript = get_transcript(video_id)
        data = open_ai(transcript, True)
        # print(data.choices[0].message.content)
    except NoTranscriptFound:
        return jsonify({"data": "No English Subtitles found", "error": True})
    except InvalidVideoId:
        return jsonify({"data": "Invalid Video Id", "error": True})
    except Exception as e:
        print(e)
        return jsonify({"data": "Unable to Summarize the video", "error": True})

    return jsonify({"data": data.choices[0].message.content, "error": False})

@app.route('/summary/detailed', methods=['GET'])
def youtube_summarizer1():
    video_id = request.args.get('v')
    try:
        transcript = get_transcript(video_id)
        data = open_ai(transcript, False)
        # print(data.choices[0].message.content)
    except NoTranscriptFound:
        return jsonify({"data": "No English Subtitles found", "error": True})
    except InvalidVideoId:
        return jsonify({"data": "Invalid Video Id", "error": True})
    except Exception as e:
        print(e)
        return jsonify({"data": "Unable to Summarize the video", "error": True})

    return jsonify({"data": data.choices[0].message.content, "error": False})



def get_transcript(video_id):
    transcript_response = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_list = [item['text'] for item in transcript_response]
    return ' '.join(transcript_list)


def open_ai(transcript, isShort):
    client = OpenAI(api_key=API_KEY)
    if isShort:
        content = "You have to summarize a YouTube video using its transcript in 10 points"
    else:
        content = "You have to summarize a YouTube video using its transcript in detail with atleast 200 words"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system",
             "content": content},
            {"role": "user", "content": transcript}
        ]
    )
    return completion
