export const asyncFilter = async (arr: any[], predicate: (a: any) => Promise<boolean>) => {
	const results = await Promise.all(arr.map(predicate));

	return arr.filter((_v, index) => results[index]);
};
