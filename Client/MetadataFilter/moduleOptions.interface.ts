export interface ModuleOptions {
	name: ModuleName;
}

export type ModuleName = keyof typeof ModuleRoutes;

export const ModuleRoutes = {
	metadata: 'http://localhost:8083/',
	text: 'http://localhost:8085/',
};
