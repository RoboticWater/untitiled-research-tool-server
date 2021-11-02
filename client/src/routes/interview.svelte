<script lang="ts">
  import { afterUpdate, onMount } from "svelte";

  import Note from "../components/Note.svelte";
  import type { NoteInterface } from "../components/Note.svelte";

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

  let notes: NoteInterface[] = [];
  let notesRef: HTMLElement;
  let noteAdded = false;
  let saveTimeout;

  onMount(() => {
    fetch("/api/note")
      .then((res) => {
        return res.json();
      })
      .then(({ data }) => {
        notes = data;
      });
  });

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
                connection.removeEventListener("icegatheringstatechange", checkState);
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
      if (event.data) {
        const data = JSON.parse(event.data);
        if (data.result) {
          data.result[0].word = data.result[0].word.charAt(0).toUpperCase() + data.result[0].word.slice(1);
          transcript = [...transcript, { words: data.result }];
          partial = "";
        } else if (data.partial) {
          partial = data.partial.charAt(0).toUpperCase() + data.partial.slice(1);
        }
      }
    };
    connection.oniceconnectionstatechange = () => {
      if (connection.iceConnectionState == "disconnected") {
        status = ConnectionStatus.IDLE;
        console.log("%c === WebRTC Connection Disconnected === ", "color: #d79f20");
      }
    };

    const constraints = {
      audio: true,
      video: false,
    };

    navigator.mediaDevices.getUserMedia(constraints).then(
      (stream) => {
        stream.getTracks().forEach((track) => {
          connection.addTrack(track, stream);
        });
        return negotiate();
      },
      (err) => {
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
      connection.getTransceivers().forEach((transceiver) => {
        if (transceiver.stop) {
          transceiver.stop();
        }
      });
    }

    // close local audio / video
    connection.getSenders().forEach((sender) => {
      sender.track.stop();
    });

    // close peer connection
    setTimeout(() => {
      connection.close();
    }, 500);
  }

  afterUpdate(() => {
    // store.set('notes', notes);
    // clearTimeout(saveTimeout);
    // saveTimeout = setTimeout(() => store.set('notes', notes), 500);
    if (noteAdded) {
      const childNotes: HTMLCollectionOf<Element> = notesRef.getElementsByClassName("note");
      const lastNote: HTMLElement = childNotes[childNotes.length - 1] as HTMLElement;
      (lastNote.getElementsByClassName("note__content")[0] as HTMLElement).focus();
      // notes[notes.length - 1].text = "";
      noteAdded = false;
    }
  });

  async function addNote(text: string = "", runPostUpdate: boolean = true) {
    const res = await fetch("/api/note", {
      method: "POST",
      body: JSON.stringify({ text }),
      headers: {
        "Content-Type": "application/json",
      },
    }).then((res) => {
      return res.json();
    });
    console.log(res);

    const note = res.data;
    notes = [...notes, note];
    noteAdded = runPostUpdate;
  }

  function handleDeleteNote(note: NoteInterface, i: number) {
    notes.splice(i, 1);
    notes = notes;
    fetch("/api/note/" + note.id, { method: "DELETE" });
  }

  function handleChange(note: NoteInterface, i: number) {
    if (note.text === "") {
      handleDeleteNote(note, i);
    } else {
      fetch("/api/note/" + note.id, {
        method: "PUT",
        body: JSON.stringify({ text: note.text }),
        headers: {
          "Content-Type": "application/json",
        },
      });
    }
  }

  function handleBlur(note: NoteInterface, i: number) {
    if (note.text === "") {
      handleDeleteNote(note, i);
    }
  }

  function getSelectionText() {
    var text = "";
    if (window.getSelection) {
      text = window.getSelection().toString();
    } else if (document.selection && document.selection.type != "Control") {
      text = document.selection.createRange().text;
    }
    return text;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === " " && event.ctrlKey) {
      const selection = getSelectionText();
      if (selection !== "") addNote(selection);
    }
  }

  function handleAddNote() {
    const selection = getSelectionText();
    addNote(selection || "");
  }
</script>

<svelte:window on:keydown={handleKeydown} />
<section>
  <content>
    <div class="meta">
      <h1>Interview</h1>
      <div class="controls">
        <button
          disabled={status === ConnectionStatus.CONNECTING}
          on:click={() => {
            if (status === ConnectionStatus.CONNECTED) stop();
            else start();
          }}
          >{status === ConnectionStatus.CONNECTED ? "Stop" : "Start"}
          <svg width="16px" height="16px">
            <path xmlns="http://www.w3.org/2000/svg" d="m4,3 l8,5 l-8,5 l0,-10z" stroke="var(--black)" fill="var(--black)" />
          </svg>
        </button>
        <div class="status">
          {status}
          <div class="status-icon" class:conencted={status === ConnectionStatus.CONNECTED} class:error={status === ConnectionStatus.ERROR} class:connecting={status === ConnectionStatus.CONNECTING} />
        </div>
      </div>
    </div>
    <div class="transcript">
      <div class="transcript__content">
        {#each transcript as block}
          <div class="transcript__block">
            {#each block.words as wordData, i}
              <span class="transcript__word">{wordData.word}</span>{#if i < block.words.length - 1}&nbsp;{/if}
            {/each}
          </div>
        {/each}
      </div>
      <div class="transcript__partial">{partial}</div>
    </div>
    <div bind:this={notesRef} class="notes">
      {#each notes as note, i}
        <Note id={note.id} bind:text={note.text} timestamp={note.created} on:delete={() => handleDeleteNote(note, i)} on:change={() => handleChange(note, i)} on:blur={() => handleBlur(note, i)} />
      {/each}
      <button class="add-note" on:click={handleAddNote}> Add note +</button>
    </div>
  </content>
</section>

<style lang="scss">
  section {
    display: grid;
    /* grid-template-rows: auto 1fr; */
    height: 100%;
  }
  content {
    display: grid;
    grid-template-areas:
      ". meta ."
      ". transcript notes";
    grid-template-rows: auto 1fr;
    grid-template-columns: minmax(0px, 1fr) 800px minmax(420px, 1fr);
    gap: 10px;
  }
  .transcript {
    grid-area: transcript;
  }
  .meta {
    grid-area: meta;
  }
  .notes {
    grid-area: notes;
    background: #efefef;
  }
  @media screen and (max-width: 1220px) {
    content {
      grid-template-columns: 0 minmax(500px, 1fr) 420px;
    }
  }
  button {
    background: none;
    border: 1px var(--black) solid;
    display: flex;
    align-items: center;
    cursor: pointer;
  }
  button:hover {
    background: var(--black);
    color: var(--white);
    path {
      stroke: var(--white);
      fill: var(--white);
    }
  }
  button:disabled {
    opacity: 0.5;
    color: var(--black);
    pointer-events: none;
  }
  svg {
    display: inline;
    padding-left: 3px;
  }
  .transcript__block {
    padding: 3px;
  }
  .transcript__partial {
    padding: 8px 10px;
    margin-top: 10px;
    background: #efefef;
    min-height: 18px;
  }

  .add-note {
    cursor: pointer;
    width: 400px;
    margin: 10px;
    padding: 15px;
    box-sizing: border-box;
  }
  .transcript__word {
    display: inline-block;
  }
  .controls {
    display: flex;
    justify-content: space-between;
  }
  .status {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .status-icon {
    background: #f5de0f;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    &.error {
      background: #f52a0f;
    }
    &.conencted {
      background: #1aec83;
    }
    &.connecting {
      background: #969696;
      animation: connecting 2s cubic-bezier(0.67, 0.09, 0.2, 0.92) infinite forwards;
    }
  }
  @keyframes connecting {
    0% {
      transform: scale(1);
    }
    20% {
      transform: scale(0.3);
    }
    50% {
      transform: scale(0.3);
    }
    80% {
      transform: scale(1);
    }
    100% {
      transform: scale(1);
    }
  }
</style>
