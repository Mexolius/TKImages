import { getImageExif } from '../Utils/metadata.utils';
import { filterRange, filterValue, } from '../Utils/filter.utils';
import MetadataOptions from './metadataOptions.interface';
import { asyncFilter } from '../Utils/async.utils';
import MetadataRequest from './metadataRequest';

const exifFileTypes = ['jpg', 'tiff'];

export default async function handleRequest(payload: MetadataRequest): Promise<string[]> {
	const request = payload;
	const result = await asyncFilter(request.paths, (path) => filterMetadata(path, request.options));
	return result;
}

export async function filterMetadata(path: string, options: MetadataOptions): Promise<boolean> {
	// Valid format guard
	const fileType = path.split('.').slice(-1)[0];
	if (!exifFileTypes.includes(fileType)) {
		return false;
	}

	const imgData: any = await getImageExif(path);
	
	// Here we add filters as guards
	if (!filterValue(imgData.exif.ExposureTime, options.exposureTime)) return false;
	
	if (!filterValue(imgData.exif.FNumber, options.fNumber)) return false;
	
	if (!filterValue(imgData.exif.FocalLength, options.focalLength)) return false;

	if (!filterValue(imgData.exif.Flash, options.flash)) return false;

	if (!filterRange([imgData.exif.ExifImageWidth].flat()[0], options.pixelXDimMin, options.pixelXDimMax)) return false;

	if (!filterRange([imgData.exif.ExifImageHeight].flat()[0], options.pixelYDimMin, options.pixelYDimMax)) return false;
	
	return true;
}
