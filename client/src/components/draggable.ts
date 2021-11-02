export function draggable(node: HTMLElement): { destroy: () => void } {
	let x;
	let y;
	let startX;
	let startY;

	function handleMousedown(event) {
		startX = x = event.clientX;
		startY = y = event.clientY;

		node.dispatchEvent(
			new CustomEvent('dragstart', {
				detail: { x, y, startX, startY }
			})
		);

		window.addEventListener('mousemove', handleMousemove);
		window.addEventListener('mouseup', handleMouseup);
	}

	function handleMousemove(event) {
		const dx = event.clientX - x;
		const dy = event.clientY - y;
		x = event.clientX;
		y = event.clientY;

		node.dispatchEvent(
			new CustomEvent('dragmove', {
				detail: { x, y, dx, dy, startX, startY }
			})
		);
	}

	function handleMouseup(event) {
		x = event.clientX;
		y = event.clientY;

		node.dispatchEvent(
			new CustomEvent('dragend', {
				detail: { x, y, startX, startY }
			})
		);

		window.removeEventListener('mousemove', handleMousemove);
		window.removeEventListener('mouseup', handleMouseup);
	}

	node.addEventListener('mousedown', handleMousedown);

	return {
		destroy() {
			node.removeEventListener('mousedown', handleMousedown);
		}
	};
}
