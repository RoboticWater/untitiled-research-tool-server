/// <reference types="svelte" />
declare namespace svelte.JSX {
  interface DOMAttributes<T> {
    ondragmove?: CompositionEventHandler<T>;
    ondropreceive?: CompositionEventHandler<T>;
  }
}
