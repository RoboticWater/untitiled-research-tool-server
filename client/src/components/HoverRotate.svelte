<script lang="ts">
	import { spring } from 'svelte/motion';

	export let rotateXAmount: number = -0.15;
	export let rotateYAmount: number = 0.15;
	export let perspective: number = 500;

	let coords = spring(
		{ x: 0, y: 0 },
		{
			stiffness: 0.1,
			damping: 0.5
		}
	);
	let parentElem;

	let isHovering = false;
	function onMouseEnter(event: MouseEvent) {
		if (event.target !== parentElem) return;
		event.stopPropagation();
		isHovering = true;
	}
	function onMouseMove(event: MouseEvent) {
		event.stopPropagation();
		const rect = parentElem.getBoundingClientRect();
		coords.set({
			x: event.clientX - (rect.right + rect.left) / 2,
			y: event.clientY - (rect.bottom + rect.top) / 2
		});
	}
	function onMouseExit(event: MouseEvent) {
		event.stopPropagation();
		isHovering = false;
		coords.set({ x: 0, y: 0 });
	}
</script>

<div
	bind:this={parentElem}
	class="hover-container"
	style={perspective ? `perspective: ${perspective}px` : ''}
	class:hovering={isHovering}
	on:mouseenter={onMouseEnter}
	on:mouseleave={onMouseExit}
	on:mousemove={onMouseMove}
>
	<div
		class="hover"
		style={`transform: rotateX(${rotateXAmount * $coords.y}deg)\
      rotateY(${rotateYAmount * $coords.x}deg)`}
	>
		<slot />
	</div>
</div>

<style>
	.hover-container {
		perspective: 500px;
	}
	.hover {
		transform-style: preserve-3d;
		-webkit-transform-style: preserve-3d;
	}
	/* .hover-container .hover {
		transition: transform 0.05s ease;
		transform: none;
	}
	.hover-container.hovering .hover {
		transition: none;
	} */
</style>
