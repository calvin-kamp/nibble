interface HelpLink {
	label: string
	routeName?: string
	hash?: string
	href?: string
}

interface HelpQuestion {
	id: string
	question: string
	answer: string[]
	links?: HelpLink[]
}

export interface HelpTopic {
	/** Jump mark of the section, also used in the footer */
	id: string
	title: string
	lead: string
	questions: HelpQuestion[]
}

export interface HelpGuide {
	id: string
	title: string
	lead: string
	steps: string[]
	links?: HelpLink[]
}
