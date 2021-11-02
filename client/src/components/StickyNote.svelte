<script lang="ts" context="module">
  export interface StickyNoteInterface {
    text: string;
    comments: string[];
    coords: Vector;
  }
</script>

<script lang="ts">
  //TODO replace with https://daybrush.com/moveable/
  import type { Vector } from "./utils";
  import { onMount } from "svelte";
  import { draggable } from "./draggable";
  import { snap } from "./snapping";

  export let onDuplicate: (text: string, coords: Vector) => void = null;
  export let text: string = "";
  export let coords: Vector = { x: 0, y: 0 };
  export let parent: any = null;

  let comments = [];
  let content;
  let isEditable = false;
  let dragging = false;

  //TODO: should this be fixed so we don't have to worry about relative pos?
  let stickyNoteRef: HTMLElement;
  let initialScreenPos: Vector = null;

  onMount(() => {
    const rect = stickyNoteRef.getBoundingClientRect();
    initialScreenPos = {
      x: rect.x,
      y: rect.y,
    };
  });

  function onDragStart(event: MouseEvent) {
    if (isEditable) return;
  }

  function onDragEnd(event) {
    if ($snap.snap) {
      coords = {
        x: $snap.coords.x - initialScreenPos.x,
        y: $snap.coords.y - initialScreenPos.y,
      };
    }
    const dropTarget = document.elementFromPoint(
      event.detail.x,
      event.detail.y
    );
    const note: StickyNoteInterface = { text, coords, comments };
    dropTarget.dispatchEvent(
      new CustomEvent("dropreceive", {
        bubbles: true,
        detail: { note, parent, node: event.target },
      })
    );

    dragging = false;
  }

  function onDragMove(event) {
    if (isEditable) return;
    dragging = true;
    coords.x += event.detail.dx;
    coords.y += event.detail.dy;
  }

  function addComment() {
    comments = [...comments, "test"];
  }

  function handleHotKeys(event: KeyboardEvent) {
    if (event.ctrlKey && event.key === "d") {
      event.preventDefault();
      if (onDuplicate) onDuplicate(text, Object.assign({}, coords));
    }
    if (event.ctrlKey && event.altKey && event.key === "c") {
      event.preventDefault();
      addComment();
    }
  }

  function toggleEditable() {
    isEditable = !isEditable;
    if (isEditable) {
      content.focus();
      document.execCommand("selectAll", false, null);
    }
  }
</script>

<main
  use:draggable
  bind:this={stickyNoteRef}
  on:dragstart={onDragStart}
  on:dragmove={onDragMove}
  on:dragend={onDragEnd}
  on:keydown={handleHotKeys}
  on:dblclick={toggleEditable}
  tabindex="0"
  class:dragging
  class="stickynote"
  style={`transform: translate(
		${$snap.snap && dragging ? $snap.coords.x - initialScreenPos.x : coords.x}px, 
		${$snap.snap && dragging ? $snap.coords.y - initialScreenPos.y : coords.y}px)`}
>
  <div
    class="content"
    class:hidden={!isEditable}
    on:blur={toggleEditable}
    contenteditable="true"
    bind:innerHTML={text}
    bind:this={content}
  />
  <div
    class="content static"
    class:hidden={isEditable}
    on:keydown={handleHotKeys}
    on:blur={() => (isEditable = false)}
  >
    {text}
  </div>
  {#if comments.length > 0}
    <div
      class="comments"
      on:mousedown={(e) => e.stopPropagation()}
      on:dblclick={(e) => e.stopPropagation()}
    >
      {#each comments as comment, i}
        <div class="comment">
          <!-- {comment} -->
          <input type="text" bind:value={comments[i]} />
        </div>
      {/each}
    </div>
  {/if}
  <div class="focus-menu">
    <div class="add-buttons">
      <button class="add-button top">+</button>
      <button class="add-button left">+</button>
      <button class="add-button right">+</button>
      <button class="add-button bottom">+</button>
    </div>
  </div>
</main>

<style lang="scss">
  main {
    background: #fff67f;
    position: absolute;
    top: 0;
    left: 0;
    width: 200px;
    height: 200px;
    display: grid;
    cursor: grab;
    z-index: 10;
    &.dragging {
      cursor: grabbing;
      z-index: 100;
      opacity: 0.5;
      pointer-events: none;
    }
    &:focus:after {
      --border-width: 3px;
      content: "";
      border: var(--border-width) #209fda6c solid;
      position: absolute;
      top: calc(-1 * var(--border-width));
      left: calc(-1 * var(--border-width));
      right: calc(-1 * var(--border-width));
      bottom: calc(-1 * var(--border-width));
    }
  }
  .content {
    position: absolute;
    top: 0;
    left: 0;
    vertical-align: middle;
    width: 100%;
    height: 100%;
    text-align: center;
    display: grid;
    align-content: center;
    word-break: break-word;
    padding: 10px;
    box-sizing: border-box;
    &.static {
      user-select: none;
    }
    &.hidden {
      opacity: 0;
      pointer-events: none;
    }
  }
  .comments {
    position: absolute;
    width: 100%;
    left: 100%;
    top: 0;
    padding: 0 5px 5px 5px;
  }
  .comment {
    padding: 5px;
    background: #eee;
    margin-bottom: 5px;
  }
  .comment input {
    width: 100%;
    margin: 0;
    box-sizing: border-box;
    border: none;
    border-bottom: #0004 solid 1px;
    background: none;
  }
  .focus-menu {
    opacity: 0;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
  .add-button {
    position: absolute;
  }
  .add-button.right {
    top: 50%;
    right: -35px;
    transform: translate(0, -50%);
  }
  .add-button.left {
    top: 50%;
    left: -35px;
    transform: translate(0, -50%);
  }
  .add-button.top {
    left: 50%;
    top: -35px;
    transform: translate(-50%, 0);
  }
  .add-button.bottom {
    left: 50%;
    bottom: -35px;
    transform: translate(-50%, 0);
  }
  main:focus .focus-menu {
    opacity: 1;
  }
</style>
