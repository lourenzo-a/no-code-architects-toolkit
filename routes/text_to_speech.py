from flask import Blueprint
from app_utils import *
import logging
import os
from services.text_to_speech import synthesize
from services.authentication import authenticate
from services.cloud_storage import upload_file
from services.file_management import download_file


text_to_speech_bp = Blueprint('text_to_speech', __name__)
logger = logging.getLogger(__name__)

@text_to_speech_bp.route('/text-to-speech', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "text": {"type": "string", "minLength": 1},
        "voice_url": {"type": "string", "format": "uri"},
        "language": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["text", "voice_url", "language"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def text_to_speech(job_id, data):
    text = data.get('text')
    voice_url = data.get('voice_url')
    language = data.get('language')
    webhook_url = data.get('webhook_url')  # Optional webhook URL
    id = data.get('id') # Optional identifier for tracking the job

    logger.info(f"Job {job_id}: Received text-to-speech request for text: {text}")

    try:
        # Download the voice file from the provided URL
        voice_path = download_file(voice_url, "/tmp/")

        # Generate the speech audio file
        output_filename = synthesize(
            text=text,
            voice_path=voice_path,
            language=language,
            job_id=job_id
        )

        # Upload the generated audio file to cloud storage
        cloud_url = upload_file(output_filename)

        logger.info(f"Job {job_id}: Speech audio uploaded to cloud storage: {cloud_url}")

        # Return the cloud URL for the uploaded file
        return cloud_url, "/text-to-speech", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during text-to-speech process - {str(e)}")
        return str(e), "/text-to-speech", 500
