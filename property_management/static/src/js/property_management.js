import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";

export class PropertyStatusWidget extends CharField {
    setup() {
        super.setup();
    }
    _renderReadonly() {
        super._renderReadonly();
        if (this.props.value) {
            let statusClass = "";
            switch (this.props.value.toLowerCase()) {
                case "available":
                    statusClass = "text-success";
                    break;
                case "reserved":
                    statusClass = "text-warning";
                    break;
                case "sold":
                    statusClass = "text-danger";
                    break;
            }
            this.el.classList.add(statusClass, "fw-bold");
        }
    }
}
registry.category("fields").add("property_status", PropertyStatusWidget);
