document.addEventListener("DOMContentLoaded", function (event) {
    // All pages
    const div = document.createElement("div");
    div.style.textAlign = "center";
    const p = document.createElement('p');
    const a = document.createElement('a');
    a.text = "Impressum & Datenschutz";
    a.style.color = "#FFFFFF";
    a.href = "https://dpvonline.de/impressum/";
    a.target = "_blank";
    div.append(p)
    div.append(a)
    document.body.appendChild(div);

    // Register page
    const register_form = document.getElementById("kc-register-form");
    if (register_form) {
        function dynamicVerbandBundChange() {
            let attribute_bund = document.getElementById("attributes.bund").value;
            let class_bund = document.getElementById("class.bund").value;
            let verband = document.getElementById("user.attributes.verband").value;
            if (verband === "DPV") {
                let buende = {
                    "BEP": "Bund Europäischer Pfadfinder",
                    "DPH": "Deutscher Pfadfinderbund Hamburg",
                    "DPBM": "Deutscher Pfadfinderbund Mosaik",
                    "FP": "Freie Pfadfinderschaft",
                    "JOMS": "Jomsburg - freier Pfadfinderbund",
                    "PBH": "Pfadfinderbund Horizonte",
                    "PBMV": "Pfadfinderbund Mecklenburg-Vorpommern",
                    "PBN": "Pfadfinder- und Pfadfinderinnenbund Nord",
                    "PBNL": "Pfadfinder- und Pfadfinderinnenbund Nordlicht",
                    "PBW": "Pfadfinderbund Weltenbummler",
                    "PBB": "Pfadfinderbund Boreas",
                    "PSD": "Pfadfinderschaft Süddeutschland"
                };

                let option_list = "<select class=" + class_bund + " id=\"user.attributes.bund\" name=\"user.attributes.bund\" value=" + attribute_bund + ">\n";
                option_list += "<option value=\"\"></option>\n";
                for (let bund of Object.entries(buende)) {
                    if (bund[0] === attribute_bund) {
                        option_list += "<option value=" + bund[0] + " selected>" + bund[1] + "</option>\n";
                    } else {
                        option_list += "<option value=" + bund[0] + ">" + bund[1] + "</option>\n";
                    }
                }
                option_list += "</select>";
                document.getElementById("bund").innerHTML = option_list;
            } else {
                document.getElementById("bund").innerHTML = "<input type=\"text\" id=\"user.attributes.bund\" class=" + class_bund + " name=\"user.attributes.bund\" " +
                    "value=" + attribute_bund + ">";
            }
        }

        dynamicVerbandBundChange();
        document.getElementById("user.attributes.verband").addEventListener("input", dynamicVerbandBundChange);

        let form = document.getElementById("kc-register-form");
        form.addEventListener("submit", function (event) {
            function replaceEmpty(name) {
                let form = document.getElementById("kc-register-form");
                if (form[name].value === "") {
                    form[name].value = "-";
                }
            }

            function validateUsername(name) {
                let form = document.getElementById("kc-register-form");

                function validateUser(string) {
                    const pattern = /^[a-zA-Z0-9]*$/
                    return pattern.test(String(string));
                }

                if (!validateUser(form[name].value)) {
                    let span = document.getElementById("input-error-username");
                    if( !span ){
                        span = document.createElement("span");
                        span.setAttribute("id", "input-error-username");
                        span.setAttribute("class", "pf-c-form__helper-text pf-m-error required kc-feedback-text");
                    }

                    span.textContent = "Darf keine Mail Adresse sein und keine Sonder- oder Leerzeichen enthalten.";
                    form[name].parentNode.insertBefore(span, form[name].nextSibling);

                    event.preventDefault();
                }
            }

            replaceEmpty("firstName")
            replaceEmpty("lastName")
            validateUsername("username")
        });
    }
});



