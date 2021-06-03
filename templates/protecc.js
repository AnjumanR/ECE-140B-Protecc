function mark_option(checkbox) {
    var boxes = document.getElementsByName('resolution')
    boxes.forEach((item) => {
        if (item !== checkbox) item.checked = false
    })
}
