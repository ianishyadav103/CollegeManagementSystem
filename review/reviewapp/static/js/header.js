icon_arrow_cross = document.getElementById("drop-icon")
page_body = document.getElementsByTagName("body")[0]
let theme = "white";
let show_cross = function () {
    if (theme == "white") {
        icon_arrow_cross.src = "/static/cross_icon.png"
    }
    else {
        icon_arrow_cross.src = "/static/cross_icon_w.png"
    }
}
let show_drop_arrow = function () {
    if (theme == "white") {
        icon_arrow_cross.src = "/static/drop_arrow_icon.png"
    }
    else {
        icon_arrow_cross.src = "/static/drop_arrow_icon_w.png"

    }
}
let show_cross_touch = function () {
    if (theme == "white") {
        icon_arrow_cross.src = "/static/cross_icon.png"
    }
    else {
        icon_arrow_cross.src = "/static/cross_icon_w.png"
    }

    icon_arrow_cross.removeEventListener('touchstart', show_cross_touch)
    icon_arrow_cross.addEventListener('touchstart', show_drop_arrow_touch)
    page_body.addEventListener('touchmove', show_drop_arrow_touch)
}
let show_drop_arrow_touch = function () {
    if (theme == "white") {
        icon_arrow_cross.src = "/static/drop_arrow_icon.png"
    }
    else {
        icon_arrow_cross.src = "/static/drop_arrow_icon_w.png"

    }
    icon_arrow_cross.removeEventListener('touchstart', show_drop_arrow_touch)
    icon_arrow_cross.addEventListener('touchstart', show_cross_touch)
    page_body.removeEventListener('touchmove', show_drop_arrow_touch)
}

icon_arrow_cross.addEventListener('mouseover', show_cross)
icon_arrow_cross.addEventListener('mouseout', show_drop_arrow)
icon_arrow_cross.addEventListener('touchstart', show_cross_touch)

