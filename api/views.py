from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.http import JsonResponse
from google.cloud import translate_v2 as translate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.cloud import texttospeech, speech
from django.http import HttpResponse
from rest_framework.parsers import BaseParser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
class TTSView(APIView):
    def get(self, request):
        print("Received request for TTS")
        text = request.query_params.get("text", "Hello from Garuda.")
        lang = request.query_params.get("lang", "en-US")
        if not text:
            return Response({"error": "Text missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            # Return audio/mp3 using HttpResponse instead of Response to avoid JSON serialization
            return HttpResponse(response.audio_content, content_type='audio/mpeg')

        except Exception as e:
            # return Response(f"Error: {str(e)}", status=500)
            return HttpResponse(f"Error generating speech: {str(e)}", status=500, content_type="text/plain")


class RawBinaryParser(BaseParser):
    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()
    
@method_decorator(csrf_exempt, name='dispatch')
class STTView(APIView):
    parser_classes = [RawBinaryParser]
    
    def post(self, request, *args, **kwargs):
        print("Received request for STT")
        lang = request.GET.get("lang", "en-US").split(",")
        audio_data = request.data

        try:
            client = speech.SpeechClient()
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=lang[0],
                alternative_language_codes=lang[1:]  # Other languages to auto-detect
            )
            response = client.recognize(config=config, audio=audio)
            transcript = " ".join([r.alternatives[0].transcript for r in response.results])
            return Response({'transcript': transcript})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

@method_decorator(csrf_exempt, name='dispatch')
class TranslateView(APIView):
    def get(self, request, *args, **kwargs):
        text = request.GET.get('text', '')
        target_lang = request.GET.get('lang', 'hi')

        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        try:
            client = translate.Client()
            result = client.translate(text, target_language=target_lang.split('-')[0])
            return JsonResponse({'translated_text': result['translatedText']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
