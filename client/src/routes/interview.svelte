<script lang="ts">
  enum ConnectionStatus {
    IDLE = "Idle",
    CONNECTING = "Connecting",
    CONNECTED = "Connected",
    CONNECTION_FAILED = "Connection failed",
    ERROR = "Connection error",
  }
  interface TranscriptWord {
    conf: number;
    start: number;
    end: number;
    word: string;
  }
  interface TranscriptBlock {
    words: TranscriptWord[];
  }

  let connection, channel;

  let status: ConnectionStatus = ConnectionStatus.IDLE;
  let transcript: TranscriptBlock[] = [];
  let partial = "";

  function negotiate() {
    return connection
      .createOffer()
      .then(function (offer) {
        return connection.setLocalDescription(offer);
      })
      .then(function () {
        return new Promise<void>((resolve) => {
          if (connection.iceGatheringState === "complete") {
            resolve();
          } else {
            function checkState() {
              if (connection.iceGatheringState === "complete") {
                connection.removeEventListener(
                  "icegatheringstatechange",
                  checkState
                );
                resolve();
              }
            }

            connection.addEventListener("icegatheringstatechange", checkState);
          }
        });
      })
      .then(function () {
        var offer = connection.localDescription;
        console.log(offer.sdp);
        return fetch("/offer", {
          body: JSON.stringify({
            sdp: offer.sdp,
            type: offer.type,
          }),
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
        });
      })
      .then(function (response) {
        return response.json();
      })
      .then(function (answer) {
        console.log(answer.sdp);
        return connection.setRemoteDescription(answer);
      })
      .catch(function (e) {
        console.log(e);
        status = ConnectionStatus.ERROR;
      });
  }

  function start() {
    console.log("%c === Starting WebRTC Connection === ", "color: #d79f20");
    status = ConnectionStatus.CONNECTING;
    // @ts-ignore
    connection = new RTCPeerConnection({ sdpSemantics: "unified-plan" });
    channel = connection.createDataChannel("chat", {});
    channel.onclose = () => {
      status = ConnectionStatus.IDLE;
      console.log("%c === WebRTC Data Channel Closed === ", "color: #d79f20");
    };
    channel.onopen = () => {
      status = ConnectionStatus.CONNECTED;
      console.log("%c =!= WebRTC Connection Successful =!= ", "color: #09ad43");
    };
    channel.onmessage = (event) => {
      if (event.data !== undefined) {
        const data = JSON.parse(event.data);
        if (data.text !== undefined) {
          console.log(data);
          transcript = [...transcript, data.result];
        } else if (data.partial !== undefined) {
          partial = data.partial;
        }
      }
    };
    connection.oniceconnectionstatechange = () => {
      if (connection.iceConnectionState == "disconnected") {
        status = ConnectionStatus.IDLE;
        console.log(
          "%c === WebRTC Connection Disconnected === ",
          "color: #d79f20"
        );
      }
    };

    const constraints = {
      audio: true,
      video: false,
    };

    navigator.mediaDevices.getUserMedia(constraints).then(
      function (stream) {
        stream.getTracks().forEach(function (track) {
          connection.addTrack(track, stream);
        });
        return negotiate();
      },
      function (err) {
        console.log("Could not acquire media: " + err);
        status = ConnectionStatus.ERROR;
      }
    );
  }
  function stop() {
    // close data channel
    if (channel) {
      channel.close();
    }

    // close transceivers
    if (connection.getTransceivers) {
      connection.getTransceivers().forEach(function (transceiver) {
        if (transceiver.stop) {
          transceiver.stop();
        }
      });
    }

    // close local audio / video
    connection.getSenders().forEach(function (sender) {
      sender.track.stop();
    });

    // close peer connection
    setTimeout(function () {
      connection.close();
    }, 500);
  }
</script>

<section>
  <h1>Interview</h1>
  <button
    disabled={status === ConnectionStatus.CONNECTING}
    on:click={() => {
      if (status === ConnectionStatus.CONNECTED) stop();
      else start();
    }}>{status === ConnectionStatus.CONNECTED ? "Stop" : "Start"}</button
  >
  <div class="status">{status}</div>
  <div class="transcript">
    <div class="transcript__content">
      {#each transcript as block}
        <div class="transcript__block">
          {#each block.words as wordData}
            <span class="transcript__word">{wordData.word}</span>
          {/each}
        </div>
      {/each}
    </div>
    <div class="transcript__partial">{partial}</div>
  </div>
</section>
