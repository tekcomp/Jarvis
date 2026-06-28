# Voice Conversation Implementation Plan

## Core Components to Enable
1. **Audio Pipeline** (`audio_stream.py`, `audio/frontend.py`)
   - [ ] Add device selection UI
   - [ ] Implement audio stream buffering
   - [ ] Configure sample rate/channels

2. **Speech Recognition** (`stt_stream.py`, `stt/vad.py`)
   - [ ] Configure silence detection thresholds
   - [ ] Add wake word confirmation
   - [ ] Implement continuous listening

3. **Conversation Management** (`core/brain_v3.py`, `state.py`)
   - [ ] Add conversation history tracking
   - [ ] Implement context preservation
   - [ ] Create dialog state machine

4. **Response Generation** (`llm/ollama.py`, `core/personality_engine_v2.py`)
   - [ ] Connect LLM to conversation loop
   - [ ] Add personality configuration
   - [ ] Implement response filtering

5. **Speech Synthesis** (`tts/voice.py`, `tts/voice_async.py`)
   - [ ] Configure voice parameters
   - [ ] Add interrupt handling
   - [ ] Implement streaming output

## Implementation Sequence
1. **Phase 1: Core Conversation Loop** (`jarvis.py`)
   - Add main while loop with states:
     - WAKE_DETECTION
     - USER_INPUT
     - PROCESSING
     - RESPONSE
   - Connect audio buffer to STT
   - Connect LLM to TTS

2. **Phase 2: State Management** (`state.py`)
   - Extend with:
     ```python
     class ConversationState:
         history: list  # [(user, jarvis), ...]
         context: str   # "current topic"
         status: Enum  # LISTENING, PROCESSING, SPEAKING
     ```

3. **Phase 3: Personality Configuration** (`config/jarvis_config.json`)
   - Add voice section:
     ```json
     "voice": {
         "speech_rate": 1.0,
         "voice_name": "en-US-JennyNeural",
         "style": "friendly"
     }
     ```

4. **Phase 4: Advanced Features**
   - Continuous conversation
   - Voice interrupt during responses
   - Multi-turn dialog handling

## Testing Procedure
1. Unit tests for audio pipeline (`tests/test_wake_stream.py`)
2. Integration test for full conversation (`tests/test_brain.py`)
3. Performance test with various audio devices
4. User acceptance testing with voice commands

## Dependencies
- PyAudio 0.2.14 (`pip install pyaudio`)
- FasterWhisper 0.10.0 (`pip install faster-whisper`)
- SoundDevice 0.4.6 (`pip install sounddevice`)