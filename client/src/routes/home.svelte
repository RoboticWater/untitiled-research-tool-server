<script context="module" lang="ts">
  export const prerender = true;
</script>

<script lang="ts">
  import type { SvelteComponent } from "svelte";
  import HoverRotate from "../components/HoverRotate.svelte";

  import MdFormatAlignLeft from "svelte-icons/md/MdFormatAlignLeft.svelte";
  import MdMap from "svelte-icons/md/MdMap.svelte";
  import MdNote from "svelte-icons/md/MdNote.svelte";
  interface Component {
    name: string;
    icon: typeof SvelteComponent;
    link: string;
  }

  export let location;

  const components: Component[] = [
    {
      name: "Interview",
      link: "interview",
      icon: MdFormatAlignLeft,
    },
    // {
    //   name: "Sticky Notes",
    //   link: "stickynotes",
    //   icon: MdNote,
    // },
    {
      name: "Journey Mapping",
      link: "journeymap",
      icon: MdMap,
    },
  ];
</script>

<svelte:head>
  <title>Home</title>
</svelte:head>

<section>
  <div class="components">
    {#each components as component, i}
      <HoverRotate>
        <a
          href={component.link}
          class="component"
          style={`animation-delay: ${i * 0.1}s`}
        >
          <div class="component__icon">
            <svelte:component this={component.icon} />
          </div>
          <div class="component__name">{component.name}</div>
        </a>
      </HoverRotate>
    {/each}
  </div>
  <h1>
    <div class="title">Untitled</div>
    <div>Research Tool</div>
  </h1>
</section>

<style lang="scss">
  h1 {
    position: fixed;
    bottom: 10%;
    left: 4%;
    font-size: 5em;
    grid-area: title;
    margin: 20px 40px 0;
    font-weight: 600;
    animation: fade-in 0.5s ease forwards;
    font-family: var(--font-mono);
    .title {
      font-weight: 200;
      font-size: 1.5em;
      font-style: italic;
      margin-bottom: -32px;
    }
  }
  section {
    display: grid;
    grid-template-rows: 1fr;
    grid-template-areas: "." "components" "title";
    width: 100%;
    padding-top: 15%;
  }
  .components {
    grid-area: components;
    justify-self: center;
    align-self: center;
    width: 80%;
    display: grid;
    justify-content: center;
    grid-template-columns: repeat(auto-fit, 200px);
    grid-template-rows: repeat(auto-fit, 200px);
    gap: 20px;
    // perspective: 100px;
  }

  .component {
    opacity: 0;
    display: grid;
    grid-template-rows: 40px 1fr minmax(40px, auto);
    justify-items: center;
    align-items: center;
    height: 200px;
    cursor: pointer;
    transition: all 0.15s ease;
    border: 1px var(--text-color) solid;
    animation: component-intro 0.5s ease forwards;
    box-sizing: border-box;
    color: var(--text-color);
    border-radius: 4px;
    font-family: var(--font-mono);
    // font-weight: 600;
    &:hover {
      // background: #ddd;
      border-color: var(--accent-color);
      color: var(--accent-color);
    }
    .component__icon {
      width: 40%;
      grid-area: 2;
    }
    .component__name {
      grid-area: 3;
      justify-self: left;
      padding-left: 10px;
    }
  }

  @keyframes component-intro {
    0% {
      opacity: 0;
      transform: rotateX(21deg);
    }
    100% {
      opacity: 1;
      transform: none;
    }
  }

  @keyframes fade-in {
    0% {
      opacity: 0;
    }
    100% {
      opacity: 1;
    }
  }
</style>
