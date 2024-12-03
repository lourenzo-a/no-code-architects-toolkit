import os
import time
from pathlib import Path
from TTS.api import TTS
import html
import torch  # Ensure torch is imported for device handling
from pydub import AudioSegment  # For audio concatenation
import uuid  # For generating unique temporary filenames

# Define storage path for temporary files
STORAGE_PATH = "/tmp/"
os.environ["COQUI_TOS_AGREED"] = "1"

def preprocess(text):
    """
    Preprocesses the input text by unescaping HTML entities and handling trailing punctuation.
    """
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Remove only the last trailing dot, if present, but keep ellipses
    #if text.endswith('.') and not text.endswith('...'):
    #    text = text[:-1]  # Remove the last dot only
    
    return text

def preprocess_and_tokenize(text, tokenizer, framework="pt"):
    """
    Preprocess and tokenize the input text with a dynamic framework.

    Args:
        text (str): The input text to preprocess.
        tokenizer: The tokenizer to use.
        framework (str): The framework format ('pt' for PyTorch, 'tf' for TensorFlow, etc.).

    Returns:
        tuple: input_ids and attention_mask
    """
    input_ids = tokenizer.encode(text, return_tensors=framework, padding=True)
    attention_mask = (input_ids != tokenizer.pad_token_id).long() if framework == "pt" else None

    return input_ids, attention_mask

def split_into_sentences(text, remove_trailing_dots=False):
    """
    Splits the text into sentences and optionally removes trailing periods.

    Args:
        text (str): The input text to split into sentences.
        remove_trailing_dots (bool): Whether to remove trailing periods.

    Returns:
        list: A list of processed sentences.
    """
    # Use a simple sentence splitter (you can use NLP libraries for more robust handling)
    sentences = text.split('. ')  # Splits sentences by ". " (space after period)

    if remove_trailing_dots:
        sentences_without_dots = []
        for sentence in sentences:
            if sentence.endswith('.') and not sentence.endswith('...'):
                sentence = sentence[:-1]  # Remove the final period
            sentences_without_dots.append(sentence)
        return sentences_without_dots

    return sentences

def synthesize(text, voice_path, language, job_id, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
    """
    Synthesizes speech audio from text using the Coqui TTS library, concatenating multiple sentences.

    Args:
        text (str): The input text to be converted to speech.
        voice_path (str): Path to the voice file (speaker WAV).
        language (str): Language of the text.
        job_id (str): Unique job identifier.
        model_name (str): Model to be used for TTS.

    Returns:
        str: Path to the final concatenated audio file.
    """
    # Set up paths
    storage_path = Path(STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    final_output_file = storage_path / f"tts_output_{job_id}_{int(time.time())}.wav"

    # Load TTS model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = TTS(model_name).to(device)

    # Preprocess input text
    processed_text = preprocess(text)
    sentences = split_into_sentences(processed_text, remove_trailing_dots=True)

    try:
        # Generate temporary audio files for each sentence
        temp_files = []
        for sentence in sentences:
            temp_file = storage_path / f"{uuid.uuid4()}.wav"
            model.tts_to_file(
                text=sentence,
                file_path=str(temp_file),
                speaker_wav=[voice_path],
                language=language
            )
            temp_files.append(temp_file)

        # Concatenate all temporary audio files into the final output file
        combined_audio = AudioSegment.empty()
        for temp_file in temp_files:
            combined_audio += AudioSegment.from_file(temp_file)

        combined_audio.export(final_output_file, format="wav")

        # Clean up temporary files
        for temp_file in temp_files:
            temp_file.unlink()  # Delete the file

        return str(final_output_file)

    except Exception as e:
        raise RuntimeError(f"Error in TTS synthesis: {e}")
    finally:
        # Ensure the temporary voice file is removed
        if Path(voice_path).exists():
            os.remove(voice_path)
