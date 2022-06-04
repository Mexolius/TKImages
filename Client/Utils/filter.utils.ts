export function filterRange(value?: number | Date | null, filterFrom?: number | Date | null, filterTo?: number | Date | null): boolean{
    if (filterFrom == null && filterTo == null) return true;

    if ( value == null) return false;

    if (filterFrom != null && value < filterFrom) return false;

    if (filterTo != null && value > filterTo) return false;

    return true;
}

export function filterValue(value?: string | number, filterOption?: string | number): boolean{
    if(filterOption == null) return true;
    
    if(value == null) return false;

    console.log(value, +filterOption, "?", value === +filterOption)

    return value === +filterOption;
}
