import { writable } from 'svelte/store';
import produce from 'immer';
import type { Vector } from './utils';

interface SnapState {
	coords: Vector;
	snap: boolean;
}

const initialState: SnapState = { coords: { x: 0, y: 0 }, snap: false };

//TODO
function createSnap() {
	const { subscribe, set, update } = writable<SnapState>(initialState);

	return {
		subscribe,
		setSnapCoords: (x, y) =>
			update((state) =>
				produce(state, (draft) => {
					draft.coords = { x, y };
					draft.snap = true;
				})
			),
		unsetSnap: () =>
			update((state) =>
				produce(state, (draft) => {
					draft.snap = false;
				})
			)
		// decrement: () => update(n => n - 1),
		// reset: () => set(0)
	};
}

export const snap = createSnap();
