# Phase 2 test checklist — tick each before moving to Phase 3

- [ ] Backend starts: uvicorn main:app --reload --port 8001
- [ ] GET http://localhost:8001/api/health returns {"status": "ok"}
- [ ] POST http://localhost:8001/api/messages/respond with {"text": "hello", "user_id": 1}
      returns a response (even placeholder is fine)
- [ ] VoiceInterface mic button visible on home screen
- [ ] Tapping mic button changes colour to red
- [ ] Browser asks for microphone permission
- [ ] Speaking is captured and displayed as transcript
- [ ] Response text is returned from backend
- [ ] Response is spoken aloud via TTS
- [ ] Speaking state shows green mic button
- [ ] Returns to idle state after speaking
- [ ] No console errors throughout