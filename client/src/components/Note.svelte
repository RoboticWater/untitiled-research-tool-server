<script lang="ts" context="module">
  export interface NoteInterface {
    id: string;
    text: string;
    created: Date;
    color?: string;
  }
</script>

<script lang="ts">
  import moment from "moment";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  export let id: string;
  export let text: string;
  export let timestamp: Date;
  export let color: string | null = null;

  let focused = false;
  // export let followups: NoteInterface[] = [];

  let ref: HTMLElement;

  function handleNoteClick(event: MouseEvent) {
    if (focused) return;
    focused = true;
    const content = ref.querySelector(".note__content") as HTMLInputElement;
    content.focus();
    document.execCommand("selectAll", false, null);
  }

  function handleDeleteNote(event: MouseEvent) {
    dispatch("delete", { event, note: { text, timestamp } });
  }

  function handleBlur(event: FocusEvent) {
    focused = false;
    dispatch("blur", { event, note: { text, timestamp } });
  }

  function handleChange(event: Event) {
    dispatch("change", { event, note: { text, timestamp } });
  }

  function handleAddFollowup(event: MouseEvent) {
    dispatch("addfollowup", {
      event,
      note: { text: "", timestamp: new Date() },
    });
  }
</script>

<div class="note" bind:this={ref} on:click={handleNoteClick} on:focusout={handleBlur}>
  <div class="content">
    <input class="note__content" type="text" on:change={handleChange} bind:value={text} />
    <div class="note__timestamp">{moment(timestamp).format("HH:mm:ss")}</div>
    <button class="delete" on:click={handleDeleteNote} />
  </div>
  <!-- <div class="followups">
    {#each followups as followup}
      <div class="followup">{1}</div>
    {/each}
    <button>Add Follow-up</button>
  </div> -->
</div>

<style lang="scss">
  .note {
    margin: 10px;
    width: 400px;
  }
  .content {
    background: #fff;
    color: #333;
    padding: 15px;
    width: 100%;
    box-sizing: border-box;
    transition: box-shadow 0.3s ease;
    display: inline-grid;
    grid-template-areas: "input delete" "timestamp timestamp";
    grid-template-columns: 1fr auto;
    grid-template-rows: repeat(auto);
    // min-width: 200px;
    // max-width: 400px;
    // border: 1px var(--text-color) solid;
    // border-radius: 4px;
    // &:hover {
    // 	box-shadow: 0 0 10px 10px rgba(0, 0, 0, 0.01);
    // }
    .note__content {
      grid-area: input;
      padding: 3px;
      border: none;
    }
    .note__timestamp {
      grid-area: timestamp;
      color: #777;
      font-size: 0.8em;
      margin-top: 10px;
      // text-align: right;
    }
    .delete {
      grid-area: delete;
      width: 16px;
      height: 16px;
      margin: 2px 0 0 4px;
      cursor: pointer;
      position: relative;
      background: none;
      border: none;
      &:before {
        content: "";
        position: absolute;
        width: 100%;
        height: 1px;
        background: #999;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(45deg);
      }
      &:after {
        content: "";
        position: absolute;
        width: 100%;
        height: 1px;
        background: #999;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-45deg);
      }
    }
  }
  // .followups {
  //   background: #f6f6f6;
  //   padding: 5px 15px;
  //   text-align: right;
  //   & > button {
  //     border: none;
  //     padding: 5px 8px;
  //     background: none;
  //     cursor: pointer;
  //     color: #666;
  //     font-size: 0.9em;
  //     &:hover {
  //       background: #0001;
  //     }
  //   }
  // }
</style>
