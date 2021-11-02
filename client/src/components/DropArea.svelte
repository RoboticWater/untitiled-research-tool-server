<script lang="ts">
  import type { StickyNoteInterface } from "./StickyNote.svelte";
  import StickyNote from "./StickyNote.svelte";

  export let notes: StickyNoteInterface[] = [];
  export let handleMoveNote: (event: any, dest: HTMLElement) => void;

  function handleDropReceive(event) {
    event.stopPropagation();
    handleMoveNote(event, event.target);
  }
</script>

<div
  class={"drop-area " + ($$props.class || "")}
  on:dropreceive={handleDropReceive}
>
  {#each notes as note, i}
    <StickyNote {...note} />
  {/each}
  <slot />
</div>

<style>
  .drop-area {
    position: relative;
    height: 100%;
    width: 100%;
  }
</style>
