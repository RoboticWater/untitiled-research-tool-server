from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
import logging
import sys
import ssl
import concurrent.futures
import asyncio

from pathlib import Path
from vosk import KaldiRecognizer, Model
from av.audio.resampler import AudioResampler
from aiortc import RTCSessionDescription, RTCPeerConnection

from fastapi_socketio import SocketManager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).parent

# Set up sever parameters
vosk_port = int(os.environ.get('VOSK_SERVER_PORT', 2700))
vosk_interface = os.environ.get('VOSK_SERVER_INTERFACE', 'localhost')
vosk_cert_file = os.environ.get('VOSK_CERT_FILE', None)

# Set up Vosk parameters
vosk_model_path = os.environ.get('VOSK_MODEL_PATH', ROOT / 'model')
vosk_sample_rate = float(os.environ.get('VOSK_SAMPLE_RATE', 16000))

print(vosk_model_path)
# Create Vosk model + threading setup
model = Model(str(vosk_model_path))
pool = concurrent.futures.ThreadPoolExecutor((os.cpu_count() or 1))
loop = asyncio.get_event_loop()

# Create server app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: specify origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
sio = SocketManager(app=app)

# Mount static directory to serve files
app.mount("/static", StaticFiles(directory="client/public"), name="static")
templates = Jinja2Templates(directory="client/public")


def process_chunk(rec, message):
    if rec.AcceptWaveform(message):
        o = json.loads(rec.Result())
        if 'result' in o.keys():
            return json.dumps(o)
        return rec.Result()
    else:
        return rec.PartialResult()


class KaldiTask:
    def __init__(self, user_connection):
        self.__resampler = AudioResampler(
            format='s16', layout='mono', rate=48000)
        self.__pc = user_connection
        self.__audio_task = None
        self.__track = None
        self.__channel = None
        self.__recognizer = KaldiRecognizer(model, 48000)
        self.__recognizer.SetWords(True)

    async def set_audio_track(self, track):
        self.__track = track

    async def set_text_channel(self, channel):
        self.__channel = channel

    async def start(self):
        self.__audio_task = asyncio.create_task(self.__run_audio_xfer())

    async def stop(self):
        if self.__audio_task is not None:
            self.__audio_task.cancel()
            self.__audio_task = None

    async def __run_audio_xfer(self):
        dataframes = bytearray(b"")
        while True:
            frame = await self.__track.recv()
            frame = self.__resampler.resample(frame)
            max_frames_len = 16000
            message = frame.planes[0].to_bytes()
            recv_frames = bytearray(message)
            dataframes += recv_frames
            if len(dataframes) > max_frames_len:
                wave_bytes = bytes(dataframes)
                response = await loop.run_in_executor(pool, process_chunk, self.__recognizer, wave_bytes)
                print(response)
                self.__channel.send(response)
                dataframes = bytearray(b"")


async def offer(request):

    params = await request.json()
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type'])

    pc = RTCPeerConnection()

    kaldi = KaldiTask(pc)

    @pc.on('datachannel')
    async def on_datachannel(channel):
        await kaldi.set_text_channel(channel)
        await kaldi.start()

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == 'failed':
            await pc.close()

    @pc.on('track')
    async def on_track(track):
        if track.kind == 'audio':
            await kaldi.set_audio_track(track)

        @track.on('ended')
        async def on_ended():
            await kaldi.stop()

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return Response(content=json.dumps({
        'sdp': pc.localDescription.sdp,
        'type': pc.localDescription.type
    }), media_type='application/json')


@app.post("/offer")
async def offer(request: Request):
    return await offer(request)


# @app.get('/api/messages')
# async def messages(request: Request):
#     print([m.body for m in client.messages.list(to='+15108769505')])
#     return Response(content=json.dumps([m.body for m in client.messages.list(to='+15108769505')]))


twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(twilio_account_sid, twilio_auth_token)


@app.api_route("/sms", methods=['GET', 'POST'])
def sms_reply(request: Request):
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()
    print(request, request.json())

    # Add a message
    resp.message("Message received")
    print(str(resp))

    return Response(content=str(resp), media_type='application/xml')


@app.get("/{path_name:path}")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# message = client.messages \
#                 .create(
#                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
#                     from_='+15017122661',
#                     to='+15558675310'
#                 )


if __name__ == '__main__':
    import uvicorn

    if vosk_cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(vosk_cert_file)
    else:
        ssl_context = None

    uvicorn.run("server:app", host=vosk_interface,
                port=vosk_port, reload=True, debug=False)

    # app = web.Application()
    # app.router.add_post('/offer', offer)

    # app.router.add_get('/', index)
    # app.router.add_static('/static/', path=ROOT / 'static', name='static')

    # web.run_app(app, port=vosk_port, ssl_context=ssl_context)
