import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
from gtts import gTTS
import os

# ✅ Securely fetch API key from Streamlit input or environment variable
def setup_openai_client(api_key):
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("❌ Invalid API key. Please enter a valid OpenAI API key.")
    
    openai.api_key = api_key
    st.sidebar.success("✅ API Key Set Successfully")

# ✅ Function to transcribe Urdu audio using OpenAI Whisper API
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(  
            model="whisper-1",  
            file=audio_file,
            language="ur"
        )
    return transcript["text"].strip() if "text" in transcript else ""

# ✅ Function to get AI response in Urdu
def fetch_ai_response(input_text):
    if not input_text:  
        return "معذرت! میں آپ کی بات نہیں سن سکا۔ براہ کرم دوبارہ بولیں۔"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": input_text}],
        temperature=0.7,
        max_tokens=200
    )
    return response["choices"][0]["message"]["content"]

# ✅ Convert text to Urdu speech using Google TTS
def text_to_audio(text, audio_path):
    tts = gTTS(text=text, lang='ur')
    tts.save(audio_path)

# ✅ Main function to run the app
def main():
    st.sidebar.title("🔑 API Key Configuration")
    api_key = st.sidebar.text_input("اپنا OpenAI API کلید درج کریں", type="password")

    st.title("🗣️ Aurora SpeakEasy - اردو")
    st.write("السلام علیکم! مجھ سے بات کرنے کے لئے نیچے ریکارڈنگ کا بٹن دبائیں۔")

    if api_key:
        try:
            setup_openai_client(api_key)  # Ensure API key is set correctly
            recorded_audio = audio_recorder()

            if recorded_audio:
                audio_file = "audio.mp3"
                with open(audio_file, "wb") as f:
                    f.write(recorded_audio)

                transcribed_text = transcribe_audio(audio_file)

                if not transcribed_text:  
                    st.write("⚠️ کوئی آواز نہیں سنی گئی، براہ کرم دوبارہ کوشش کریں۔")
                    return  

                st.write("📝 **تحریری متن:** ", transcribed_text)

                ai_response = fetch_ai_response(transcribed_text)

                response_audio_file = "audio_response.mp3"
                text_to_audio(ai_response, response_audio_file)

                st.audio(response_audio_file)
                st.write("🤖 **AI کا جواب:** ", ai_response)

        except ValueError as e:
            st.sidebar.error(str(e))  # Show API key error
        except openai.error.AuthenticationError:
            st.sidebar.error("❌ OpenAI API Key Incorrect! Please enter a valid key.")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")  # Catch unexpected errors

if __name__ == "__main__":
    main()
