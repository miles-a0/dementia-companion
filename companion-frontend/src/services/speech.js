var globalRetryCount = {};
var globalMaxRetries = 3;

export function speak(text) {
  return new Promise(function(resolve, reject) {
    if (!window.speechSynthesis) {
      console.warn('Speech synthesis is not available');
      resolve();
      return;
    }

    var retryKey = 'speak_' + text;
    var retryCount = globalRetryCount[retryKey] || 0;

    window.speechSynthesis.cancel();

    var utterance = new window.SpeechSynthesisUtterance(text);
    utterance.rate = 0.85;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    var voices = window.speechSynthesis.getVoices();
    if (voices.length === 0 && retryCount < globalMaxRetries) {
      globalRetryCount[retryKey] = retryCount + 1;
      setTimeout(function() {
        speak(text).then(resolve).catch(reject);
      }, 100);
      return;
    }
    globalRetryCount[retryKey] = 0;

    var selectedVoice = null;
    var i = 0;
    while (i < voices.length) {
      var voice = voices[i];
      if (voice.lang && voice.lang.indexOf('en-GB') !== -1) {
        selectedVoice = voice;
        break;
      }
      i = i + 1;
    }
    if (!selectedVoice) {
      i = 0;
      while (i < voices.length) {
        var voice = voices[i];
        if (voice.lang && voice.lang.indexOf('en') !== -1) {
          selectedVoice = voice;
          break;
        }
        i = i + 1;
      }
    }
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onend = function() {
      resolve();
    };

    utterance.onerror = function(event) {
      reject(event.error);
    };

    window.speechSynthesis.speak(utterance);
  });
}

export function listen() {
  return new Promise(function(resolve, reject) {
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      reject('Speech recognition is not available on this device');
      return;
    }

    var recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-GB';
    recognition.maxAlternatives = 1;

    var timeoutId = setTimeout(function() {
      recognition.stop();
      reject('No speech detected');
    }, 10000);

    recognition.onresult = function(event) {
      clearTimeout(timeoutId);
      var results = event.results;
      if (results && results.length > 0) {
        var result = results[0];
        if (result && result[0] && result[0].transcript) {
          resolve(result[0].transcript);
        } else {
          reject('No speech detected');
        }
      } else {
        reject('No speech detected');
      }
    };

    recognition.onerror = function(event) {
      clearTimeout(timeoutId);
      reject(event.error || 'Speech recognition failed');
    };

    recognition.onend = function() {
      clearTimeout(timeoutId);
    };

    recognition.start();
  });
}

export function isSupported() {
  var tts = typeof window !== 'undefined' && typeof window.speechSynthesis !== 'undefined';
  var stt = typeof window !== 'undefined' && (typeof window.SpeechRecognition !== 'undefined' || typeof window.webkitSpeechRecognition !== 'undefined');
  return { tts: tts, stt: stt };
}