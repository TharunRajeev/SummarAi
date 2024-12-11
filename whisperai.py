import json
import os
import openai
import whisper
import subprocess
from pytube import YouTube
from config import API_KEY

def download_audio(video_id, output_path="/tmp/audio.mp3"):
    """
    Download the audio from a YouTube video using yt-dlp.
    """
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        command = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_path,
            youtube_url
        ]
        subprocess.run(command, check=True)
        print(f"Audio downloaded to {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error downloading audio: {e}")
        return None

def transcribe_audio(file_path):
    """
    Transcribe the audio file using Whisper AI.
    """
    try:
        model = whisper.load_model("base")  # Use "small", "medium", or "large" for more accuracy.
        print("Transcribing audio...")
        result = model.transcribe(file_path)
        return result.get("text", "")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def lambda_handler(event, context):
    try:
        openai.api_key = API_KEY
    except KeyError:
        return {
            'statusCode': 500,
            'body': 'OpenAI API key not found.'
        }

    if 'queryStringParameters' not in event or 'video_id' not in event['queryStringParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Video Id not found in query string parameter'})
        }
    
    video_id = event['queryStringParameters']['video_id']

    try:
        # Step 1: Download audio from YouTube video
        audio_file = download_audio(video_id)
        if not audio_file:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unable to download audio from the video'})
            }

        # Step 2: Transcribe the audio using Whisper AI
        transcript = transcribe_audio(audio_file)
        if not transcript:
            os.remove(audio_file)  # Cleanup in case of failure
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unable to transcribe audio'})
            }

        # Step 3: Use OpenAI to summarize the transcript
        prompt = (
            "Summarize the following transcript. Output the summary in bullet points, and be detailed.\n\n"
            f"Transcript:\n{transcript}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for summarizing transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=512,
        )

        summary = response['choices'][0]['message']['content']

        # Step 4: Cleanup the temporary audio file
        os.remove(audio_file)

        return {
            'statusCode': 200,
            'body': json.dumps({'summary': summary})
        }

    except Exception as e:
        print(f"Error: {e}")
        if os.path.exists(audio_file):
            os.remove(audio_file)  # Ensure cleanup on error
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An error occurred while processing the video.'})
        }


if __name__ == "__main__":
    event = {
        "queryStringParameters": {
            "video_id": "1aA1WGON49E&t=8s"  # Replace with a valid YouTube video ID
        }
    }
    context = None  # Not needed for local testing

    # Call the handler directly
    response = lambda_handler(event, context)
    print(json.dumps(response, indent=4))
