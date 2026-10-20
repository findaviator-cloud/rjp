import os
import win32com.client  # Agar pywin32 na ho to fallback neeche hai

try:
    import pyttsx3
    engine = pyttsx3.init()
    
    # Swara voice dhoondo
    swara_id = None
    for voice in engine.getProperty('voices'):
        if "swara" in voice.name.lower() or "hindi" in voice.name.lower():
            swara_id = voice.id
            break

    if swara_id:
        engine.setProperty('voice', swara_id)

    # LKG ke liye slow speed (-2 equivalent)
    engine.setProperty('rate', 130)

    os.makedirs("audio_game", exist_ok=True)

    items = [
        ("audio_game/q_a.wav", "तनिष्का, अ से अनार कौन सा है?"),
        ("audio_game/q_aa.wav", "तनिष्का, आ से आम कौन सा है?"),
        ("audio_game/q_i.wav", "तनिष्का, इ से इमली कौन सी है?"),
        ("audio_game/q_ee.wav", "तनिष्का, ई से ईख कौन सी है?"),
        ("audio_game/q_u.wav", "तनिष्का, उ से उल्लू कौन सा है?"),
        ("audio_game/win.wav", "शाबाश तनिष्का! बहुत बढ़िया!"),
        ("audio_game/wrong.wav", "अरे! फिर से कोशिश करो।")
    ]

    for path, text in items:
        print(f"Generating: {path}")
        engine.save_to_file(text, path)
    
    engine.runAndWait()
    print("\nSUCCESS: Saari WAV files audio_game folder mein ban gayi hain!")

except Exception as e:
    # Direct Windows SAPI fallback (Har Windows PC par 100% chalta hai)
    import comtypes.client
    print("Using direct Windows SAPI...")
    os.makedirs("audio_game", exist_ok=True)
    speaker = comtypes.client.CreateObject("SAPI.SpVoice")
    
    # Select Swara
    for voice in speaker.GetVoices():
        if "swara" in voice.GetDescription().lower():
            speaker.Voice = voice
            break
            
    speaker.Rate = -2
    
    items = [
        ("audio_game\\q_a.wav", "तनिष्का, अ से अनार कौन सा है?"),
        ("audio_game\\q_aa.wav", "तनिष्का, आ से आम कौन सा है?"),
        ("audio_game\\q_i.wav", "तनिष्का, इ से इमली कौन सी है?"),
        ("audio_game\\q_ee.wav", "तनिष्का, ई से ईख कौन सी है?"),
        ("audio_game\\q_u.wav", "तनिष्का, उ से उल्लू कौन सा है?"),
        ("audio_game\\win.wav", "शाबाश तनिष्का! बहुत बढ़िया!"),
        ("audio_game\\wrong.wav", "अरे! फिर से कोशिश करो।")
    ]

    for path, text in items:
        file_stream = comtypes.client.CreateObject("SAPI.SpFileStream")
        file_stream.Open(path, 3, False)
        speaker.AudioOutputStream = file_stream
        speaker.Speak(text)
        file_stream.Close()
        print(f"Created: {path}")

    print("\nSUCCESS: SAPI se sabhi WAV files audio_game folder mein ban gayi!")