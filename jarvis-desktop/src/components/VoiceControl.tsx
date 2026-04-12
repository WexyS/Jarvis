import { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface VoiceControlProps {
  onVoiceInput?: (text: string) => void;
  onTTS?: (text: string) => void;
  isListening: boolean;
  isSpeaking: boolean;
  disabled?: boolean;
}

export default function VoiceControl({
  onVoiceInput,
  onTTS,
  isListening,
  isSpeaking,
  disabled = false,
}: VoiceControlProps) {
  const [recognition, setRecognition] = useState<any>(null);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'tr-TR'; // Turkish language support

        recognitionInstance.onresult = (event: any) => {
          let finalTranscript = '';
          let interimTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }

          setTranscript(interimTranscript || finalTranscript);

          if (finalTranscript && onVoiceInput) {
            onVoiceInput(finalTranscript);
          }
        };

        recognitionInstance.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setError(`Error: ${event.error}`);
        };

        recognitionInstance.onend = () => {
          setTranscript('');
        };

        setRecognition(recognitionInstance);
      } else {
        setError('Speech recognition not supported in this browser');
      }
    }
  }, [onVoiceInput]);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (!recognition || disabled) return;

    if (isListening) {
      recognition.stop();
    } else {
      setError(null);
      recognition.start();
    }
  }, [recognition, isListening, disabled]);

  // Toggle TTS
  const toggleSpeaking = useCallback(() => {
    if (disabled) return;

    if (isSpeaking) {
      if (onTTS) {
        onTTS(''); // Stop speaking
      }
      window.speechSynthesis.cancel();
    } else {
      // Test TTS
      const utterance = new SpeechSynthesisUtterance('Jarvis activated');
      utterance.lang = 'tr-TR';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  }, [isSpeaking, disabled, onTTS]);

  return (
    <div className="flex items-center gap-2">
      {/* Voice Input Button */}
      <motion.button
        whileHover={{ scale: disabled ? 1 : 1.05 }}
        whileTap={{ scale: disabled ? 1 : 0.95 }}
        onClick={toggleListening}
        disabled={disabled}
        className={`
          relative p-2.5 rounded-full transition-all duration-200
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-jarvis-card'}
          ${isListening ? 'bg-jarvis-accent/20 ring-2 ring-jarvis-accent animate-pulse' : ''}
        `}
        title={isListening ? 'Stop listening' : 'Start listening'}
      >
        <AnimatePresence mode="wait">
          {isListening ? (
            <motion.div
              key="listening"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
            >
              <Mic className="w-5 h-5 text-jarvis-accent" />
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
            >
              <MicOff className="w-5 h-5 text-jarvis-textMuted" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Listening indicator */}
        {isListening && (
          <motion.div
            className="absolute -top-1 -right-1 w-3 h3 bg-jarvis-accent rounded-full"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
      </motion.button>

      {/* Voice Output (TTS) Button */}
      <motion.button
        whileHover={{ scale: disabled ? 1 : 1.05 }}
        whileTap={{ scale: disabled ? 1 : 0.95 }}
        onClick={toggleSpeaking}
        disabled={disabled}
        className={`
          p-2.5 rounded-full transition-all duration-200
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-jarvis-card'}
          ${isSpeaking ? 'bg-jarvis-accent/20 ring-2 ring-jarvis-accent animate-pulse' : ''}
        `}
        title={isSpeaking ? 'Stop speaking' : 'Enable voice response'}
      >
        <AnimatePresence mode="wait">
          {isSpeaking ? (
            <motion.div
              key="speaking"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
            >
              <Volume2 className="w-5 h-5 text-jarvis-accent" />
            </motion.div>
          ) : (
            <motion.div
              key="silent"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
            >
              <VolumeX className="w-5 h-5 text-jarvis-textMuted" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Transcript display */}
      <AnimatePresence>
        {transcript && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            className="px-3 py-1.5 text-xs rounded-md bg-jarvis-card border border-jarvis-border max-w-xs truncate"
          >
            <span className="text-jarvis-textMuted">🎤</span> {transcript}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="px-3 py-1.5 text-xs rounded-md bg-jarvis-danger/10 border border-jarvis-danger/30 text-jarvis-danger"
          >
            ⚠️ {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading indicator */}
      {(isListening || isSpeaking) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-1 text-xs text-jarvis-textMuted"
        >
          <Loader2 className="w-3 h-3 animate-spin" />
          <span>{isListening ? 'Listening...' : 'Speaking...'}</span>
        </motion.div>
      )}
    </div>
  );
}
