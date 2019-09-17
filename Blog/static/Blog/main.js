function Copy(text) {
    console.log('inside copy function');
    console.log(text, 'fgdf');
    $('.copy').select();
    document.execCommand("copy");
}