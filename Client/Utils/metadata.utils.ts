const ExifImage = require('exif').ExifImage;

export function parseExifDate(exifDate: string): Date {
	let [stringDate, stringTime] = exifDate.split(' ');

	stringDate = stringDate.split(':').join('-');

	stringDate = [stringDate, stringTime].join('T');

	return new Date(stringDate);
}

export const getImageExif = (imgPath: string) =>
	new Promise((resolve, reject) => {
		new ExifImage({ image: imgPath }, (err: any, exifData: any) => {
			if (err) return resolve({ exif: {} });

			resolve(exifData);
		});
	});
