var vendor_options = {valueNames: ['district', 'vendor', 'contact', 'address', 'mobile', 'category', 'desc','origin', 'order_type', 'available_date', 'record_date', 'tags']};
var vendorList = new List('vendor', vendor_options);

var resident_options = {valueNames: ['published_date', 'district', 'address']};
var residentList = new List('resident', resident_options);

var summary_options = {valueNames: ['published_date', 'district', 'diagnosed','asymptomatic']};
var summaryList = new List('summary', summary_options);

function s2ab(s) {
    var buf = new ArrayBuffer(s.length);
    var view = new Uint8Array(buf);
    for (var i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
    return buf;
}
function export_excel(id, name) {
    var wb = XLSX.utils.table_to_book(document.getElementById(id), {sheet:"Sheet JS"});
    var wbout = XLSX.write(wb, {bookType:'xlsx', bookSST:true, type: 'binary'});
    saveAs(new Blob([s2ab(wbout)],{type:"application/octet-stream"}), 'shanghai_2022_living_' + name + '.xlsx');
}
