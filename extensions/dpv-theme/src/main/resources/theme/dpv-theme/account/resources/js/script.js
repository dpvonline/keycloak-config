document.addEventListener("DOMContentLoaded", function(event) {
    var div = document.createElement("div");
    div.style.textAlign = "center";
    var p = document.createElement('p');
    var a = document.createElement('a');
    a.text = "Impressum & Datenschutz";
    a.style.color= "#FFFFFF";
    a.href = "https://dpvonline.de/impressum/";
    a.target ="_blank";
    div.append(p)
    div.append(a)
    document.body.appendChild(div);
});

