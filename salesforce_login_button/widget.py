import anywidget
import traitlets
from pathlib import Path

class SalesforceLoginButton(anywidget.AnyWidget):
    # _esm = Path(__file__).parent / 'static/index.js'
    _esm = """
    function render({ model, el }) {
        let button = document.createElement("button");
        button.innerHTML = `count is ${model.get("value")}`
        console.log("hi");
        console.log(model.get("value"));
        button.addEventListener("click", () => {
            model.set("value", model.get("value") + 1);
            model.save_changes();
        })
        model.on("change:value", () => {
            button.innerHTML = `count is ${model.get("value")}`;
        })
        el.appendChild(button);
    }

    export default { render };
    """
    _css = Path(__file__).parent / 'static/index.css'
    value = traitlets.Int(0).tag(sync=True)
