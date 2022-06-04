import MetadataOptions from './metadataOptions.interface';
export default class MetadataRequest {
	paths: string[];
	options: MetadataOptions;

	constructor(data: MetadataRequest) {
		const { paths, options } = data;
		this.paths = paths;
		this.options = options;
	}
}
