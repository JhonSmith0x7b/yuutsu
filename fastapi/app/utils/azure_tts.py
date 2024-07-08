import os
import azure.cognitiveservices.speech as speechsdk
import datetime
import uuid
def simple_tts(text: str) -> str:
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"), 
        region=os.getenv("AZURE_SPEECH_REGION")
        )
    audio_config = None
    speech_config.speech_synthesis_voice_name = os.getenv("AZURE_SPEECH_VOICE")
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, 
        audio_config=audio_config
        )
    result = speech_synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = f"./audios/{date[:8]}"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_uuid = str(uuid.uuid4())
        file_path = f"{file_path}/{date}-{file_uuid}.mp3"
        audio_data_stream = speechsdk.AudioDataStream(result)
        audio_data_stream.save_to_wav_file(file_path)
        return file_path
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    return None