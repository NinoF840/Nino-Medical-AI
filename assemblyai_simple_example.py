"""
Simple AssemblyAI Usage Example
Just the basics - how to transcribe audio files with AssemblyAI
"""
import assemblyai as aai

# Set your API key
aai.settings.api_key = "987de64ccb5a4c098d90d42e50de8731"

def simple_transcription(audio_file):
    """Basic transcription example"""
    print(f"Transcribing: {audio_file}")
    
    # Create transcriber
    transcriber = aai.Transcriber()
    
    # Transcribe (simple version)
    transcript = transcriber.transcribe(audio_file)
    
    print(f"Status: {transcript.status}")
    if transcript.status == "completed":
        print(f"Text: {transcript.text}")
    else:
        print(f"Error: {transcript.error}")

def italian_transcription(audio_file):
    """Italian transcription with configuration"""
    print(f"Transcribing Italian audio: {audio_file}")
    
    # Create transcriber
    transcriber = aai.Transcriber()
    
    # Configure for Italian
    config = aai.TranscriptionConfig(
        language_code="it",
        punctuate=True,
        format_text=True
    )
    
    # Transcribe
    transcript = transcriber.transcribe(audio_file, config=config)
    
    print(f"Status: {transcript.status}")
    if transcript.status == "completed":
        print(f"Italian Text: {transcript.text}")
    else:
        print(f"Error: {transcript.error}")

def transcription_with_speakers(audio_file):
    """Transcription with speaker identification"""
    print(f"Transcribing with speaker separation: {audio_file}")
    
    transcriber = aai.Transcriber()
    
    config = aai.TranscriptionConfig(
        language_code="it",
        speaker_labels=True
    )
    
    transcript = transcriber.transcribe(audio_file, config=config)
    
    if transcript.status == "completed":
        print("Full text:", transcript.text)
        
        # Print by speaker
        if hasattr(transcript, 'utterances'):
            print("\nBy speaker:")
            for utterance in transcript.utterances:
                print(f"Speaker {utterance.speaker}: {utterance.text}")

# Example usage:
if __name__ == "__main__":
    print("📱 AssemblyAI Examples")
    print("=" * 30)
    
    # Replace with your actual audio file paths:
    # simple_transcription("my_audio.wav")
    # italian_transcription("italian_speech.mp3")  
    # transcription_with_speakers("conversation.wav")
    
    print("💡 To use these examples:")
    print("1. Replace the file paths with your actual audio files")
    print("2. Uncomment the function calls above")
    print("3. Run this script")
    print("\n🎵 Supported formats: .wav, .mp3, .mp4, .m4a, .flac, .aac")
