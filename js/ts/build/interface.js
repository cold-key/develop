/**
 * 将时间戳转换为指定格式
 * @param time 时间戳
 * @param options 格式化选项
 */
function parseTimeToSpecialTypeByData(time, options) {
    return parseTimeToSpecialType(time, options.year, options.sp1, options.month, options.sp2, options.date, options.sp3, options.hour, options.sp4, options.minute, options.sp5, options.second);
}
/**
 * 将时间戳转换为指定格式
 */
function parseTimeToSpecialType(time, year, sp1, month, sp2, date, sp3, hour, sp4, minute, sp5, second) {
    const newDate = new Date(time);
    let returnString = '';
    if ((year === null || year === void 0 ? void 0 : year.length) === 4) {
        returnString += newDate.getFullYear() + (sp1 || '');
    }
    if (month) {
        const m = newDate.getMonth() + 1;
        returnString += (month.length === 2 ? this.twoTimeFill(String(m)) : m) + (sp2 || '');
    }
    if (date) {
        const d = newDate.getDate();
        returnString += (date.length === 2 ? this.twoTimeFill(String(d)) : d) + (sp3 || '');
    }
    if (hour) {
        const h = newDate.getHours();
        returnString += (hour.length === 2 ? this.twoTimeFill(String(h)) : h) + (sp4 || '');
    }
    if (minute) {
        const m = newDate.getMinutes();
        returnString += (minute.length === 2 ? this.twoTimeFill(String(m)) : m) + (sp5 || '');
    }
    if (second) {
        const s = newDate.getSeconds();
        returnString += (second.length === 2 ? this.twoTimeFill(String(s)) : s);
    }
    return returnString;
}
// test
console.log(parseTimeToSpecialTypeByData(new Date().getTime(), { year: 'yyyy', sp1: '-', month: 'MM', sp2: '-', date: 'dd', sp3: '-', hour: 'HH', sp4: '-', minute: 'mm', sp5: '-', second: 'ss' }));
