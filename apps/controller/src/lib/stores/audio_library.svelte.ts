export type ClipMeta = {
	id: string;
	category: string;
	text: string;
	file: string;
	product?: string;
	tags?: string[];
};

export const CATEGORIES = [
	'ALL', 'A_opening', 'B_reset_viewer', 'C_paloma_context', 'D_cctv_context',
	'E_senter_context', 'F_tracker_context', 'G_question_hooks', 'H_price_safe',
	'I_trust_safety', 'J_idle_human', 'K_closing',
] as const;
