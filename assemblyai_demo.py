"""
Simple AssemblyAI Standalone Demo
A straightforward example of using AssemblyAI for speech-to-text transcription
"""
import assemblyai as aai
import os


class SimpleAssemblyAI:
    """Simple AssemblyAI wrapper for transcription"""
    
    def __init__(self, api_key: str):
        """Initialize with your AssemblyAI API key"""
        self.api_key = api_key
        aai.settings.api_key = api_key
        print(f"✅ AssemblyAI initialized with API key")
    
    def transcribe_audio(self, audio_file_path: str, language: str = "it"):
        """
        Transcribe an audio file
        
        Args:
            audio_file_path: Path to audio file (wav, mp3, mp4, m4a, flac, aac)
            language: Language code (it=Italian, en=English, etc.)
        """
        print(f"🎙️  Starting transcription of: {audio_file_path}")
        print(f"🌍 Language: {language}")
        
        # Check if file exists
        if not os.path.exists(audio_file_path):
            print(f"❌ Error: Audio file not found: {audio_file_path}")
            return None
        
        try:
            # Create transcriber
            transcriber = aai.Transcriber()
            
            # Configure transcription
            config = aai.TranscriptionConfig(
                language_code=language,
                punctuate=True,
                format_text=True
            )
            
            print("⏳ Transcribing... (this may take a moment)")
            
            # Perform transcription
            transcript = transcriber.transcribe(audio_file_path, config=config)
            
            # Check result
            if transcript.status == "completed":
                print("✅ Transcription completed successfully!")
                return {
                    'text': transcript.text,
                    'status': transcript.status,
                    'id': transcript.id
                }
            else:
                print(f"❌ Transcription failed with status: {transcript.status}")
                if hasattr(transcript, 'error'):
                    print(f"Error details: {transcript.error}")
                return None
                
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return None
    
    def transcribe_with_speakers(self, audio_file_path: str, language: str = "it"):
        """
        Transcribe audio with speaker identification
        """
        print(f"🎙️  Starting transcription with speaker separation: {audio_file_path}")
        
        if not os.path.exists(audio_file_path):
            print(f"❌ Error: Audio file not found: {audio_file_path}")
            return None
        
        try:
            transcriber = aai.Transcriber()
            
            config = aai.TranscriptionConfig(
                language_code=language,
                punctuate=True,
                format_text=True,
                speaker_labels=True  # Enable speaker identification
            )
            
            print("⏳ Transcribing with speaker separation...")
            
            transcript = transcriber.transcribe(audio_file_path, config=config)
            
            if transcript.status == "completed":
                print("✅ Transcription with speakers completed!")
                
                result = {
                    'text': transcript.text,
                    'status': transcript.status,
                    'id': transcript.id,
                    'speakers': []
                }
                
                # Extract speaker information if available
                if hasattr(transcript, 'utterances') and transcript.utterances:
                    for utterance in transcript.utterances:
                        result['speakers'].append({
                            'speaker': utterance.speaker,
                            'text': utterance.text,
                            'start': utterance.start,
                            'end': utterance.end
                        })
                
                return result
            else:
                print(f"❌ Transcription failed: {transcript.status}")
                return None
                
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return None
    
    def print_transcript(self, result: dict):
        """Print transcription results in a nice format"""
        if not result:
            print("❌ No transcript to display")
            return
        
        print("\n" + "="*60)
        print("📄 TRANSCRIPTION RESULTS")
        print("="*60)
        
        print(f"📊 Status: {result['status']}")
        print(f"🆔 ID: {result['id']}")
        
        print(f"\n📝 Full Text:")
        print("-" * 40)
        print(result['text'])
        
        # If speakers are available, show them separately
        if 'speakers' in result and result['speakers']:
            print(f"\n👥 By Speaker:")
            print("-" * 40)
            for i, speaker_segment in enumerate(result['speakers']):
                speaker = speaker_segment['speaker']
                text = speaker_segment['text']
                start = speaker_segment.get('start', 0)
                end = speaker_segment.get('end', 0)
                
                print(f"Speaker {speaker} ({start/1000:.1f}s - {end/1000:.1f}s): {text}")
        
        print("="*60)
    
    def check_supported_formats(self):
        """Show supported audio formats"""
        formats = ['.wav', '.mp3', '.mp4', '.m4a', '.flac', '.aac']
        print("🎵 Supported audio formats:")
        for fmt in formats:
            print(f"   • {fmt}")
        return formats


def demo():
    """Demo function showing how to use AssemblyAI"""
    print("🚀 AssemblyAI Standalone Demo")
    print("="*50)
    
    # Your API key
    api_key = "987de64ccb5a4c098d90d42e50de8731"
    
    # Initialize AssemblyAI
    assemblyai = SimpleAssemblyAI(api_key)
    
    # Show supported formats
    assemblyai.check_supported_formats()
    
    # Example usage (you would replace with actual audio file paths)
    print(f"\n📋 Example Usage:")
    print(f"# For basic transcription:")
    print(f"result = assemblyai.transcribe_audio('path/to/your/audio.wav')")
    print(f"assemblyai.print_transcript(result)")
    
    print(f"\n# For transcription with speaker identification:")
    print(f"result = assemblyai.transcribe_with_speakers('path/to/conversation.mp3')")
    print(f"assemblyai.print_transcript(result)")
    
    print(f"\n# Supported languages:")
    print(f"# Italian: 'it', English: 'en', Spanish: 'es', French: 'fr', etc.")
    
    print(f"\n⚠️  Note: To test with real audio, replace the file paths above")
    print(f"   with actual audio files and uncomment the function calls.")


def test_with_real_file(file_path: str):
    """
    Test function for real audio files
    Uncomment and modify to test with your audio files
    """
    api_key = "987de64ccb5a4c098d90d42e50de8731"
    assemblyai = SimpleAssemblyAI(api_key)
    
    print(f"\n🧪 Testing with real file: {file_path}")
    
    # Basic transcription
    result = assemblyai.transcribe_audio(file_path, language="it")
    if result:
        assemblyai.print_transcript(result)
    
    # Transcription with speakers (if it's a conversation)
    print(f"\n👥 Testing with speaker separation...")
    speaker_result = assemblyai.transcribe_with_speakers(file_path, language="it")
    if speaker_result:
        assemblyai.print_transcript(speaker_result)


if __name__ == "__main__":
    demo()
    
    # Uncomment and provide a real audio file path to test:
    # test_with_real_file("path/to/your/audio/file.wav")
