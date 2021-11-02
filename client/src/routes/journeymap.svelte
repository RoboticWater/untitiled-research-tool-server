<script lang="ts">
  import MapCell from "../components/MapCell.svelte";
  import type { StickyNoteInterface } from "../components/StickyNote.svelte";
  import { draggable } from "../components/draggable";
  import DropArea from "../components/DropArea.svelte";
  import { onMount } from "svelte";

  interface JournemMap {
    rows: number[];
    cols: number[];
    cells: { notes: StickyNoteInterface[] }[][];
  }
  let notes = [];
  // { notes: [{ text: 'test', coords: { x: 0, y: 0 }, comments: [] }] }
  //TODO: consider using list of stickynotes with parent reference then filtering in the journeymap
  const map: JournemMap = {
    rows: [300, 300, 300],
    cols: [300, 300, 300],
    cells: [
      [{ notes: [] }, { notes: [] }, { notes: [] }],
      [{ notes: [] }, { notes: [] }, { notes: [] }],
      [{ notes: [] }, { notes: [] }, { notes: [] }],
    ],
  };

  onMount(() => {
    fetch("/api/note")
      .then((res) => {
        return res.json();
      })
      .then(({ data }) => {
        notes = data.map((n, i) => ({
          ...n,
          coords: { x: 1000 + i * 250, y: 0 },
        }));
      });
  });

  function handleDragResizeMove(axis: "x" | "y", index: number, event) {
    map[axis === "y" ? "rows" : "cols"][index] += axis === "x" ? event.detail.dx : event.detail.dy;
  }

  function handleMoveNote(event: any, destX: number, destY: number) {
    const { parent, node } = event.detail;
    console.log(parent, destX, destY, node, event.target);
    if (parent.x === destX && parent.y === destY) return;
    var noteData;
    if (parent.x === -1) {
      noteData = notes[parent.index];
    } else {
      noteData = map.cells[parent.y][parent.x].notes[parent.index];
    }
    const notePos = node.getBoundingClientRect();
    const areaPos = event.target.getBoundingClientRect();
    noteData.coords.x = notePos.x - areaPos.x;
    noteData.coords.y = notePos.y - areaPos.y;
    if (destX === -1) {
      notes.push(noteData);
      notes = notes;
    } else {
      map.cells[destY][destX].notes.push(noteData);
    }

    if (parent.x === -1) {
      notes.splice(parent.index, 1);
      notes = notes;
    } else {
      map.cells[parent.y][parent.x].notes.splice(parent.index, 1);
    }
    map.cells = map.cells;
  }

  function handleAddRow(index: number) {
    map.rows.splice(index + 1, 0, map.rows[index]);
    map.rows = map.rows;
    map.cells.splice(
      index + 1,
      0,
      [...new Array(map.cols.length)].map((e) => ({ notes: [] }))
    );
    map.cells = map.cells;
  }

  function handleAddCol(index: number) {
    map.cols.splice(index + 1, 0, map.cols[index]);
    map.cols = map.cols;
    map.cells.forEach((row) => {
      row.splice(index + 1, 0, { notes: [] });
    });
    map.cells = map.cells;
  }
</script>

<section>
  <DropArea
    handleMoveNote={(event) => handleMoveNote(event, -1, -1)}
    notes={notes.map((note, i) => ({
      ...note,
      parent: { x: -1, y: -1, index: i },
    }))}
  >
    <div class="map">
      <div class="col-handles">
        {#each map.cols.reduce((acc, cur, i) => [...acc, (i > 0 ? acc[acc.length - 1] : 0) + cur], []) as handle, i}
          <div class="handle col" style={`left: ${handle}px`} use:draggable on:dragmove={(e) => handleDragResizeMove("x", i, e)}>
            <button class="add-track col" on:click={() => handleAddCol(i)}>+</button>
          </div>
        {/each}
      </div>
      <div class="row-handles">
        {#each map.rows.reduce((acc, cur, i) => [...acc, (i > 0 ? acc[acc.length - 1] : 0) + cur], []) as handle, i}
          <div class="handle row" style={`top: ${handle}px`} use:draggable on:dragmove={(e) => handleDragResizeMove("y", i, e)}>
            <button class="add-track row" on:click={() => handleAddRow(i)}>+</button>
          </div>
        {/each}
      </div>
      {#each map.cells as row, y}
        <div class="row">
          {#each row as cell, x}
            <MapCell
              width={map.cols[x]}
              height={map.rows[y]}
              notes={cell.notes.map((note, i) => ({
                ...note,
                parent: { x, y, index: i },
              }))}
              handleMoveNote={(event) => handleMoveNote(event, x, y)}
            />
          {/each}
        </div>
      {/each}
    </div>
  </DropArea>
</section>

<style lang="scss">
  .row {
    display: flex;
  }
  .map {
    // border-top: 1px #ddd solid;
    // border-left: 1px #ddd solid;
    box-sizing: border-box;
    display: inline-flex;
    flex-direction: column;
    position: relative;
    border-left: 1px #ddd solid;
    border-top: 1px #ddd solid;
  }
  .handle {
    position: absolute;
    z-index: 100;
    opacity: 0;
    background: #ddd;
    transition: opacity 0.15s ease;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    &:hover {
      opacity: 1;
    }
    &.col {
      cursor: ew-resize;
      top: 0;
      bottom: 0;
      width: 20px;
      transform: translateX(-50%);
    }
    &.row {
      cursor: ns-resize;
      left: 0;
      right: 0;
      height: 20px;
      transform: translateY(-50%);
    }
    .add-track {
      position: absolute;
      &.row {
        right: -25px;
        top: 50%;
        transform: translate(0, -50%);
      }
      &.col {
        top: -25px;
        left: 50%;
        transform: translate(-50%, 0);
      }
    }
  }
</style>
