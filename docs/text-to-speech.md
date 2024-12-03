# `/text-to-speech` API Documentation

## Overview
The `/text-to-speech` endpoint converts text into speech using a specified voice and language. It supports dynamic voice selection and multi-language input, and can asynchronously notify a webhook with the resulting audio URL upon completion.

## Endpoint
- **URL**: `/text-to-speech`
- **Method**: `POST`

---

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **text** (string, required): The text to be converted into speech. Must be at least 1 character long.
- **voice_url** (string, required): URL of the audio file specifying the voice to be used for the speech synthesis.
- **language** (string, required): ISO code for the language of the text (e.g., `"pt"` for Portuguese, `"en"` for English, etc).
- **webhook_url** (string, optional): URL to receive the resulting audio URL or an error message upon job completion.
- **id** (string, optional): Unique identifier for tracking the job.

---

### Example Request
#### Request Body:
```json
{
  "text": "Hello world!",
  "voice_url": "https://example.com/voice.wav",
  "language": "pt",
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "tts123"
}
```

#### Example Using `curl`:
```bash
curl -X POST "https://your-api-domain.com/text-to-speech" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "text": "Hello world!",
      "voice_url": "https://example.com/voice.wav",
      "language": "pt",
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "tts123"
    }'
```

---

## Response

### Success Response (200 OK)
If the TTS generation is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "tts123",
      "audio_url": "https://cloud-storage-url.com/generated_audio.wav",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "tts123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid parameters (`text`, `voice_url`, `language`).
  ```json
  {
    "error": "Missing required text, voice_url or language"
  }
  ```
- **500 Internal Server Error**: TTS generation process failed.
  ```json
  {
    "error": "Error during text-to-speech synthesis"
  }
  ```

---

## Webhook Notifications
If `webhook_url` is provided in the request, the API posts the result or an error message to the specified URL upon job completion.

### Webhook Payload:
#### Success Payload:
```json
{
  "id": "tts123",
  "status": "completed",
  "result": "https://cloud-storage-url.com/generated_audio.wav"
}
```

#### Failure Payload:
```json
{
  "id": "tts123",
  "status": "failed",
  "error": "Error during text-to-speech synthesis"
}
```

---

## Error Handling
- **400 Bad Request**: Returned if any required parameters are missing or malformed.
- **500 Internal Server Error**: Returned if there’s an issue during speech generation.

---

## Usage Notes
1. **Dynamic Voice Support**:
   - Provide a valid `voice_url` pointing to a speaker WAV file for personalized speech synthesis.
2. **Multi-Language Support**:
   - Ensure the `language` parameter matches the input text's language for optimal results.
3. **Webhook for Async Processing**:
   - Use `webhook_url` to receive results for large text inputs asynchronously.

---

## Common Issues
1. **Invalid Voice URL**:
   - Ensure the `voice_url` is accessible and points directly to a WAV file.
2. **Unsupported Language**:
   - Check that the provided `language` is supported by the TTS model.
3. **Webhook URL Errors**:
   - Verify that the `webhook_url` accepts POST requests with JSON payloads.

---

## Best Practices
- **Use Webhooks for Long Inputs**: For lengthy text inputs, use `webhook_url` to handle asynchronous job completion efficiently.
- **Format Input Text**: Split long texts into natural sentences for clearer and more natural speech.
- **Optimize Voice Selection**: Use high-quality voice files to ensure realistic and expressive speech synthesis.