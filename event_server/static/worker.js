import { pipeline } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.6.0';

let transcriber = null;

self.onmessage = async (e) => {
    const { type, audioData, qIndex } = e.data;

    if (type === 'init') {
        try {
            transcriber = await pipeline('automatic-speech-recognition', 'Xenova/whisper-base.en');
            self.postMessage({ type: 'init_complete', success: true });
        } catch (err) {
            self.postMessage({ type: 'init_complete', success: false, error: err.message });
        }
    }

    if (type === 'transcribe') {
        try {
            const result = await transcriber(audioData);
            self.postMessage({ type: 'transcribe_complete', text: result.text, qIndex });
        } catch (err) {
            self.postMessage({ type: 'transcribe_complete', error: err.message, qIndex });
        }
    }
};
