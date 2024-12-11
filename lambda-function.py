import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable, NoTranscriptFound

def lambda_handler(event, context):
    """
    Lambda function to extract YouTube transcript using youtube-transcript-api.
    Event Format: { "video_id": "YourYouTubeVideoID" }
    """
    try:
        # Extract the video ID from the event
        video_id = event.get("video_id")
        if not video_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'video_id' in request"})
            }
        
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"transcript": transcript})
        }
    except TranscriptsDisabled:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "Transcripts are disabled for this video."})
        }
    except VideoUnavailable:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Video not found or unavailable."})
        }
    except NoTranscriptFound:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No transcript found for this video."})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
