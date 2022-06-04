import { ModuleOptions } from './moduleOptions.interface';

export default interface MetadataOptions extends ModuleOptions {
	exposureTime?: number;
	fNumber?: number;
	focalLength?: number;
	flash: number;
	pixelXDimMin?: number;
	pixelXDimMax?: number;
	pixelYDimMin?: number;
	pixelYDimMax?: number;
}
