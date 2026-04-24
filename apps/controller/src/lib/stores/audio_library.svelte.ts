// Audio Library store — type exports only
// AudioLibraryGrid is self-contained; this file exports the shared ClipMeta type

export type ClipMeta = {
	id: string;
	category: string;
	tags: string[];
	duration_ms: number;
	script: string;
	scene_hint: string;
};
