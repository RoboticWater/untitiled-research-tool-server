<script lang="ts">
  import DropArea from "./DropArea.svelte";

  export let width: number = 100;
  export let height: number = 100;
  export let notes = [];
  export let handleMoveNote: (event: any, dest: HTMLElement) => void;
</script>

<div
  class={"cell " + ($$props.class || "")}
  style={`width: ${width}px; height: ${height}px;`}
>
  <DropArea {notes} {handleMoveNote} />
</div>

<style lang="scss">
  .cell {
    border-bottom: 1px #ddd solid;
    border-right: 1px #ddd solid;
    box-sizing: border-box;
  }
</style>
